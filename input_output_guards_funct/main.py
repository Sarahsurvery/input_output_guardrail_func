# main.py
import asyncio
from guardrails.guardrails import triage_route
from agents_base import Runner, InputGuardrailTripwireTriggered

def main():
    msg = input("Enter your question: ").strip()
    try:
        agent = asyncio.run(triage_route(msg))
        print(f"Handoff → {agent.name}")

        result = asyncio.run(Runner.run(agent, msg))
        print(f"\nFinal Output: {result.final_output}")

    except InputGuardrailTripwireTriggered:
        print("❌ Error: invalid input (blocked by input guardrail)")
    except Exception as ex:
        print(f"\nError: {ex}")

if __name__ == "__main__":
    main()
