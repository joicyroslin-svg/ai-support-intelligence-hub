def build_priority_prompt(ticket: str) -> str:
    return (
        "Analyze this support ticket and classify priority as High, Medium, or Low.\n"
        f"Ticket: {ticket}\n"
        "Only give priority and reason."
    )


def build_reply_prompt(ticket: str, tone: str, language: str) -> str:
    tone_text = f" Use a {tone.lower()} tone." if tone else ""
    language_text = f" Write in {language}." if language else ""
    return (
        "Generate a professional and polite customer support reply for this issue."
        f"{tone_text}{language_text}\n"
        f"{ticket}"
    )


def build_teardown_prompt(tool_name: str, focus: str, tool_info: str) -> str:
    return """
Full teardown of {} focusing on {}.

Tool response: {}

User-first analysis for building agents:
- Features list
- UI/UX patterns
- API endpoints/integration
- Strengths/weaknesses
- Best agent use cases
- Product lessons

Strict JSON:
{{
  "name": "{}",
  "features": ["list"],
  "ui_patterns": "str",
  "api_endpoints": ["list"],
  "strengths": ["list"],
  "weaknesses": ["list"],
  "agent_integration": "str",
  "product_insights": "str"
}}
""".format(tool_name, focus, tool_info, tool_name)


def build_agent_prompt(insights: str, user_goal: str) -> str:
    return """
Using these tool teardowns: {}

Build a real AI Agent for: {}

JSON config:
{{
  "agent_name": "str",
  "tools": [{{"tool": "str", "role": "str"}}],
  "system_prompt": "str",
  "ui_recommendations": "str",
  "user_flow": ["str"]
}}
User-first, production-ready.
""".format(insights, user_goal)
