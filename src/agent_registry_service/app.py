# AgentRegistryService のエントリポイント（AIAgentの登録・管理API）
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import json
import os
import uuid
from typing import Dict

app = FastAPI()

REGISTRY_FILE = '/work/agents.json'

def load_agents() -> Dict[str, dict]:
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_agents(agents: Dict[str, dict]):
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)

agents = load_agents()

@app.get("/agents")
def list_agents():
    """AIAgentの一覧を返すAPI"""
    return list(agents.values())

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    """AIAgentの詳細を返すAPI"""
    agent = agents.get(agent_id)
    if agent:
        return agent
    raise HTTPException(status_code=404, detail="not found")

@app.post("/agents")
async def register_agent(request: Request):
    """AIAgentの登録API (artifactIDで登録・更新)"""
    data = await request.json()
    artifact_id = data.get('artifactID')
    # 必須項目チェックのみ行い、データ構造ごと保存
    if not artifact_id or not data.get('name') or not data.get('description') or not isinstance(data.get('capabilities'), list) or not data.get('endpoint'):
        return JSONResponse(status_code=400, content={'error': 'artifactID, name, description, capabilities(list), endpoint are required'})
    if 'tasks' not in data or not isinstance(data['tasks'], list):
        data['tasks'] = []
    agents[artifact_id] = data
    save_agents(agents)
    return {'result': 'ok', 'artifactID': artifact_id}

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    """AIAgentの削除API"""
    # artifactIDで削除できるようにキー名を変更
    if agent_id in agents:
        del agents[agent_id]
        save_agents(agents)
        return {'result': 'deleted'}
    raise HTTPException(status_code=404, detail="not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002, reload=True)
