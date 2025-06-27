FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
# ここに必要な依存パッケージを追記
CMD ["python3", "-m", "http.server", "5001"]
# このディレクトリはSuperAgentServerへ移行されました
