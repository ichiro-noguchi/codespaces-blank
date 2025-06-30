# プロジェクト名

（ここにシステム名を記入）

## 概要
AIエージェントを使ったChatシステムの開発を行うプロジェクトです。
### 構成
- クライアント：ChatClient と呼びます
- サーバ
    - SuperAgentServer
    - AgentRegistryService
    - LinuxMetricsAIAgent
    - LinuxCommandAIAgent

## 機能一覧
- [x] ChatClient
    - [x] デスクトップ向け3ペインレイアウト（左サイドメニュー・中央チャット・右サブ画面）
    - [x] 画面全体を広く使うレスポンシブデザイン
    - [x] メッセージ送信・ダミー応答のチャットUI
    - [x] サイドメニュー・サブ画面の仮実装
    - [ ] SuperAgentServer API連携（今後実装）
- [ ] サーバ
    - [x] SuperAgentServer（Gemini LLM連携API, FastAPI, .env対応）
        - [x] Gemini LLM API連携
        - [x] .envによるAPIキー・モデル一元管理
        - [x] RESTサーバ起動
        - [ ] AgentRegistry/AIAgent連携
        - [ ] 実行計画・同意確認・ChatClient連携
    - [x] AgentRegistryService（FastAPI, .env対応）
        - [x] AIAgentの登録・一覧・詳細・削除API
        - [x] JSON永続化
        - [x] endpoint/capabilities/同意要否情報の管理
    - [x] LinuxMetricsAIAgent
        - [x] /tasks, /run API
        - [x] get_tasksでrequires_consent情報付与
    - [x] LinuxCommandAIAgent
        - [x] /tasks, /run API
        - [x] Gemini LLMによるコマンド提案
        - [x] get_tasksでrequires_consent情報付与
        - [ ] コマンド実行の安全対策

- [ ] 機能3: （例：データ表示）

## 機能詳細
### ChatClient
- React + TypeScript + Vite で実装
- デスクトップ向け3ペインレイアウト（左サイドメニュー・中央チャット・右サブ画面）
- 画面全体を広く使うレスポンシブデザイン
- メッセージ送信・ダミー応答のチャットUI
- サイドメニュー・サブ画面の仮実装
- SuperAgentServer API連携は今後実装予定

### SuperAgentServer
#### 実装の前提
- Gemini LLM API連携（/llmエンドポイント）
- .envによるAPIキー・モデル一元管理
- RESTサーバ起動（FastAPI）
#### ユーザ要求の処理
- どんな機能があるのかを聞かれたら、AgentRegistryServiceからAIAgent情報を取得して、了解性の高いフォーマットでユーザに示す
- AgentRegistryServiceからAIAgent情報を取得し、ユーザの要求に応じるための実行計画を立てる
- 実行計画に従い、AIAgentやLLM、ツールを組み合わせて処理を実行
    - 各AIAgentの/tasks, /run APIを呼び出し、ーザ要求に応じた実行計画を立案
    - requires_consent=trueのタスクはChatClient経由でユーザ同意を取得
- 今後：ChatClientとのAPI連携、実行計画の自動生成・管理、同意フローのUI連携
#### 結果の表示
- 結果をChatClientに返却

### AgentRegistryService
- SuperAgentServerの登録・管理を行うサーバ
- SuperAgentServerの一覧と詳細を取得するAPIを提供
- Flask + FastAPI + langchain + langgraph で実装
- API は
    - 一覧と詳細の取得は  SuperAgentServerが使用することを想定しています
    - 登録・更新・削除は、AIAgentが使用することを想定しています
- 登録されたSuperAgentServerの情報を保持し、SuperAgentServerが自身の情報を登録するためのエンドポイントを提供
- 登録データはJSONファイルとしてローカルファイルで保存し、JSON の中身は AgentRegistryInfo
- AgentRegistryInfo は以下の情報を持ちます
    - id: エージェントの一意なID（AgentRegistryServiceが登録時に生成）
    - name: エージェント名
    - description: エージェントの説明
    - capabilities: 機能・役割（例: ["get_cpu_metrics", "get_memory_metrics", ...]）
    - endpoint: エージェントのAPIエンドポイントURL
    - status: 稼働状態（例: "active", "inactive" など）

### AIAgent
- これはAIAgentを実装したサービスのベースクラスです。
- 以下の機能を持ちます
    - AIAgentとしての基本的なインターフェースを定義
    - AgentRegistryService へ登録するためのメソッドを提供
    - 起動時に AgentRegistryService へ自身の情報を登録します
    - AIAgentの実装を提供するための抽象メソッドを定義
    - **/tasks エンドポイント（GET）を必須で実装し、自身が対応可能なタスク（Task Definitionのリスト）を返すAPIを提供**
        - 例: GET /tasks → [{"type": "get_cpu_metrics", "parameters": {...}, ...}, ...]


### LinuxMetricsAIAgent
- AIAgentの具体的な実装です
- Linuxのメトリクスを取得するためのAIAgent サービスです
- 以下の機能をA2A のタスクとして提供します
    - メトリック種別一覧取得（同意不要）
    - CPU Metrics（同意不要）
    - Memory Metrics（同意不要）
    - Disk Metrics（同意不要）
    - ※各タスク定義には `requires_consent`（ユーザ同意要否: true/false）を含める

### LinuxCommandAIAgent
- AIAgentの具体的な実装です
- Linuxのコマンドを実行するためのAIAgent サービスです
- 以下の機能をA2A のタスクとして提供します
    - ユーザの指示に応じたコマンドラインの提案（同意不要）
    - 指定したコマンドラインの実行（同意必須: requires_consent=true）
    - ※各タスク定義には `requires_consent`（ユーザ同意要否: true/false）を含める


## セットアップ手順
1. リポジトリをクローン
2. devcontainer で開く
3. 必要なコマンドを実行

## 使用技術
### ChatClient
- 言語: TypeScript
- フレームワーク: React, Vite
- その他: Docker, VS Code Devcontainer
### SuperAgentServer
- 言語: Python
- フレームワーク: Flask, FastWGI , langchain, langgraph
- その他: Devcontainer 
### AgentRegistryService
- 言語: Python
- フレームワーク: Flask, FastWGI , langchain, langgraph
- その他: Devcontainer 
### AIAgent / LinuxMetricsAIAgent / LinuxCommandAIAgent
- 言語: Python
- フレームワーク: Flask, FastWGI , langchain, langgraph
- その他: Devcontainer 

## ディレクトリ構成
```
<project-root>
    docker-compose.yml
    src/
        ├── chat_client/          # ChatClientのコード
        ├── super_agent_server/   # SuperAgentServerのコード
        ├── agent_registry_service/ # AgentRegistryServiceのコード
        ├── linux_metrics_ai_agent/ # LinuxMetricsAIAgentのコード
        └── linux_command_ai_agent/ # LinuxCommandAIAgentのコード
        └── common/              # 共通のコード
```

## 今後のTODO
- [ ] README.md を更新
- [ ] 必要なファイル・ディレクトリを追加
- [ ] コード実装