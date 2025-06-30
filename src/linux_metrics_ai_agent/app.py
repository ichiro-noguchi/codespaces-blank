from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from ai_agent import LinuxMetricsAIAgent
import os

app = FastAPI()

# エージェントのエンドポイントURL（本番では環境変数や設定ファイルで指定）
ENDPOINT = os.environ.get("AGENT_ENDPOINT", "http://localhost:5004")
agent = LinuxMetricsAIAgent(endpoint=ENDPOINT)

@app.get("/tasks")
def get_tasks():
    """対応可能なタスク定義リストを返す"""
    return agent.get_tasks()

@app.post("/run")
async def run_task(request: Request):
    data = await request.json()
    task_type = data.get("type")
    params = data.get("parameters", {})
    if not task_type:
        return JSONResponse(status_code=400, content={"error": "type is required"})
    return agent.handle_request(task_type, params)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5004, reload=True)
