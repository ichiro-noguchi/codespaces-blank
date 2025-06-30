import { useState, useEffect, useRef } from 'react';
import './App.css';
import ReactMarkdown from 'react-markdown'; // react-markdownをインポート

interface Message {
  from: string;
  text: string;
}

// README.md に基づく SuperAgentServer の入出力型
interface CommandIn {
  command: string;
  arguments?: string[];
}

interface CommandOut {
  command: string;
  status: string; // "SUCCESS", "ERROR"
  errorMessage?: string;
  result?: any; // コマンドに応じた型
}

interface RequestIn {
  user_input: string;
}

interface RequestOut {
  status: string; // 予約 (README.mdより)
  result?: any; // 実行内容に応じた型
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { from: 'ai', text: 'こんにちは！ご用件をどうぞ。' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiUrl, setApiUrl] = useState<string | null>(null);
  const configLoaded = useRef(false);

  useEffect(() => {
    if (configLoaded.current) return;
    fetch('/chat_client.json')
      .then(res => res.json())
      .then(cfg => {
        setApiUrl(cfg.SUPER_AGENT_API);
        configLoaded.current = true;
      })
      .catch(() => setApiUrl(null));
  }, []);

  // サイドメニューの仮データ
  const menuItems = [
    'チャット',
    '履歴',
    '設定',
  ];

  // サブ画面の仮表示フラグ
  const [showSub, setShowSub] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || !apiUrl) return;
    const userMessage = { from: 'user', text: input };
    setMessages([...messages, userMessage]);
    setLoading(true);
    const currentInput = input; // 入力値をクリアする前に保持
    setInput('');

    try {
      let res;
      let data;
      let aiText = '';

      if (currentInput.startsWith('/')) {
        // システムコマンドの場合: /command エンドポイントへ送信
        const parts = currentInput.slice(1).split(' ');
        const command = parts[0];
        const commandArgs = parts.slice(1); // arguments を commandArgs に変更
        const commandIn: CommandIn = { command, arguments: commandArgs }; // ここも修正

        res = await fetch(`${apiUrl}/command`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(commandIn)
        });
        data = await res.json() as CommandOut; // CommandOutとしてキャスト

        // CommandOutの応答を処理
        if (data.status === 'SUCCESS') {
          // resultの内容をMarkdownで整形して表示
          if (data.command === 'help' && data.result && data.result.agents) {
             // /helpコマンドの出力をMarkdownリストで整形
             aiText = '**利用可能なAIAgent**\n' + data.result.agents.map((a: any) => `- **${a.name}**: ${a.description}\n    - 機能: ${a.capabilities.map((cap: string) => `\n      - ${cap}`).join('')}`).join('\n');
          } else if (data.result !== undefined) {
             // その他のコマンド結果はJSONコードブロックまたは文字列として表示
             aiText = typeof data.result === 'string' ? data.result : '```json\n' + JSON.stringify(data.result, null, 2) + '\n```';
          } else {
             aiText = `コマンド実行成功: ${data.command}`;
          }
        } else {
          aiText = `コマンド実行エラー (${data.command}): ${data.errorMessage || '不明なエラー'}`;
        }

      } else {
        // 通常の要求の場合: /request エンドポイントへ送信
        const requestIn: RequestIn = { user_input: currentInput };

        res = await fetch(`${apiUrl}/request`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestIn)
        });
        data = await res.json() as RequestOut; // RequestOutとしてキャスト

        // RequestOutの応答を処理
        if (data.status === 'SUCCESS') {
           // resultの内容をMarkdownで整形して表示
           if (typeof data.result === 'string') {
             aiText = data.result;
           } else if (Array.isArray(data.result)) {
             // 配列の場合はMarkdownリスト形式で表示
             aiText = '**結果リスト**\n\n' + data.result.map((item: any) => `- ${typeof item === 'object' ? '```json\n' + JSON.stringify(item, null, 2) + '\n```' : item}`).join('\n');
           } else if (typeof data.result === 'object' && data.result !== null) {
             // オブジェクトの場合はMarkdownリスト形式でキーと値を列挙
             aiText = '**結果詳細**\n\n' + Object.entries(data.result).map(([key, value]) => `- **${key}**: ${typeof value === 'object' ? '```json\n' + JSON.stringify(value, null, 2) + '\n```' : value}`).join('\n');
           } else {
             // その他の型の場合はMarkdownコードブロックでJSON文字列化
             aiText = '```json\n' + JSON.stringify(data.result, null, 2) + '\n```';
           }
        } else if (data.status === 'MISSING_PARAMS') {
           aiText = `追加情報が必要です: ${JSON.stringify(data.result, null, 2)}`;
        } else if (data.status === 'CONSENT_REQUIRED') {
           aiText = 'この操作にはユーザの同意が必要です。実行してよいですか？'; // または result に同意確認用の情報が含まれるか？
        } else {
           // その他のstatus (例: ERROR)
           aiText = `要求処理エラー (${data.status}): ${JSON.stringify(data.result, null, 2)}`;
        }
      }

      // レスポンスメッセージを追加
      setMessages((msgs: Message[]) => [...msgs, { from: 'ai', text: aiText }]);

    } catch (e) {
      console.error('API通信エラー:', e);
      setMessages((msgs: Message[]) => [...msgs, { from: 'ai', text: 'API通信エラーが発生しました。' }]);
    }
    setLoading(false);
  };

  return (
    <div className="layout-root">
      <aside className="side-menu">
        <h3>メニュー</h3>
        <ul>
          {menuItems.map(item => (
            <li key={item} onClick={() => item === '設定' && setShowSub((s: boolean) => !s)}>{item}</li>
          ))}
        </ul>
      </aside>
      <main className="main-area">
        <div className="chat-container">
          <h2>ChatClient パイロット版</h2>
          <div className="chat-box">
            {messages.map((msg: Message, i: number) => ( /* msg と i に型アノテーションを追加 */
              <div key={i} className={msg.from === 'user' ? 'msg-user' : 'msg-ai'}>
                <b>{msg.from === 'user' ? 'あなた' : 'AI'}:</b>
                {/* Markdownをレンダリング */}
                <ReactMarkdown className="markdown">{msg.text}</ReactMarkdown>
              </div>
            ))}
            {loading && <div className="msg-ai">AI: ...応答中</div>}
          </div>
          <div className="chat-input">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="メッセージを入力..."
            />
            <button onClick={sendMessage} disabled={loading}>送信</button>
          </div>
        </div>
        {showSub && <div className="sub-screen">サブ画面（設定など）</div>}
      </main>
    </div>
  );
}

export default App;
