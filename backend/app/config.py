import os


class Config:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-sonnet-4-6")
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "claude-sonnet-4-6")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
    SYNTHESIS_MAX_TOKENS: int = int(os.getenv("SYNTHESIS_MAX_TOKENS", "2048"))
    MCP_TRANSPORT: str = os.getenv("MCP_TRANSPORT", "sse")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8001"))
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "/app/data/documents")
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "/app/data/vector_store")

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is not set")
        return errors
