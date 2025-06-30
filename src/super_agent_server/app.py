# SuperAgentServer のエントリポイント（FastAPI + Gemini 対応版）
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
import httpx
import json

app = FastAPI()

# CORS設定: 特定のオリジンからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://edo.marble-corp.com:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini APIキー・モデル名を環境変数から取得
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-pro")
AGENT_REGISTRY_URL = os.environ.get("AGENT_REGISTRY_URL", "http://agent_registry_service:5002")

class SuperAgentServer:
    def __init__(self):
        self.gemini_api_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL
        self.agent_registry_url = AGENT_REGISTRY_URL
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)

    async def fetch_agents(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.agent_registry_url}/agents")
            return resp.json()

    def generate_plan(self, user_input, agents):
        plan_prompt = f"""
        ユーザ要求: {user_input}
        利用可能なAIAgent: {[a['name'] for a in agents]}
        どのAIAgentのどのタスクを使うべきか、JSONで出力してください。
        """
        try:
            plan_resp = genai.chat.completions.create(
                model=self.gemini_model,
                messages=[{"role": "user", "content": plan_prompt}]
            )
            plan_json = plan_resp.choices[0].message.content.strip()
            plan = json.loads(plan_json)
            return plan, None
        except Exception as e:
            return None, str(e)

    async def execute_plan(self, plan, agents):
        """
        実行計画(plan)に従い、AIAgentのエンドポイント/runにPOSTしてタスクを実行。
        パラメータが不足している場合はChatClientに追加情報を要求する。
        """
        if not plan or not isinstance(plan, dict):
            return {"error": "Invalid plan format"}
        agent_name = plan.get("agent")
        task_type = plan.get("task")
        parameters = plan.get("parameters", {})
        # agent_nameからエンドポイントを特定
        agent_info = next((a for a in agents if a.get("name") == agent_name), None)
        if not agent_info:
            return {"error": f"Agent '{agent_name}' not found"}
        endpoint = agent_info.get("endpoint")
        if not endpoint:
            return {"error": f"Endpoint for agent '{agent_name}' not found"}
        # requires_consent判定 & パラメータ必須チェック
        consent_required = False
        missing_params = []
        try:
            async with httpx.AsyncClient() as client:
                tasks_resp = await client.get(f"{endpoint}/tasks")
                tasks = tasks_resp.json()
                task_def = next((t for t in tasks if t.get("type") == task_type), None)
                if task_def:
                    consent_required = task_def.get("requires_consent", False)
                    # パラメータ必須チェック
                    param_defs = task_def.get("parameters", {})
                    for key in param_defs:
                        if key not in parameters or parameters[key] in (None, ""):
                            missing_params.append(key)
        except Exception as e:
            return {"error": f"Failed to fetch tasks from agent: {e}"}
        if missing_params:
            return {"missing_parameters": missing_params, "plan": plan}
        if consent_required:
            return {"consent_required": True, "plan": plan}
        # 実際にAIAgentの/runを呼び出す
        try:
            async with httpx.AsyncClient() as client:
                run_resp = await client.post(f"{endpoint}/run", json={"type": task_type, "parameters": parameters})
                result = run_resp.json()
            return {"result": result, "consent_required": False}
        except Exception as e:
            return {"error": f"Failed to execute agent task: {e}"}

    async def handle_command(self, command: str):
        if command == "/help":
            agents = await self.fetch_agents()
            # 機能一覧を分かりやすく整形
            features = []
            for agent in agents:
                features.append({
                    "name": agent.get("name"),
                    "description": agent.get("description"),
                    "capabilities": agent.get("capabilities", []),
                    "endpoint": agent.get("endpoint"),
                    "status": agent.get("status")
                })
            return {"help": features}
        # 他のコマンドは今後拡張
        return {"error": f"Unknown command: {command}"}

super_agent = SuperAgentServer()

@app.post("/request")
async def handle_request(request: Request):
    """
    ChatClientからのユーザ入力を受け取り、
    - AgentRegistryServiceからAIAgent情報を取得
    - Gemini LLMで実行計画を生成
    - 必要に応じてAIAgentやLLM、同意確認を自律的に実行
    - 結果を返却
    """
    data = await request.json()
    user_input = data.get("user_input", "")
    if user_input.startswith("/"):
        # SuperAgentServerコマンドとして処理
        return await super_agent.handle_command(user_input)
    agents = await super_agent.fetch_agents()
    plan, err = super_agent.generate_plan(user_input, agents)
    if err:
        return JSONResponse(status_code=500, content={"error": f"Plan LLM error: {err}"})
    exec_result = await super_agent.execute_plan(plan, agents)
    return {"plan": plan, **exec_result}

@app.get("/")
def index():
    return {"message": "SuperAgentServer is running."}

# ChatClientとのAPI連携や同意フローは今後実装

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
