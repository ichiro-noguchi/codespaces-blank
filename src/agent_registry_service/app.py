# AgentRegistryService のエントリポイント（AIAgentの登録・管理API）
from flask import Flask, request, jsonify
import json
import os
import uuid

app = Flask(__name__)

REGISTRY_FILE = 'agents.json'

def load_agents():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_agents(agents):
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)

agents = load_agents()

@app.route('/agents', methods=['GET'])
def list_agents():
    """AIAgentの一覧を返すAPI"""
    return jsonify(list(agents.values()))

@app.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """AIAgentの詳細を返すAPI"""
    agent = agents.get(agent_id)
    if agent:
        return jsonify(agent)
    return jsonify({'error': 'not found'}), 404

@app.route('/agents', methods=['POST'])
def register_agent():
    """AIAgentの登録API"""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    functions = data.get('functions')
    if not name or not description or not isinstance(functions, list):
        return jsonify({'error': 'name, description, functions(list) are required'}), 400
    agent_id = str(uuid.uuid4())
    registry_info = {
        'id': agent_id,
        'name': name,
        'description': description,
        'functions': functions
    }
    agents[agent_id] = registry_info
    save_agents(agents)
    return jsonify({'result': 'ok', 'id': agent_id})

@app.route('/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """AIAgentの削除API"""
    if agent_id in agents:
        del agents[agent_id]
        save_agents(agents)
        return jsonify({'result': 'deleted'})
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
