import React, { useState } from 'react';
import './App.css';

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
    // ダミー応答: 実際はAIAgent APIへfetchする
    setTimeout(() => {
      setMessages(msgs => [...msgs, { from: 'ai', text: '（ダミー応答）: ' + msgs[msgs.length-1].text }]);
      setLoading(false);
    }, 800);
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
      </main>
      {showSub && (
        <aside className="sub-panel">
          <h3>サブ画面（例：設定）</h3>
          <p>ここにサブ画面の内容を表示できます。</p>
        </aside>
      )}
    </div>
  );
}

export default App;
