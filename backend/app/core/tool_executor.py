import json
from typing import Any

from .session_state import SessionState
from .error_handler import format_structured_error
from ..tools.bank_tools import execute_bank_tool


def run_tool(tool_name: str, tool_input: dict, session_state: SessionState) -> str:
    """Single routing point for all tool execution (Claude-final pattern).

    Every tool call from any agent goes through here, which means session_state
    only needs to be threaded through one place rather than multiple call sites.
    Any new tool you add gets access to session state automatically just by
    being added to this routing function.
    """
    if tool_name in ("get_account", "get_rates", "get_faq",
                     "get_security_policies", "block_account",
                     "get_legal_terms", "get_privacy_policy"):
        return execute_bank_tool(tool_name, tool_input, session_state)
    else:
        return format_structured_error(
            "validation",
            f"Tool '{tool_name}' is not recognised.",
            retryable=False
        )


def run_tool_sync(tool_name: str, tool_input: dict,
                  session_state: SessionState) -> str:
    """Synchronous wrapper for tool execution."""
    return run_tool(tool_name, tool_input, session_state)
