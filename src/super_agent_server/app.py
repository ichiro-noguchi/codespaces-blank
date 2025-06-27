# SuperAgentServer のエントリポイント（仮実装）
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'SuperAgentServer is running.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
