import json
import time
import uuid
from typing import Any, Optional


class SessionState:
    """Session state management following Claude-final verification gate pattern.

    Tracks verified identity, conversation context, and any other conditions
    that need to persist across tool calls within this conversation.
    Starts empty at the beginning of every conversation — there is
    no carry-over between sessions, which is intentional. Each customer
    interaction starts fresh with no inherited state from previous ones.

    Includes TTL support via last_accessed timestamp for automatic cleanup,
    and a feedback registry for tracking user thumbs up/down on responses.
    """

    DEFAULT_TTL_SECONDS: int = 1800  # 30 minutes

    def __init__(self, user_message: str = ""):
        self.session_id: str = str(uuid.uuid4())
        self.created_at: float = time.time()
        self.last_accessed: float = time.time()
        self.verified_user_id: Optional[str] = None
        self.verified_user_name: Optional[str] = None
        self.conversation_history: list[dict] = [
            {"role": "user", "content": user_message}
        ] if user_message else []
        self.assigned_agent: Optional[str] = None
        self.routing_confidence: float = 0.0
        self.worker_results: dict[str, Any] = {}
        self.coverage_notes: list[dict] = []
        self.feedback: list[dict] = []
        self.message_count: int = 0

    def touch(self) -> None:
        """Update last_accessed timestamp to keep the session alive."""
        self.last_accessed = time.time()

    def is_expired(self, ttl_seconds: int | None = None) -> bool:
        """Check if this session has exceeded its TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL_SECONDS
        return (time.time() - self.last_accessed) > ttl

    def verify_user(self, user_id: str, user_name: str) -> None:
        self.verified_user_id = user_id
        self.verified_user_name = user_name

    def is_verified(self) -> bool:
        return self.verified_user_id is not None

    def assign_agent(self, agent_name: str, confidence: float) -> None:
        self.assigned_agent = agent_name
        self.routing_confidence = confidence

    def store_worker_result(self, worker: str, result: dict) -> None:
        self.worker_results[worker] = result

    def store_worker_failure(self, worker: str, status: str, error_type: str,
                             message: str, retryable: bool = False) -> None:
        self.worker_results[worker] = {
            "status": status,
            "data": None
        }
        self.coverage_notes.append({
            "source": worker,
            "status": status,
            "error_type": error_type,
            "message": message,
            "retryable": retryable
        })

    def record_feedback(self, message_index: int, feedback: str) -> None:
        """Record user feedback (positive/negative) for a specific message."""
        self.feedback.append({
            "message_index": message_index,
            "feedback": feedback,
            "timestamp": time.time()
        })

    def append_message(self, role: str, content: Any) -> None:
        self.conversation_history.append({"role": role, "content": content})

    def increment_message_count(self) -> int:
        """Increment and return the current message count."""
        self.message_count += 1
        return self.message_count

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "verified_user_id": self.verified_user_id,
            "verified_user_name": self.verified_user_name,
            "assigned_agent": self.assigned_agent,
            "routing_confidence": self.routing_confidence,
            "worker_results": self.worker_results,
            "coverage_notes": self.coverage_notes,
            "feedback": self.feedback,
            "message_count": self.message_count
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

