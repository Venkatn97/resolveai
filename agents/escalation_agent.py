import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from agents.models import AgentState
from tools.mock_tools import (
    create_jira_ticket,
    notify_slack,
    send_resolution_email,
    check_billing_status
)

load_dotenv()

ESCALATION_PROMPT = """You are a senior customer success manager for TechFlow SaaS.

You handle the most critical and sensitive customer situations:
- Extremely angry or frustrated customers
- Legal threats or mentions of lawyers
- Critical system outages affecting the customer
- Churn risk — customer threatening to cancel
- VIP customer complaints
- Situations that could damage TechFlow's reputation

Your workflow:
1. Immediately notify the support team on Slack with full details
2. Create a high priority Jira ticket
3. If billing related — check their billing status
4. Craft a very empathetic and professional response
5. Offer concrete next steps and a personal follow up
6. Send resolution email with your direct contact details

Always:
- Be extremely empathetic and apologetic
- Take full ownership of the problem
- Offer concrete compensation or resolution
- Never argue with the customer
- Escalate to human review if situation is extremely serious
"""

ESCALATION_TOOLS = [
    create_jira_ticket,
    notify_slack,
    send_resolution_email,
    check_billing_status
]


def escalation_node(state: AgentState) -> dict:
    llm = ChatBedrock(
        model_id=os.getenv("BEDROCK_MODEL_ID"),
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        model_kwargs={"temperature": 0.3, "max_tokens": 2048}
    )

    llm_with_tools = llm.bind_tools(ESCALATION_TOOLS)

    ticket = state.ticket
    user_message = f"""
Customer: {ticket.customer_name}
Email: {ticket.customer_email}
Subject: {ticket.subject}
Description: {ticket.description}
Priority: {state.priority.value if state.priority else 'critical'}

This is an escalated ticket. Handle with highest priority and care.
"""

    messages = [
        SystemMessage(content=ESCALATION_PROMPT)
    ] + state.messages + [
        HumanMessage(content=user_message)
    ]

    response = llm_with_tools.invoke(messages)

    tool_node = ToolNode(ESCALATION_TOOLS)

    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_names = [tc["name"] for tc in response.tool_calls]
        print(f"\n Escalation agent calling tools: {', '.join(tool_names)}")

        tool_result = tool_node.invoke({"messages": [response]})
        tool_messages = tool_result["messages"]

        final_messages = messages + [response] + tool_messages
        final_response = llm_with_tools.invoke(final_messages)

        # keep calling until no more tool calls
        while hasattr(final_response, "tool_calls") and final_response.tool_calls:
            tool_names = [tc["name"] for tc in final_response.tool_calls]
            print(f"\n Technical agent calling more tools: {', '.join(tool_names)}")
            tool_result = tool_node.invoke({"messages": [final_response]})
            tool_messages = tool_result["messages"]
            final_messages = final_messages + [final_response] + tool_messages
            final_response = llm_with_tools.invoke(final_messages)

        resolution = final_response.content
    else:
        resolution = response.content
    print(f"\n Escalation agent resolution ready")

    return {
        "messages": [response],
        "resolution": resolution,
        "assigned_agent": "escalation_agent"
    }