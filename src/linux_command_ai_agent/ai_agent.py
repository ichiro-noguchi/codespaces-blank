from ai_agent_base import AIAgentBase
from typing import List, Dict, Any
import subprocess
# Gemini用のimport例（google.generativeai）
import os
import google.generativeai as genai

class LinuxCommandAIAgent(AIAgentBase):
    def __init__(self, endpoint: str):
        super().__init__(
            name="LinuxCommandAIAgent",
            description="Linuxサーバ上でコマンド提案や実行を行い、システム操作や自動化を支援するAIAgent。コマンドライン操作の自動化や運用効率化に利用可能。",
            capabilities=[
                "suggest_command",
                "run_command"
            ],
            endpoint=endpoint
        )
        # Gemini APIキーの設定
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = "gemini-pro"

    def suggest_command(self, user_instruction: str) -> Dict[str, Any]:
        """
        ユーザの指示からコマンドラインを提案する（Gemini利用）
        """
        if not self.gemini_api_key:
            return {"error": "GEMINI_API_KEY not set"}
        prompt = f"""
        ユーザの指示: {user_instruction}
        上記の指示を実現するLinuxコマンドを1行で提案してください。
        コマンドのみを返してください。
        """
        try:
            response = genai.chat.completions.create(
                model=self.gemini_model,
                messages=[{"role": "user", "content": prompt}]
            )
            command = response.choices[0].message.content.strip()
            return {"suggested_command": command}
        except Exception as e:
            return {"error": str(e)}

    def run_command(self, command: str, working_directory: str = "/tmp") -> Dict[str, Any]:
        """
        指定コマンドを実行する（安全のためダミー実装。実運用時は要サニタイズ）
        """
        try:
            # 実際のコマンド実行例（危険なので本番は要制限）
            # result = subprocess.check_output(command, shell=True, cwd=working_directory, text=True)
            # return {"result": result}
            return {"result": f"実行: {command} (in {working_directory})"}
        except Exception as e:
            return {"error": str(e)}

    def handle_request(self, task_type: str, params: Dict[str, Any]) -> Any:
        if task_type == "suggest_command":
            user_instruction = params.get("user_instruction", "")
            return self.suggest_command(user_instruction)
        elif task_type == "run_command":
            cmd = params.get("command", "echo 'no command'")
            working_dir = params.get("working_directory", "/tmp")
            return self.run_command(cmd, working_dir)
        else:
            return {"error": "Unknown task type"}

    def get_tasks(self) -> List[Dict[str, Any]]:
        return [
            {"type": "suggest_command", "parameters": {"user_instruction": "str"}, "requires_consent": False},
            {"type": "run_command", "parameters": {"command": "str", "working_directory": "str (optional)"}, "requires_consent": True}
        ]
