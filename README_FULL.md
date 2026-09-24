# Full Documentation

The complete setup and usage instructions are maintained in the main
[README.md](README.md), including separate Windows PowerShell and macOS
Terminal instructions.

For a quick reference, start the services in three terminals:

1. AI Engine: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
2. Server: `npm start`
3. Client: `npm run dev`

Then open `http://localhost:5173`.
