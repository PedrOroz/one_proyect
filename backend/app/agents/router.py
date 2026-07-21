from typing import Optional
from ..core.session_state import SessionState
from .base_agent import BaseAgent

ROUTER_SYSTEM_PROMPT = """You are a routing agent for a digital banking support system.
Your job is to analyze the customer's message and determine which specialist
should handle their request.

You have ONE tool available: get_account — use it ONLY when the customer
provides identifying information and you need to verify their account.

DO NOT try to answer the customer's question yourself. Your ONLY job is to
route them to the right specialist.

Available specialists and their responsibilities:

1. RATES_AND_SUPPORT — Handles questions about:
   - Account fees, commissions, and pricing
   - Transaction limits and daily withdrawal limits
   - General FAQs about banking operations
   - Account types and their features
   - Transfer times and procedures

2. SECURITY_AND_FRAUD — Handles questions about:
   - Suspicious transactions or unauthorized activity
   - Fraud prevention and reporting
   - Account blocking or freezing
   - Lost or stolen cards
   - Security alerts and two-factor authentication

3. LEGAL_AND_PRIVACY — Handles questions about:
   - Terms and conditions
   - Privacy policy and data protection
   - User rights (access, correction, deletion of data)
   - Legal agreements and compliance

4. GENERAL — For messages that:
   - Are greetings or simple acknowledgments
   - Ask about agent capabilities
   - Are unclear or ambiguous
   - Contain multiple unrelated topics

Your response MUST be EXACTLY one of these four words on the first line:
RATES_AND_SUPPORT
SECURITY_AND_FRAUD
LEGAL_AND_PRIVACY
GENERAL

On the second line, add a brief explanation of why you chose that route.
On the third line, add your confidence level (0.0 to 1.0).

Example:
SECURITY_AND_FRAUD
Customer reports unauthorized transaction on their account
0.95

Do not include any other text in your response."""


class RouterAgent(BaseAgent):
    """Router agent that classifies user intent and delegates to specialists."""

    SYSTEM_PROMPT = ROUTER_SYSTEM_PROMPT
    AVAILABLE_TOOLS = BaseAgent.get_tools_for_worker("router")

    def __init__(self):
        super().__init__()

    def route(self, user_message: str,
              session_state: Optional[SessionState] = None) -> dict:
        """Classify the user message and return routing decision.

        Returns dict with:
        - agent: the assigned agent name
        - confidence: routing confidence (0.0-1.0)
        - explanation: why this routing was chosen
        - session_state: updated session with routing info
        """
        if session_state is None:
            session_state = SessionState(user_message)

        raw_response = self.run(user_message, session_state)

        lines = raw_response.strip().split("\n")
        agent_choice = lines[0].strip() if len(lines) > 0 else "GENERAL"
        explanation = lines[1].strip() if len(lines) > 1 else ""
        confidence_str = lines[2].strip() if len(lines) > 2 else "0.0"

        try:
            confidence = float(confidence_str)
        except ValueError:
            confidence = 0.0

        agent_name = agent_choice.upper()

        if agent_name not in ("RATES_AND_SUPPORT", "SECURITY_AND_FRAUD",
                              "LEGAL_AND_PRIVACY", "GENERAL"):
            agent_name = "GENERAL"
            confidence = 0.0
            explanation = "Unknown agent classification, defaulting to GENERAL"

        session_state.assign_agent(agent_name, confidence)

        return {
            "agent": agent_name,
            "confidence": confidence,
            "explanation": explanation,
            "session_state": session_state
        }

