import os
import asyncio
from typing import Annotated
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import UserMessage

load_dotenv()

# Global highly specialized LLM Client
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.2
)

# 🛠️ ENTERPRISE GROUNDING TOOLS (Pattern 4)
def query_invoice_ledger(invoice_id: Annotated[str, "The target alphanumeric invoice ID, e.g., INV-2026-88"]) -> str:
    """Queries corporate ERP financial ledger for real-time internal status tracking records."""
    mock_ledger = {
        "INV-2026-88": "Status: Paid. Amount: $4,500. Cleared on July 10, 2026 via corporate ACH.",
        "INV-2026-89": "Status: Pending Approval. Amount: $1,200. Stuck at Department Head signing queue."
    }
    return mock_ledger.get(invoice_id, f"Error: Invoice reference code '{invoice_id}' not found in database records.")

def search_hr_policy_handbook(query: Annotated[str, "Specific semantic topic or policy query to lookup"]) -> str:
    """Performs a vector-style look-up against the internal corporate 2026 HR Policy & Compliance Manual."""
    q = query.lower()
    if "leave" in q or "holiday" in q:
        return "[Document Fragment: Chapter 4, Sec 2] All FTEs receive 25 standard days of annual paid time off. Leave requests must be logged via the internal HR portal 48 hours prior."
    if "insurance" in q or "health" in q:
        return "[Document Fragment: Chapter 7, Sec 1] Premium health coverage includes comprehensive dental and vision frameworks covering 90% of procedures under group policy #HP-2026-X."
    return "Result: Match confidence low. Standard operational policy dictates consulting your localized HR coordinator for custom edge-cases."

# 🏢 Core Grounded Agents Allocation
finance_agent = AssistantAgent(
    name="Finance_Agent",
    model_client=model_client,
    tools=[query_invoice_ledger],
    system_message="You are the Finance Support Expert. Use the query_invoice_ledger tool to check real data whenever the user asks about specific invoices."
)

it_agent = AssistantAgent(
    name="IT_Support_Agent",
    model_client=model_client,
    system_message="You are the IT Support Specialist. Provide localized, explicit step-by-step technical recovery flows."
)

hr_agent = AssistantAgent(
    name="HR_Team_Agent",
    model_client=model_client,
    tools=[search_hr_policy_handbook],
    system_message="You are the HR Specialist. Use the search_hr_policy_handbook tool to pull authoritative context before answering policy questions."
)

product_agent = AssistantAgent(
    name="Product_Engineering_Agent",
    model_client=model_client,
    system_message="You are the Product Support Agent. Address software release updates, structural tracking bugs, or service availability metrics."
)

AGENTS_REGISTRY = {
    "Finance Agent": finance_agent,
    "IT Support Agent": it_agent,
    "HR Team Agent": hr_agent,
    "Product & Engineering Agent": product_agent
}

def get_agents():
    return AGENTS_REGISTRY

async def ai_triage_router(query: str, history_context: str = "") -> str:
    """Uses a context-aware LLM call to accurately route queries based on prompt and conversation history."""
    prompt = f"""
    You are an enterprise support router. Analyze the user's latest query along with recent chat history, 
    and classify it into exactly one of these operational categories:
    - Finance Agent (for payroll, expenses, tax, invoices)
    - IT Support Agent (for hardware, software access, VPN, password resets)
    - HR Team Agent (for leaves, holidays, health benefits, onboarding)
    - Product & Engineering Agent (for software bugs, production downtime, feature requests)

    [Conversation History Context]
    {history_context}

    Latest User Query: "{query}"

    Respond with ONLY the category name. Do not add any punctuation, markdown formatting, or extra text.
    """
    
    response = await model_client.create(messages=[UserMessage(content=prompt, source="user")])
    category = str(response.content).strip()
    
    valid_categories = ["Finance Agent", "IT Support Agent", "HR Team Agent", "Product & Engineering Agent"]
    return category if category in valid_categories else "Product & Engineering Agent"