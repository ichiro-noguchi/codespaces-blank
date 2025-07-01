# SuperAgentServer のエントリポイント（FastAPI + Gemini 対応版）
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
import httpx
import json
from pydantic import BaseModel
from typing import Any, Union # AnyとUnionをインポート
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

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

# SuperAgentServer 入出力モデル (README.md に基づく)
class CommandIn(BaseModel):
    command: str
    arguments: list[str] = []

class CommandOut(BaseModel):
    command: str
    status: str # "SUCCESS", "ERROR"
    errorMessage: str | None = None
    result: Union[Any, None] = None # any | None を Union[Any, None] に修正

class RequestIn(BaseModel):
    user_input: str

class RequestOut(BaseModel):
    status: str # 予約 (README.mdより)
    result: Union[Any, None] = None # any | None を Union[Any, None] に修正

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
            agents = resp.json()
            return agents

    def generate_plan(self, user_input, agents):
        # 利用可能なエージェントのdescription/capabilities/tasksをプロンプトに含める
        agent_profiles = {
            a['name']: {
                "description": a.get('description', ''),
                "capabilities": a.get('capabilities', []),
                "tasks": a.get('tasks', [])
            } for a in agents
        }
        plan_prompt = f"""
        ユーザ要求: {user_input}
        利用可能なAIAgentとその説明・機能・タスク仕様:
        {json.dumps(agent_profiles, indent=2, ensure_ascii=False)}

        上記の情報に基づき、ユーザ要求に応じるために最適なAIAgentとそのタスク、必要なパラメータをJSON形式で出力してください。
        出力形式:
        {{
          "agent": "<最適なAIAgent名>",
          "task": "<実行するタスクタイプ>",
          "parameters": {{ <タスクに必要なパラメータ> }}
        }}
        もし適切なAIAgentやタスクがない場合は、その旨をJSONで示してください。
        例: {{
          "agent": null,
          "task": null,
          "parameters": {{}},
          "reason": "適切なAIAgentが見つかりませんでした"
        }}
        注意: JSON以外の出力や説明文、コードブロック記号（```）は一切付けず、純粋なJSONのみを返してください。
        """
        try:
            # Gemini APIの呼び出し方法を修正
            logging.debug(f"[Gemini LLM] プロンプト送信: {plan_prompt}")
            model = genai.GenerativeModel(self.gemini_model)
            chat = model.start_chat(history=[])
            plan_resp = chat.send_message(plan_prompt)
            logging.debug(f"[Gemini LLM] レスポンス受信: {plan_resp.text}")
            plan_json = plan_resp.text.strip()
            # コードブロックで返ってきた場合は中身だけ抽出
            if plan_json.startswith('```'):
                plan_json = plan_json.split('\n', 1)[-1]  # 1行目（```json等）を除去
                if plan_json.endswith('```'):
                    plan_json = plan_json.rsplit('```', 1)[0]
                plan_json = plan_json.strip()
            if not plan_json:
                logging.error("[Gemini LLM] レスポンスが空です")
                return None, "Gemini LLM response is empty."
            try:
                plan = json.loads(plan_json)
            except Exception as je:
                logging.error(f"[Gemini LLM] JSONデコード失敗: {je}\nレスポンス内容: {plan_json}")
                return None, f"Gemini LLM response is not valid JSON: {je}\nResponse: {plan_json}"
            return plan, None
        except Exception as e:
            logging.error(f"[Gemini LLM] 例外発生: {e}")
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
        # agent_info["tasks"] から直接仕様を参照
        tasks = agent_info.get("tasks", [])
        task_def = next((t for t in tasks if t.get("type") == task_type), None)
        if task_def:
            consent_required = task_def.get("requires_consent", False)
            param_defs = task_def.get("parameters", {})
            for key in param_defs:
                if key not in parameters or parameters[key] in (None, ""):
                    missing_params.append(key)
        else:
            return {"error": f"Task definition for '{task_type}' not found in agent '{agent_name}'"}
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

    async def handle_command(self, command_in: CommandIn) -> CommandOut:
        """
        システムコマンドを処理し、CommandOut形式で結果を返却
        """
        command = command_in.command
        arguments = command_in.arguments

        if command == "help": # README.mdでは"/"を除去したものがcommand
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
            return CommandOut(command=command, status="SUCCESS", result={"agents": features})
        # 他のコマンドは今後拡張
        return CommandOut(command=command, status="ERROR", errorMessage=f"Unknown command: {command}")

    async def handle_request_logic(self, request_in: RequestIn) -> RequestOut:
        """
        ユーザ要求を処理し、RequestOut形式で結果を返却 (計画生成・実行ロジック)
        """
        user_input = request_in.user_input

        agents = await self.fetch_agents()
        plan, err = self.generate_plan(user_input, agents)

        if err:
            # エラー発生時はRequestOut形式でエラーを返す
            return RequestOut(status="ERROR", result={"error": f"Plan LLM error: {err}"})

        exec_result = await self.execute_plan(plan, agents)

        # execute_planの戻り値をRequestOut形式に変換
        if "error" in exec_result:
            return RequestOut(status="ERROR", result=exec_result)
        elif "missing_parameters" in exec_result:
            # README.mdのstatusは「予約」だが、ここでは状態を示すために使用
            return RequestOut(status="MISSING_PARAMS", result=exec_result)
        elif "consent_required" in exec_result and exec_result["consent_required"]:
             # README.mdのstatusは「予約」だが、ここでは状態を示すために使用
            return RequestOut(status="CONSENT_REQUIRED", result=exec_result)
        elif "result" in exec_result:
            return RequestOut(status="SUCCESS", result=exec_result["result"])
        else:
            # 想定外のケース
            return RequestOut(status="ERROR", result={"error": "Unexpected execution result", "details": exec_result})


super_agent = SuperAgentServer()

@app.post("/command", response_model=CommandOut) # /command エンドポイントを新設
async def command_endpoint(command_in: CommandIn):
    """
    ChatClientからのシステムコマンドを受け取り処理する
    """
    return await super_agent.handle_command(command_in)


@app.post("/request", response_model=RequestOut)
async def request_endpoint(request_in: RequestIn):
    """
    ChatClientからのユーザ要求を受け取り処理する
    """
    # README.mdの定義に従い、/requestは純粋なユーザ要求のみを処理
    # コマンド処理は/commandエンドポイントへ移動
    return await super_agent.handle_request_logic(request_in)

@app.get("/")
def index():
    return {"message": "SuperAgentServer is running."}

# ChatClientとのAPI連携や同意フローは今後実装

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
