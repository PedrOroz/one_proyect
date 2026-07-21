import json
from typing import Optional


class AgentError(Exception):
    """Base error class following Claude-final structured error pattern.

    Every error carries:
    - type: classification for routing and handling (validation, permission, timeout, api_error)
    - retryable: whether the caller can retry the same operation
    - message: human-readable explanation with recovery guidance
    """

    def __init__(self, error_type: str, message: str, retryable: bool = False,
                 details: Optional[dict] = None):
        self.error_type = error_type
        self.retryable = retryable
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": {
                "type": self.error_type,
                "retryable": self.retryable,
                "message": self.message,
                **self.details
            }
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class ValidationError(AgentError):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("validation", message, retryable=False, details=details)


class AgentPermissionError(AgentError):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("permission", message, retryable=False, details=details)


class TimeoutError_(AgentError):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("timeout", message, retryable=True, details=details)


class ApiError(AgentError):
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        retryable = status_code == 429
        super().__init__("api_error", message, retryable=retryable,
                         details={**(details or {}), "status_code": status_code})


def success_response(data: dict, message: str = "") -> str:
    return json.dumps({
        "success": True,
        "data": data,
        "message": message
    })


def format_structured_error(error_type: str, message: str,
                            retryable: bool = False) -> str:
    return json.dumps({
        "error": {
            "type": error_type,
            "retryable": retryable,
            "message": message
        }
    })
