# my_agents/agents.py
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

from agents_base import Agent  # <-- your custom Agent class

# ---------------- AGENTS ----------------
def get_math_agent(check_input, check_output):
    return Agent(
        "MathAgent",
        instructions="You are a math agent. Solve math problems step by step.",
        model=gemini_model,
        input_guardrails=[check_input],
        output_guardrails=[check_output],
    )

def get_general_agent(check_output):
    return Agent(
        "GeneralAgent",
        instructions="You are a helpful agent for general questions.",
        model=gemini_model,
        output_guardrails=[check_output],
    )
