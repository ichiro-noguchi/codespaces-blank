# テスト README

このディレクトリは本プロジェクトのテストコードを管理します。

## テストの観点
- AgentRegistryService の API（/agents）登録・取得・tasks情報の整合性
- SuperAgentServer からの Registry 連携・tasks取得
- 各AIAgent（LinuxMetricsAIAgent, LinuxCommandAIAgent）の tasks 情報の正当性
- Docker運用時の永続化・再起動後のデータ保持
- .env 設定値による動作切り替え

## テスト計画（例）
1. AgentRegistryService の /agents GET/POST の正常系・異常系
2. tasks 情報の登録・取得・内容検証
3. SuperAgentServer からの Registry 情報取得の疎通
4. AIAgent の tasks API の返却値検証
5. Docker再起動時のデータ永続性確認
6. .env 設定変更時の動作確認

---

テストケースや観点は今後随時追加・更新します。
