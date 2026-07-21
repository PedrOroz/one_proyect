import json
from typing import Any

from ..core.session_state import SessionState
from ..core.error_handler import format_structured_error, success_response
from ..mock_data import MOCK_ACCOUNTS


def get_account(query: str, session_state: SessionState) -> str:
    """Look up a customer account by ID, email, or name."""
    query = query.strip().lower()

    for account in MOCK_ACCOUNTS.values():
        if (query == account["customer_id"].lower()
                or query == account["email"].lower()
                or query == account["name"].lower()):
            session_state.verify_user(account["customer_id"], account["name"])
            return success_response(account)

    return format_structured_error(
        "validation",
        f"No customer found matching '{query}'. The input may be "
        "misspelled or in the wrong format. Customer IDs follow the "
        "format CUST-XXXX. You can also search by full name or "
        "email address. Ask the customer to verify their details.",
        retryable=False
    )


def get_rates(account_type: str, session_state: SessionState) -> str:
    """Look up rates and commissions for a given account type."""
    from ..mock_data import RATES_COMMISSIONS

    account_type = account_type.strip().lower()

    if account_type in RATES_COMMISSIONS:
        return success_response(
            RATES_COMMISSIONS[account_type],
            f"Rates for {account_type} account retrieved."
        )

    return format_structured_error(
        "validation",
        f"No rate information found for account type '{account_type}'. "
        f"Available types: {', '.join(RATES_COMMISSIONS.keys())}",
        retryable=False
    )


def get_faq(category: str, session_state: SessionState) -> str:
    """Look up FAQ entries by category."""
    from ..mock_data import FAQ_ENTRIES

    category = category.strip().lower()

    if category in FAQ_ENTRIES:
        return success_response(
            FAQ_ENTRIES[category],
            f"FAQ entries for '{category}' retrieved."
        )

    return format_structured_error(
        "validation",
        f"No FAQ entries found for category '{category}'. "
        f"Available categories: {', '.join(FAQ_ENTRIES.keys())}",
        retryable=False
    )


def get_security_policies(policy_type: str, session_state: SessionState) -> str:
    """Look up security policies by type."""
    from ..mock_data import SECURITY_POLICIES

    policy_type = policy_type.strip().lower()

    if policy_type in SECURITY_POLICIES:
        return success_response(
            SECURITY_POLICIES[policy_type],
            f"Security policy '{policy_type}' retrieved."
        )

    return format_structured_error(
        "validation",
        f"No security policy found for '{policy_type}'. "
        f"Available policies: {', '.join(SECURITY_POLICIES.keys())}",
        retryable=False
    )


def block_account(customer_id: str, reason: str,
                  session_state: SessionState) -> str:
    """Block a customer account temporarily for security reasons.

    Gate check: identity must be verified before blocking.
    """
    if not session_state.is_verified():
        return format_structured_error(
            "permission",
            "Cannot block an account before customer identity has been "
            "verified. Call get_account first and confirm the customer's "
            "identity before attempting to block.",
            retryable=False
        )

    if customer_id != session_state.verified_user_id:
        return format_structured_error(
            "permission",
            f"Customer ID mismatch. The verified customer in this session is "
            f"{session_state.verified_user_id} but the block request "
            f"is for {customer_id}. Verify you have the correct customer "
            "before continuing.",
            retryable=False
        )

    if customer_id not in MOCK_ACCOUNTS:
        return format_structured_error(
            "validation",
            f"Account {customer_id} not found. Cannot block unknown account.",
            retryable=False
        )

    return success_response(
        {
            "customer_id": customer_id,
            "block_reason": reason,
            "status": "blocked",
            "block_id": "BLK-" + customer_id.split("-")[1],
            "message": (
                f"Account {customer_id} has been temporarily blocked due to: "
                f"{reason}. The customer will be notified and a review has "
                f"been initiated."
            )
        },
        f"Account {customer_id} blocked successfully."
    )


def get_legal_terms(document_type: str, session_state: SessionState) -> str:
    """Look up legal terms and conditions documents."""
    from ..mock_data import LEGAL_TERMS

    document_type = document_type.strip().lower()

    if document_type in LEGAL_TERMS:
        return success_response(
            LEGAL_TERMS[document_type],
            f"Legal document '{document_type}' retrieved."
        )

    return format_structured_error(
        "validation",
        f"No legal document found for '{document_type}'. "
        f"Available documents: {', '.join(LEGAL_TERMS.keys())}",
        retryable=False
    )


def get_privacy_policy(section: str, session_state: SessionState) -> str:
    """Look up privacy policy information by section."""
    from ..mock_data import PRIVACY_POLICY

    section = section.strip().lower()

    if section in PRIVACY_POLICY:
        return success_response(
            PRIVACY_POLICY[section],
            f"Privacy policy section '{section}' retrieved."
        )

    return format_structured_error(
        "validation",
        f"No privacy policy section found for '{section}'. "
        f"Available sections: {', '.join(PRIVACY_POLICY.keys())}",
        retryable=False
    )


TOOL_REGISTRY = {
    "get_account": get_account,
    "get_rates": get_rates,
    "get_faq": get_faq,
    "get_security_policies": get_security_policies,
    "block_account": block_account,
    "get_legal_terms": get_legal_terms,
    "get_privacy_policy": get_privacy_policy,
}


def execute_bank_tool(tool_name: str, tool_input: dict,
                      session_state: SessionState) -> str:
    """Route tool execution to the correct handler."""
    handler = TOOL_REGISTRY.get(tool_name)
    if not handler:
        return format_structured_error(
            "validation",
            f"Tool '{tool_name}' is not recognised.",
            retryable=False
        )
    return handler(**tool_input, session_state=session_state)


TOOL_DEFINITIONS = [
    {
        "name": "get_account",
        "description": (
            "Look up a customer account by customer ID, email address, or full name. "
            "Use this tool when you need to verify who you are speaking with or "
            "retrieve account information including account type, status, and balance. "
            "This must be called before any sensitive operations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Search term: customer ID (CUST-XXXX), "
                        "email address, or full name."
                    )
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_rates",
        "description": (
            "Look up rates, commissions, and fees for a specific account type. "
            "Use this tool when a customer asks about pricing, commissions, "
            "transaction fees, or account maintenance costs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_type": {
                    "type": "string",
                    "description": (
                        "The account type to look up rates for "
                        "(e.g. 'basic', 'premium', 'business', 'student')"
                    )
                }
            },
            "required": ["account_type"]
        }
    },
    {
        "name": "get_faq",
        "description": (
            "Look up frequently asked questions by category. "
            "Use this tool when a customer asks common questions about "
            "account operations, transfers, limits, or general banking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "FAQ category to retrieve "
                        "(e.g. 'transfers', 'accounts', 'limits', 'general')"
                    )
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_security_policies",
        "description": (
            "Look up security policies and fraud prevention procedures. "
            "Use this tool when a customer reports suspicious activity, "
            "unauthorized transactions, or asks about account protection."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_type": {
                    "type": "string",
                    "description": (
                        "The security policy type to retrieve "
                        "(e.g. 'fraud_prevention', 'unauthorized_transactions', "
                        "'account_protection', 'data_security')"
                    )
                }
            },
            "required": ["policy_type"]
        }
    },
    {
        "name": "block_account",
        "description": (
            "Temporarily block a customer account for security reasons. "
            "Use this tool when a customer reports fraud, unauthorized access, "
            "or when suspicious activity is detected. Requires prior identity "
            "verification via get_account."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The verified customer ID (e.g. 'CUST-4492')"
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for blocking the account"
                }
            },
            "required": ["customer_id", "reason"]
        }
    },
    {
        "name": "get_legal_terms",
        "description": (
            "Look up legal terms and conditions documents. "
            "Use this tool when a customer asks about terms of service, "
            "legal agreements, or contractual obligations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_type": {
                    "type": "string",
                    "description": (
                        "The legal document type to retrieve "
                        "(e.g. 'terms_of_service', 'terms_of_use', "
                        "'service_agreement')"
                    )
                }
            },
            "required": ["document_type"]
        }
    },
    {
        "name": "get_privacy_policy",
        "description": (
            "Look up privacy policy information by section. "
            "Use this tool when a customer asks about data protection, "
            "personal information handling, or privacy rights."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": (
                        "The privacy policy section to retrieve "
                        "(e.g. 'data_collection', 'data_usage', "
                        "'data_sharing', 'user_rights', 'data_retention')"
                    )
                }
            },
            "required": ["section"]
        }
    }
]
