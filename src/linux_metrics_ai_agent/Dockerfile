FROM python:3.11-slim
WORKDIR /app

# requirements.txtだけを先にコピーして依存関係をインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# その他のソースコードをコピー
COPY . /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--app-dir", "/app"]
