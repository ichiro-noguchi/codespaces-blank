#!/bin/sh
# E2Eテスト用のDockerイメージをビルドするスクリプト（Node.js Playwright専用・完全自己完結）
# イメージ名: codespaces-blank/e2etest:latest

docker build -t codespaces-blank/e2etest:latest -f- . <<'EOF'
FROM node:20-slim

# Playwright公式推奨の依存パッケージ
RUN apt-get update && \
    apt-get install -y wget gnupg ca-certificates curl \
      libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm-dev libxshmfence1 libxcomposite1 libxrandr2 libu2f-udev libdrm2 libxdamage1 libxfixes3 libxext6 libx11-xcb1 fonts-liberation libappindicator3-1 xdg-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /e2e
COPY playwright.config.ts ./
COPY tests ./tests

RUN npm init -y && npm install --save-dev @playwright/test && npx playwright install chromium

CMD ["npx", "playwright", "test"]
EOF
