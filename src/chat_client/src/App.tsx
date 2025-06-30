import React, { useState } from 'react';
import './App.css';

const SUPER_AGENT_API = import.meta.env.VITE_SUPER_AGENT_API || '/api';

function App() {
  const [messages, setMessages] = useState([
    { from: 'ai', text: 'こんにちは！ご用件をどうぞ。' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // サイドメニューの仮データ
  const menuItems = [
    'チャット',
    '履歴',
    '設定',
  ];

  // サブ画面の仮表示フラグ
  const [showSub, setShowSub] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { from: 'user', text: input }]);
    setLoading(true);
    setInput('');
    try {
      const res = await fetch(`${SUPER_AGENT_API}/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: input })
      });
      const data = await res.json();
      let aiText = '';
      if (data.help) {
        aiText = '[機能一覧]\n' + data.help.map((a: any) => `・${a.name}: ${a.description}\n  機能: ${a.capabilities.join(', ')}`).join('\n');
      } else if (data.missing_parameters) {
        aiText = `追加情報が必要です: ${data.missing_parameters.join(', ')}`;
      } else if (data.consent_required) {
        aiText = 'この操作にはユーザの同意が必要です。実行してよいですか？';
      } else if (data.result) {
        aiText = typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2);
      } else if (data.error) {
        aiText = 'エラー: ' + data.error;
      } else {
        aiText = JSON.stringify(data);
      }
      setMessages(msgs => [...msgs, { from: 'ai', text: aiText }]);
    } catch (e) {
      setMessages(msgs => [...msgs, { from: 'ai', text: 'API通信エラー' }]);
    }
    setLoading(false);
  };

  return (
    <div className="layout-root">
      <aside className="side-menu">
        <h3>メニュー</h3>
        <ul>
          {menuItems.map(item => (
            <li key={item} onClick={() => item === '設定' && setShowSub(s => !s)}>{item}</li>
          ))}
        </ul>
      </aside>
      <main className="main-area">
        <div className="chat-container">
          <h2>ChatClient パイロット版</h2>
          <div className="chat-box">
            {messages.map((msg, i) => (
              <div key={i} className={msg.from === 'user' ? 'msg-user' : 'msg-ai'}>
                <b>{msg.from === 'user' ? 'あなた' : 'AI'}:</b> {msg.text}
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
