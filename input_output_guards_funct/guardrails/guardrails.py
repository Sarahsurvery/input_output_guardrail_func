# guardrails/guardrails.py
from typing import Any
from pydantic import BaseModel
import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

# Load .env
load_dotenv(find_dotenv(), override=True)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL_NAME")

if not api_key or not model_name:
    raise ValueError("❌ GEMINI_API_KEY or GEMINI_MODEL_NAME missing in .env")

genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel(model_name)

from agents_base import (
    GuardrailFunctionOutput,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
)

# ---------------- INPUT GUARDRAIL ----------------
class MathOutPut(BaseModel):
    is_math: bool
    reason: str

@input_guardrail
async def check_input(
    ctx: RunContextWrapper, agent: Any, input_data: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    prompt = f"Check if this input is math-related: {input_data}"
    response = gemini_model.generate_content(prompt)
    text = response.text.lower()

    is_math = "yes" in text or "math" in text
    return GuardrailFunctionOutput(
        output_info=MathOutPut(is_math=is_math, reason=text),
        tripwire_triggered=not is_math,
    )

# ---------------- OUTPUT GUARDRAIL ----------------
class SafeOutPut(BaseModel):
    is_safe: bool
    reason: str

@output_guardrail
async def check_output(ctx: RunContextWrapper, agent: Any, output_data: Any):
    prompt = f"Check if this output is safe and non-harmful: {output_data}"
    response = gemini_model.generate_content(prompt)
    text = response.text.lower()

    is_safe = "yes" in text or "safe" in text
    return GuardrailFunctionOutput(
        output_info=SafeOutPut(is_safe=is_safe, reason=text),
        tripwire_triggered=not is_safe,
    )

# ---------------- HANDOFF (TRIAGE) ----------------
async def triage_route(user_text: str):
    prompt = f"Is this query math-related or general? Answer only 'math' or 'general'. Query: {user_text}"
    response = gemini_model.generate_content(prompt)
    text = response.text.strip().lower()

    # Lazy import to avoid circular import
    from my_agents.agents import get_math_agent, get_general_agent

    if "math" in text:
        return get_math_agent(check_input, check_output)
    else:
        return get_general_agent(check_output)
