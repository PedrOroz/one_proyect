import json
from typing import Any, Optional

from anthropic import Anthropic

from ..core.session_state import SessionState
from ..core.tool_executor import run_tool
from ..tools.bank_tools import TOOL_DEFINITIONS
from ..config import Config


class BaseAgent:
    """Base agent class following Claude-final agent patterns.

    Provides the core agent loop: send messages, handle tool calls,
    and return final responses. Subclasses define their own SYSTEM_PROMPT
    and available tools.
    """

    SYSTEM_PROMPT: str = ""
    AVAILABLE_TOOLS: list[dict] = []

    def __init__(self, model: Optional[str] = None):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = model or Config.MODEL_NAME
        self.max_tokens = Config.MAX_TOKENS

    def run(self, user_message: str,
            session_state: Optional[SessionState] = None) -> str:
        """Run the agent loop: process user message, handle tools, return response."""
        if session_state is None:
            session_state = SessionState(user_message)
        else:
            session_state.append_message("user", user_message)

        conversation_history = session_state.conversation_history.copy()

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.SYSTEM_PROMPT,
                tools=self.AVAILABLE_TOOLS,
                messages=conversation_history
            )

            conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return ""

            if response.stop_reason == "tool_use":
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        result = run_tool(
                            block.name,
                            block.input,
                            session_state
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

    def run_with_structured_result(self, user_message: str,
                                   session_state: SessionState) -> dict:
        """Run agent and return structured result with status and data."""
        try:
            response_text = self.run(user_message, session_state)
            try:
                data = json.loads(response_text)
                return {"status": "success", "data": data}
            except json.JSONDecodeError:
                return {"status": "success", "data": {"raw_response": response_text}}
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "data": None
            }

    @staticmethod
    def get_tools_for_worker(worker_type: str) -> list[dict]:
        """Get the subset of tools relevant to a specific worker."""
        worker_tool_map = {
            "support": ["get_account", "get_rates", "get_faq"],
            "security": ["get_account", "get_security_policies", "block_account"],
            "legal": ["get_account", "get_legal_terms", "get_privacy_policy"],
            "router": ["get_account"],
            "synthesizer": []
        }

        tool_names = worker_tool_map.get(worker_type, [])
        return [t for t in TOOL_DEFINITIONS if t["name"] in tool_names]
