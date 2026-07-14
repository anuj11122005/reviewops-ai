class AgentExecutionError(Exception):
    """Raised when an AI Agent fails to execute its core logic."""

    def __init__(self, agent_name: str, pr_id: int, message: str) -> None:
        self.agent_name = agent_name
        self.pr_id = pr_id
        self.message = message
        super().__init__(f"[{agent_name}] PR {pr_id}: {message}")
