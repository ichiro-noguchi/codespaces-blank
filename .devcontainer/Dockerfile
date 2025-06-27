# ベースイメージ
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# デフォルトのシェルを bash に設定
SHELL ["/bin/bash", "-c"]

# Python のアップグレード（必要に応じて）
RUN pip3 install --upgrade pip

# 作業ディレクトリ
WORKDIR /workspaces/codespaces-blank
