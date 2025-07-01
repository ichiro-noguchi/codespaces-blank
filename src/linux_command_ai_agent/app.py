from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from ai_agent import LinuxCommandAIAgent
import os
import requests

app = FastAPI()

# エージェントのエンドポイントURL（本番では環境変数や設定ファイルで指定）
ENDPOINT = os.environ.get("AGENT_ENDPOINT", "http://localhost:5003")
REGISTRY_URL = os.environ.get("AGENT_REGISTRY_URL", "http://agent_registry_service:5002/agents")
agent = LinuxCommandAIAgent(endpoint=ENDPOINT)

@app.on_event("startup")
def register_agent():
    try:
        info = agent.get_registry_info()
        # agent.get_tasks()の結果を直接セット
        info["tasks"] = agent.get_tasks()
        print(f"[DEBUG] registry info to POST: {info}")
        resp = requests.post(REGISTRY_URL, json=info, timeout=5)
        resp.raise_for_status()
        agent.agent_id = resp.json().get("agent_id")
        print(f"[INFO] Agent registered: {agent.agent_id}")
    except Exception as e:
        print(f"[ERROR] Agent registration failed: {e}")

@app.post("/run")
async def run_task(request: Request):
    data = await request.json()
    task_type = data.get("type")
    params = data.get("parameters", {})
    if not task_type:
        return JSONResponse(status_code=400, content={"error": "type is required"})
    return agent.handle_request(task_type, params)

@app.get("/tasks")
def list_tasks():
    return agent.get_tasks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003, reload=True)
