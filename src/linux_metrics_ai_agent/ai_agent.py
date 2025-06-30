from common.ai_agent_base import AIAgentBase
from typing import List, Dict, Any

class LinuxMetricsAIAgent(AIAgentBase):
    def __init__(self, endpoint: str):
        super().__init__(
            name="LinuxMetricsAIAgent",
            description="Linuxのメトリクスを取得するAIAgent",
            capabilities=[
                "list_metrics",
                "get_cpu_metrics",
                "get_memory_metrics",
                "get_disk_metrics"
            ],
            endpoint=endpoint
        )

    def handle_request(self, task_type: str, params: Dict[str, Any]) -> Any:
        if task_type == "list_metrics":
            return ["cpu", "memory", "disk"]
        elif task_type == "get_cpu_metrics":
            return {"cpu_usage": 42.0}  # ダミー値
        elif task_type == "get_memory_metrics":
            return {"memory_usage": 2048}  # ダミー値
        elif task_type == "get_disk_metrics":
            return {"disk_usage": 51200}  # ダミー値
        else:
            return {"error": "Unknown task type"}

    def get_tasks(self) -> List[Dict[str, Any]]:
        return [
            {"type": "list_metrics", "parameters": {}, "requires_consent": False},
            {"type": "get_cpu_metrics", "parameters": {}, "requires_consent": False},
            {"type": "get_memory_metrics", "parameters": {}, "requires_consent": False},
            {"type": "get_disk_metrics", "parameters": {}, "requires_consent": False}
        ]
