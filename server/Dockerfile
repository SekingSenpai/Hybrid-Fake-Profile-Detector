# ---------- Express Gateway ----------
FROM node:20-alpine

WORKDIR /app

# Install deps (cached layer)
COPY package.json package-lock.json* ./
RUN npm install --omit=dev

# Copy application code
COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
