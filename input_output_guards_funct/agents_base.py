# agents_base.py
from dataclasses import dataclass
from typing import Any, Callable, List, Awaitable

# ---------------- Guardrail Utilities ----------------
@dataclass
class GuardrailFunctionOutput:
    output_info: Any
    tripwire_triggered: bool

class RunContextWrapper:
    """Dummy context wrapper (expand later if needed)."""
    def __init__(self, data: Any = None):
        self.data = data

TResponseInputItem = Any

def input_guardrail(func: Callable[..., Awaitable[GuardrailFunctionOutput]]):
    """Decorator to mark a function as input guardrail"""
    return func

def output_guardrail(func: Callable[..., Awaitable[GuardrailFunctionOutput]]):
    """Decorator to mark a function as output guardrail"""
    return func

class InputGuardrailTripwireTriggered(Exception):
    """Raised when input guardrail blocks input"""
    pass

# ---------------- Agent ----------------
@dataclass
class Agent:
    name: str
    instructions: str
    model: Any
    input_guardrails: List[Callable] = None
    output_guardrails: List[Callable] = None

    async def run(self, user_text: str) -> str:
        # Run input guardrails
        if self.input_guardrails:
            for guard in self.input_guardrails:
                result = await guard(RunContextWrapper(), self, user_text)
                if result.tripwire_triggered:
                    raise InputGuardrailTripwireTriggered(result.output_info)

        # Call LLM
        response = self.model.generate_content(f"{self.instructions}\n\nUser: {user_text}")
        output_text = response.text

        # Run output guardrails
        if self.output_guardrails:
            for guard in self.output_guardrails:
                result = await guard(RunContextWrapper(), self, output_text)
                if result.tripwire_triggered:
                    return f"⚠️ Blocked Output: {result.output_info}"

        return output_text

# ---------------- Runner ----------------
class Runner:
    @staticmethod
    async def run(agent: Agent, user_text: str):
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output

        reply = await agent.run(user_text)
        return Result(final_output=reply)
