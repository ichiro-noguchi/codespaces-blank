#!/bin/sh
# E2EテストをNode.js Playwright公式テストランナーで実行するスクリプト（完全自己完結）
# イメージ: codespaces-blank/e2etest:latest

set -e

HOSTNAME=$(uname -n)
CHATCLIENT_URL_DEFAULT="http://$HOSTNAME:3000"

echo "[E2E] Node.js Playwrightテストを実行します..."
docker run --rm \
  -e CHATCLIENT_URL="${CHATCLIENT_URL:-$CHATCLIENT_URL_DEFAULT}" \
  codespaces-blank/e2etest:latest
