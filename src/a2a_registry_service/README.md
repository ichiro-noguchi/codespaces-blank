# A2ARegistryService

AIAgentの登録・管理を行うサービスです。

## 提供API
- `GET    /agents`         : AIAgentの一覧取得
- `GET    /agents/<id>`    : AIAgentの詳細取得
- `POST   /agents`         : AIAgentの登録（JSONでid等を送信）
- `DELETE /agents/<id>`    : AIAgentの削除

## 起動方法
```
python app.py
```

## 今後の拡張案
- ストレージをDB化
- 認証・認可
- サービス監視・ヘルスチェック

# このディレクトリは agent_registry_service へ移行されました
今後は src/agent_registry_service/ をご利用ください。
