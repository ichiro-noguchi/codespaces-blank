# ビルドステージ
FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# 実行ステージ
FROM nginx:stable as runner

WORKDIR /usr/share/nginx/html

# ビルド成果物をコピー
COPY --from=builder /app/dist .

# カスタムnginx.confをコピー
COPY nginx.conf /etc/nginx/nginx.conf

# configファイル（chat_client.json）はdocker-composeでVolumeマウント

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
