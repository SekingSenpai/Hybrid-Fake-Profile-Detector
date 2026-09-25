"""Fine-tune DistilBERT on the supplied fake and legitimate text corpora."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def read_text_file(path: Path, label: int, limit: int, seed: int) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for fields in reader:
            if fields:
                text = fields[-1].strip()
                if text:
                    rows.append((text, label))
    random.Random(seed).shuffle(rows)
    return rows[:limit]


class TextDataset(Dataset):
    def __init__(self, rows: list[tuple[str, int]], tokenizer, max_length: int) -> None:
        self.encodings = tokenizer(
            [text for text, _ in rows],
            truncation=True,
            padding=True,
            max_length=max_length,
        )
        self.labels = [label for _, label in rows]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        item = {key: torch.tensor(value[index]) for key, value in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)
        return item


def fine_tune(
    fake_path: Path,
    legitimate_path: Path,
    output_dir: Path,
    model_name: str,
    max_samples_per_class: int,
    epochs: int,
    batch_size: int,
    max_length: int,
) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    fake = read_text_file(fake_path, 1, max_samples_per_class, 42)
    legitimate = read_text_file(legitimate_path, 0, max_samples_per_class, 42)
    rows = fake + legitimate
    random.Random(42).shuffle(rows)
    split = int(len(rows) * 0.9)
    train_rows, validation_rows = rows[:split], rows[split:]

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=2, id2label={0: "GENUINE", 1: "FAKE"}, label2id={"GENUINE": 0, "FAKE": 1}
    ).to(device)
    train_loader = DataLoader(
        TextDataset(train_rows, tokenizer, max_length),
        batch_size=batch_size,
        shuffle=True,
        pin_memory=device.type == "cuda",
    )
    validation_loader = DataLoader(
        TextDataset(validation_rows, tokenizer, max_length),
        batch_size=batch_size,
        pin_memory=device.type == "cuda",
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            batch = {key: value.to(device) for key, value in batch.items()}
            optimizer.zero_grad(set_to_none=True)
            loss = model(**batch).loss
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for batch in validation_loader:
                labels = batch.pop("labels").to(device)
                outputs = model(
                    **{key: value.to(device) for key, value in batch.items()}
                )
                correct += (outputs.logits.argmax(dim=-1) == labels).sum().item()
                total += labels.size(0)
        print(
            f"Epoch {epoch + 1}/{epochs} | loss={train_loss / max(1, len(train_loader)):.4f}"
            f" | validation_accuracy={correct / max(1, total):.4f} | device={device}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer.save_pretrained(output_dir)
    model.save_pretrained(output_dir)
    print(f"Saved fine-tuned DistilBERT to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parent
    data = root / "model_traning"
    parser.add_argument("--fake", type=Path, default=data / "fake_account.csv")
    parser.add_argument("--legitimate", type=Path, default=data / "legitimate_account.csv")
    parser.add_argument("--output", type=Path, default=root / "models" / "distilbert-finetuned")
    parser.add_argument("--model-name", default="distilbert-base-uncased")
    parser.add_argument("--max-samples-per-class", type=int, default=20000)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=256)
    args = parser.parse_args()
    fine_tune(
        args.fake,
        args.legitimate,
        args.output,
        args.model_name,
        args.max_samples_per_class,
        args.epochs,
        args.batch_size,
        args.max_length,
    )
