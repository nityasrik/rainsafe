FROM node:20-alpine

WORKDIR /app

# Minimal placeholder package.json to allow container to start
COPY package.json package-lock.json* ./

RUN npm ci || npm install --no-audit --no-fund

# Default command keeps container alive for devcontainer usage
CMD ["sh", "-c", "npm run dev || tail -f /dev/null"]


