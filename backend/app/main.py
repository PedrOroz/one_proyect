import os
import time
import threading
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import Config
from .core.session_state import SessionState
from .core.error_handler import AgentError
from .agents.router import RouterAgent
from .agents.worker_support import WorkerSupportAgent
from .agents.worker_security import WorkerSecurityAgent
from .agents.worker_legal import WorkerLegalAgent
from .agents.synthesizer import SynthesizerAgent

load_dotenv()

app = FastAPI(
    title="FinTech Multi-Agent Support System",
    description="Multi-agent system for digital banking customer support",
    version="1.0.0"
)

# --- CORS Configuration (restricted) ---
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --- Request / Response Models ---

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_index: int = 0
    routing_info: dict | None = None


class FeedbackRequest(BaseModel):
    session_id: str
    message_index: int
    feedback: str  # "positive" or "negative"


# --- Session Store with TTL cleanup ---

SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))
SESSION_MAX_COUNT = int(os.getenv("SESSION_MAX_COUNT", "1000"))
SESSION_CLEANUP_INTERVAL = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))

session_store: dict[str, SessionState] = {}
_session_lock = threading.Lock()


def _cleanup_expired_sessions() -> None:
    """Remove expired sessions from the in-memory store."""
    with _session_lock:
        expired_ids = [
            sid for sid, session in session_store.items()
            if session.is_expired(SESSION_TTL_SECONDS)
        ]
        for sid in expired_ids:
            del session_store[sid]


def _session_cleanup_loop() -> None:
    """Background thread that periodically cleans up expired sessions."""
    while True:
        time.sleep(SESSION_CLEANUP_INTERVAL)
        _cleanup_expired_sessions()


# Start the cleanup thread as a daemon (dies when main process exits)
_cleanup_thread = threading.Thread(target=_session_cleanup_loop, daemon=True)
_cleanup_thread.start()


# --- Agent Instances ---

router_agent = RouterAgent()
worker_support = WorkerSupportAgent()
worker_security = WorkerSecurityAgent()
worker_legal = WorkerLegalAgent()
synthesizer = SynthesizerAgent()


# --- Helper Functions ---

def get_or_create_session(session_id: str | None,
                          user_message: str) -> SessionState:
    with _session_lock:
        if session_id and session_id in session_store:
            session = session_store[session_id]
            session.touch()
            return session

        # Enforce max session count
        if len(session_store) >= SESSION_MAX_COUNT:
            _cleanup_expired_sessions()
            if len(session_store) >= SESSION_MAX_COUNT:
                # Evict oldest session
                oldest_id = min(
                    session_store,
                    key=lambda sid: session_store[sid].last_accessed
                )
                del session_store[oldest_id]

        session = SessionState(user_message)
        session_store[session.session_id] = session
        return session


def route_to_worker(agent_name: str, user_message: str,
                    session_state: SessionState) -> dict:
    """Route the query to the appropriate worker agent.

    Following Claude-final coordinator pattern: delegates to the
    correct specialist sub-agent based on router classification.
    """
    worker_map = {
        "RATES_AND_SUPPORT": worker_support,
        "SECURITY_AND_FRAUD": worker_security,
        "LEGAL_AND_PRIVACY": worker_legal,
    }

    worker = worker_map.get(agent_name)
    if not worker:
        return {
            "status": "general",
            "data": {"message": "No specialist needed for this query."},
            "note": "This was a general query that did not require specialist handling."
        }

    result = worker.handle_query(user_message, session_state)
    session_state.store_worker_result(agent_name, result)
    return result


# --- Static Files ---

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the chat interface from static files."""
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    raise HTTPException(
        status_code=404,
        detail="Frontend not found. Ensure static/index.html exists."
    )


# Mount static files for CSS, JS, and assets
if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static"
    )


# --- API Endpoints ---

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for the multi-agent system.

    Workflow:
    1. Router classifies the user intent
    2. Appropriate worker specialist handles the query
    3. Synthesizer combines all results into a final response
    """
    errors = Config.validate()
    if errors:
        raise HTTPException(status_code=500, detail="; ".join(errors))

    session = get_or_create_session(request.session_id, request.message)
    msg_index = session.increment_message_count()

    try:
        # Step 1: Route the query
        routing = router_agent.route(request.message, session)

        # Step 2: Process with the assigned worker
        worker_result = route_to_worker(
            routing["agent"], request.message, session
        )

        # Step 3: Synthesize the final response
        final_response = synthesizer.synthesize(session, request.message)

        routing_info = {
            "routed_to": routing["agent"],
            "confidence": routing["confidence"],
            "explanation": routing["explanation"],
        }
        if worker_result.get("status") == "failed":
            routing_info["worker_error"] = worker_result.get("error")

        return ChatResponse(
            response=final_response,
            session_id=session.session_id,
            message_index=msg_index,
            routing_info=routing_info
        )

    except AgentError as e:
        return ChatResponse(
            response=f"I encountered an issue: {e.message}",
            session_id=session.session_id,
            message_index=msg_index,
            routing_info={"error": e.to_dict()}
        )
    except Exception as e:
        return ChatResponse(
            response="I'm sorry, I encountered an unexpected error. "
                     "Please try again or contact support.",
            session_id=session.session_id,
            message_index=msg_index,
            routing_info={"error": str(e)}
        )


@app.post("/chat/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Record user feedback (positive/negative) on a specific message."""
    if request.feedback not in ("positive", "negative"):
        raise HTTPException(
            status_code=400,
            detail="Feedback must be 'positive' or 'negative'."
        )

    with _session_lock:
        session = session_store.get(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    session.record_feedback(request.message_index, request.feedback)
    return {"status": "ok", "message": "Feedback recorded."}


@app.get("/sessions", response_class=JSONResponse)
async def list_sessions():
    """List all active session summaries for the sidebar."""
    with _session_lock:
        summaries = []
        for sid, session in session_store.items():
            # Get first user message as title
            title = "Nueva conversación"
            for msg in session.conversation_history:
                if msg.get("role") == "user" and isinstance(msg.get("content"), str):
                    title = msg["content"][:60]
                    if len(msg["content"]) > 60:
                        title += "..."
                    break
            summaries.append({
                "session_id": sid,
                "title": title,
                "created_at": session.created_at,
                "message_count": session.message_count
            })
        # Sort newest first
        summaries.sort(key=lambda s: s["created_at"], reverse=True)
        return summaries


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fintech-multi-agent"}


@app.get("/session/{session_id}", response_class=JSONResponse)
async def get_session(session_id: str):
    """Retrieve session state for debugging."""
    with _session_lock:
        session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


if __name__ == "__main__":
    import uvicorn
    port = Config.API_PORT
    print(f"Starting FinTech Multi-Agent System on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
