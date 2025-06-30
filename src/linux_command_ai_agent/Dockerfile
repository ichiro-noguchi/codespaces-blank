FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH="/app:/app/common"
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5004"]
