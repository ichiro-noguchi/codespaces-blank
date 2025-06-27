# プロジェクト名

（ここにシステム名を記入）

## 概要
AIエージェントを使ったChatシステムの開発を行うプロジェクトです。
### 構成
- クライアント：ChatClient と呼びます
- サーバ
    - AIAgent
    - A2ARegistryService
    - LinuxMetricsA2AService
    - LinuxCommandA2AService

## 機能一覧
- [x] ChatClient
    - [x] デスクトップ向け3ペインレイアウト（左サイドメニュー・中央チャット・右サブ画面）
    - [x] 画面全体を広く使うレスポンシブデザイン
    - [x] メッセージ送信・ダミー応答のチャットUI
    - [x] サイドメニュー・サブ画面の仮実装
    - [ ] AIAgent API連携（今後実装）
- [ ] サーバ
    - [ ] AIAgent
        - [ ] ユーザの指示を受け付けます
        - [ ] 生成AIモデルを使い、ユーザの要求に答えるための実行計画を立てます
        - [ ] 実行計画に従って、生成AIモデルやツールあるいは、AIAgentの関数を呼び出します
        - [ ] 実行計画に従って処をを実行した結果、ユーザの要求に答えられたかどうか判断します。
            - [ ] 答えられた場合、ユーザに結果を返します
            - [ ] 答えられなかった場合、ユーザにその旨を伝えます
    - [ ] A2ARegistryService
        - [ ] A2AServiceの登録・を行います
        - [ ] A2AServiceの一覧と詳細を取得するAPIを提供します
    - [ ] LinuxMetricsA2AService
        - [ ] Linuxのメトリクスを取得するツールを提供します
    - [ ] LinuxCommandA2AService
        - [ ] Linuxのコマンドを実行するツールを提供します


- [ ] 機能3: （例：データ表示）

## 機能詳細
### ChatClient
- React + TypeScript + Vite で実装
- デスクトップ向け3ペインレイアウト（左サイドメニュー・中央チャット・右サブ画面）
- 画面全体を広く使うレスポンシブデザイン
- メッセージ送信・ダミー応答のチャットUI
- サイドメニュー・サブ画面の仮実装
- AIAgent API連携は今後実装予定

### AIAgent
### A2ARegistryService
- AIAgentの登録・管理を行うサーバ
- AIAgentの一覧と詳細を取得するAPIを提供
- Flask + FastAPI + langchain + langgraph で実装
- API は
    - 一覧と詳細の取得は  AIAgentが使用することを想定しています
    - 登録・更新・削除は、A２AServiceが使用することを想定しています
- 登録されたAIAgentの情報を保持し、AIAgentが自身の情報を登録するためのエンドポイントを提供
- 登録データはJSONファイルとしてローカルファイルで保存し、JSON の中身は A2ARegistryInfo
- A2ARegistryInfo は以下の情報を持ちます
    - A2AServiceのID(ID はA2ARegistryInfoの一意な識別子として  A2ARegistryServiceが登録時に生成)
    - A2AServiceの名前
    - A2AServiceの説明
    - AIAgentが提供する機能のリスト
        - 各機能を呼び出すためのエンドポイントURLとパラメータと応答の型情報






### A2AService
- これは  A2Aを実装したサービスのベースクラスです。
- 以下の機能を持ちます
    - A2Aとしての基本的なインターフェースを定義
    - A2ARegistryService へ登録するためのメソッドを提供
    - 起動時に A2ARegistryService へ自身の情報を登録します
    - A2Aの実装を提供するための抽象メソッドを定義

### LinuxMetricsA2AService
- A2AServiceの具体的な実装です
- Linuxのメトリクスを取得するためのA2A サービスです

### LinuxCommandA2AService
- A2AServiceの具体的な実装です
- Linuxのコマンドを実行するためのA2A サービスです


## セットアップ手順
1. リポジトリをクローン
2. devcontainer で開く
3. 必要なコマンドを実行

## 使用技術
### ChatClient
- 言語: TypeScript
- フレームワーク: React, Vite
- その他: Docker, VS Code Devcontainer
### AIAgent
- 言語: Python
- フレームワーク: Flask, FastWGI , langchain, langgraph
- その他: Devcontainer 
### A2ARegistryService
- 言語: Python
- フレームワーク: Flask, FastWGI , langchain, langgraph
- その他: Devcontainer 
### A2AService / LinuxMetricsA2AService / LinuxCommandA2AService
- 言語: Python
- フレームワーク: Flask, FastWGI , langchain, langgraph
- その他: Devcontainer 

## ディレクトリ構成
```
<project-root>
    docker-compose.yml
    src/
        ├── chat_client/          # ChatClientのコード
        ├── ai_agent/             # AIAgentのコード
        ├── a2a_registry_service/ # A2ARegistryServiceのコード
        ├── linux_metrics_a2a_service/ # LinuxMetricsA2AServiceのコード
        └── linux_command_a2a_service/ # LinuxCommandA2AServiceのコード
        └── common/              # 共通のコード
```

## 今後のTODO
- [ ] README.md を更新
- [ ] 必要なファイル・ディレクトリを追加
- [ ] コード実装
