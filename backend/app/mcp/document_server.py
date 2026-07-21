import json
import os

from mcp.server.fastmcp import FastMCP

from ..core.error_handler import format_structured_error, success_response
from ..mock_data import (
    RATES_COMMISSIONS,
    FAQ_ENTRIES,
    SECURITY_POLICIES,
    LEGAL_TERMS,
    PRIVACY_POLICY
)

mcp = FastMCP("fintech-document-server")


DOCUMENT_STORE = {
    "rates_commissions": {
        "description": "Rates, commissions, and fees for all account types",
        "data": RATES_COMMISSIONS,
        "tags": ["pricing", "fees", "commissions", "rates"]
    },
    "faq": {
        "description": "Frequently asked questions by category",
        "data": FAQ_ENTRIES,
        "tags": ["support", "faq", "help"]
    },
    "security_policies": {
        "description": "Security policies and fraud prevention procedures",
        "data": SECURITY_POLICIES,
        "tags": ["security", "fraud", "protection"]
    },
    "legal_terms": {
        "description": "Legal terms and conditions documents",
        "data": LEGAL_TERMS,
        "tags": ["legal", "terms", "conditions"]
    },
    "privacy_policy": {
        "description": "Privacy policy information by section",
        "data": PRIVACY_POLICY,
        "tags": ["privacy", "data", "gdpr"]
    }
}


@mcp.tool()
def query_documentation(document_type: str, query: str) -> str:
    """Query a specific documentation type by name and return relevant entries.

    This is the primary RAG access point for worker agents. Each worker
    has exclusive access to specific documentation types and uses this
    tool to retrieve the information they need.

    Args:
        document_type: The documentation type to query (rates_commissions,
                      faq, security_policies, legal_terms, privacy_policy)
        query: The search term or category to look up within the document

    Returns:
        JSON string with matching documentation entries
    """
    document_type = document_type.strip().lower()

    if document_type not in DOCUMENT_STORE:
        return format_structured_error(
            "validation",
            f"Document type '{document_type}' not found. "
            f"Available types: {', '.join(DOCUMENT_STORE.keys())}",
            retryable=False
        )

    doc = DOCUMENT_STORE[document_type]
    data = doc["data"]
    query_lower = query.strip().lower()

    if isinstance(data, dict):
        if query_lower in data:
            return success_response(
                {"document_type": document_type, "entry": data[query_lower]},
                f"Found entry '{query_lower}' in {document_type}"
            )
        elif query_lower == "__all__":
            return success_response(
                {"document_type": document_type, "entries": data,
                 "tags": doc["tags"]},
                f"All entries in {document_type}"
            )
        else:
            keys = list(data.keys())
            return format_structured_error(
                "validation",
                f"No entry found for '{query}' in {document_type}. "
                f"Available entries: {', '.join(keys)}",
                retryable=False
            )

    return format_structured_error(
        "validation",
        f"Unexpected data format in {document_type}",
        retryable=False
    )


@mcp.tool()
def list_documentation_types() -> str:
    """List all available documentation types with their descriptions.

    Returns:
        JSON string with available documentation types and metadata
    """
    summary = {}
    for doc_type, info in DOCUMENT_STORE.items():
        summary[doc_type] = {
            "description": info["description"],
            "tags": info["tags"]
        }
    return success_response(
        {"document_types": summary},
        f"Found {len(summary)} documentation types"
    )


@mcp.tool()
def search_documentation(search_term: str) -> str:
    """Search across all documentation for a specific term.

    Performs a broad search to find which documents contain
    information relevant to the search term.

    Args:
        search_term: The term to search for across all documents

    Returns:
        JSON string with search results grouped by document type
    """
    search_term = search_term.strip().lower()
    results = {}

    for doc_type, info in DOCUMENT_STORE.items():
        data = info["data"]
        matches = []

        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                value_str = json.dumps(value).lower()

                if search_term in key_lower or search_term in value_str:
                    matches.append({
                        "key": key,
                        "data": value
                    })

        if matches:
            results[doc_type] = {
                "description": info["description"],
                "matches": matches
            }

    if not results:
        return format_structured_error(
            "validation",
            f"No documentation found matching '{search_term}'",
            retryable=False
        )

    return success_response(
        {"search_term": search_term, "results": results},
        f"Found matches in {len(results)} document types"
    )


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "sse")
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        port = int(os.getenv("MCP_PORT", "8001"))
        mcp.run(transport="sse", port=port)
