class AgentExecutionError(Exception):
    """Raised when an AI Agent fails to execute its core logic."""

    def __init__(
        self, agent_name: str, pr_id: int, input_hash: str, message: str
    ) -> None:
        if input_hash == "unknown_hash":
            import logging

            logging.getLogger(__name__).warning(
                f"Missing head_sha in state when raising AgentExecutionError in {agent_name} for PR {pr_id}"
            )
        self.agent_name = agent_name
        self.pr_id = pr_id
        self.input_hash = input_hash
        self.message = message
        super().__init__(f"[{agent_name}] PR {pr_id} (Hash: {input_hash}): {message}")
