import json
from typing import Optional
from anthropic import Anthropic

from ..core.session_state import SessionState
from ..config import Config

SYNTHESIZER_SYSTEM_PROMPT = """You are a response synthesis agent for a digital banking support system.
You receive structured research data from specialist agents and produce a
clear, helpful, cohesive response for the customer.

Your job is to take the outputs from multiple specialists (if applicable) and
combine them into a single, well-organized response that addresses the
customer's original question.

Requirements:
- Reference specific information from the specialist findings
- If multiple specialists were involved, organize the information logically
- If coverage_notes contains entries, explicitly acknowledge those gaps,
  state what information is unavailable and why it matters
- Do not speculate about missing data or fill gaps with assumptions
- Be specific and direct — the customer wants to understand their situation,
  not receive generic reassurance
- Use a professional but friendly tone
- Structure long responses with clear sections
- If the query was routed to GENERAL (no specialist needed), provide
  a helpful general response or clarification

Always format the response as natural conversation text."""


class SynthesizerAgent:
    """Synthesis agent that combines specialist outputs into final response.

    Following Claude-final coordinator pattern: receives structured data
    from sub-agents and produces a final synthesized response.
    """

    def __init__(self, model: Optional[str] = None):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = model or Config.MODEL_NAME

    def synthesize(self, session_state: SessionState,
                   original_message: str) -> str:
        """Synthesize a final response from all available worker results.

        Args:
            session_state: Session state containing worker results and coverage notes
            original_message: The original user message

        Returns:
            A cohesive response string
        """
        synthesis_input = {
            "original_query": original_message,
            "routed_to": session_state.assigned_agent,
            "routing_confidence": session_state.routing_confidence,
            "worker_results": session_state.worker_results,
            "coverage_notes": session_state.coverage_notes,
            "verified_user": {
                "user_id": session_state.verified_user_id,
                "user_name": session_state.verified_user_name
            } if session_state.is_verified() else None
        }

        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.SYNTHESIS_MAX_TOKENS,
            system=SYNTHESIZER_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    "A customer has contacted our banking support. "
                    "Here is the research data from our specialist agents:\n\n"
                    f"{json.dumps(synthesis_input, indent=2)}\n\n"
                    "Produce a clear, helpful response for the customer. "
                    "Address their original question using the information "
                    "gathered by the specialists."
                )
            }]
        )

        for block in response.content:
            if hasattr(block, "text"):
                return block.text

        return "I'm sorry, I was unable to generate a response. Please try again."
