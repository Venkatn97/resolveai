import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from agents.models import AgentState, TicketCategory, TicketPriority

load_dotenv()

TRIAGE_PROMPT = """You are a support ticket triage agent for TechFlow SaaS.

Your job is to:
1. Read the customer support ticket
2. Classify it into one of these categories:
   - technical: API issues, bugs, errors, integration problems
   - billing: payments, refunds, subscriptions, invoices
   - escalation: angry customers, legal threats, critical outages
   - general: feature requests, how-to questions, general inquiries

3. Assign a priority:
   - critical: system down, data loss, security breach
   - high: major feature broken, payment failed
   - medium: partial functionality affected
   - low: minor issue, general question

4. Decide which agent should handle it:
   - technical_agent: for technical category
   - billing_agent: for billing category
   - escalation_agent: for escalation category
   - general_agent: for general category

Respond in this exact format:
CATEGORY: <category>
PRIORITY: <priority>
ASSIGNED_TO: <agent_name>
REASON: <one sentence explanation>
"""


def triage_node(state: AgentState) -> dict:
    llm = ChatBedrock(
        model_id=os.getenv("BEDROCK_MODEL_ID"),
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        model_kwargs={"temperature": 0.1, "max_tokens": 512}
    )

    ticket = state.ticket
    user_message = f"""
Customer: {ticket.customer_name}
Email: {ticket.customer_email}
Subject: {ticket.subject}
Description: {ticket.description}
"""

    messages = [
        SystemMessage(content=TRIAGE_PROMPT),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    content = response.content

    category = TicketCategory.GENERAL
    priority = TicketPriority.MEDIUM
    assigned_agent = "general_agent"

    for line in content.split("\n"):
        if line.startswith("CATEGORY:"):
            value = line.split(":")[1].strip().lower()
            try:
                category = TicketCategory(value)
            except ValueError:
                pass
        elif line.startswith("PRIORITY:"):
            value = line.split(":")[1].strip().lower()
            try:
                priority = TicketPriority(value)
            except ValueError:
                pass
        elif line.startswith("ASSIGNED_TO:"):
            assigned_agent = line.split(":")[1].strip()

    print(f"\n Triage complete:")
    print(f"   Category: {category.value}")
    print(f"   Priority: {priority.value}")
    print(f"   Assigned to: {assigned_agent}")

    return {
        "messages": [response],
        "category": category,
        "priority": priority,
        "assigned_agent": assigned_agent
    }