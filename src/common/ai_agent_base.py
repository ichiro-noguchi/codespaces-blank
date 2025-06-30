from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIAgentBase(ABC):
    """
    AIAgentのベースクラス。
    各AIAgentサービスはこのクラスを継承して実装します。
    """
    def __init__(self, name: str, description: str, capabilities: List[str], endpoint: str):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.endpoint = endpoint
        self.agent_id = None  # 登録時にAgentRegistryServiceから付与

    @abstractmethod
    def handle_request(self, task_type: str, params: Dict[str, Any]) -> Any:
        """
        指定されたtask_typeとパラメータで処理を実行し、結果を返す。
        各AIAgentで実装必須。
        """
        pass

    @abstractmethod
    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        /tasksエンドポイントで返すタスク定義リスト。
        各AIAgentで必須実装。
        例: [{"type": "get_cpu_metrics", "parameters": {...}, ...}, ...]
        """
        pass

    def get_registry_info(self) -> Dict[str, Any]:
        """
        AgentRegistryServiceへ登録するための情報を返す。
        """
        return {
            'name': self.name,
            'description': self.description,
            'capabilities': self.capabilities,
            'endpoint': self.endpoint
        }
