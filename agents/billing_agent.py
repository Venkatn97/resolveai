import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from agents.models import AgentState
from tools.mock_tools import (
    create_jira_ticket,
    check_billing_status,
    send_resolution_email,
    notify_slack
)

load_dotenv()

BILLING_PROMPT = """You are a billing support specialist for TechFlow SaaS.

You help customers with:
- Payment failures and retries
- Subscription upgrades and downgrades
- Invoice questions and disputes
- Refund requests
- Plan changes
- Billing cycle questions

Your workflow:
1. Check the customer billing status first
2. Create a Jira ticket to track the issue
3. Provide a clear resolution to the customer
4. If refund over $500 or legal threat — notify the support team on Slack
5. Send a resolution email to the customer

Always be empathetic, clear, and professional.
Never promise refunds without checking billing status first.
"""

BILLING_TOOLS = [
    create_jira_ticket,
    check_billing_status,
    send_resolution_email,
    notify_slack
]


def billing_node(state: AgentState) -> dict:
    llm = ChatBedrock(
        model_id=os.getenv("BEDROCK_MODEL_ID"),
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        model_kwargs={"temperature": 0.2, "max_tokens": 2048}
    )

    llm_with_tools = llm.bind_tools(BILLING_TOOLS)

    ticket = state.ticket
    user_message = f"""
Customer: {ticket.customer_name}
Email: {ticket.customer_email}
Subject: {ticket.subject}
Description: {ticket.description}
Priority: {state.priority.value if state.priority else 'medium'}

Please resolve this billing support ticket.
"""

    messages = [
        SystemMessage(content=BILLING_PROMPT)
    ] + state.messages + [
        HumanMessage(content=user_message)
    ]

    response = llm_with_tools.invoke(messages)

    tool_node = ToolNode(BILLING_TOOLS)

    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_names = [tc["name"] for tc in response.tool_calls]
        print(f"\n Technical agent calling tools: {', '.join(tool_names)}")

        tool_result = tool_node.invoke({"messages": [response]})
        tool_messages = tool_result["messages"]

        final_messages = messages + [response] + tool_messages
        final_response = llm_with_tools.invoke(final_messages)

        # keep calling until no more tool calls
        while hasattr(final_response, "tool_calls") and final_response.tool_calls:
            tool_names = [tc["name"] for tc in final_response.tool_calls]
            print(f"\n Billing agent calling more tools: {', '.join(tool_names)}")
            tool_result = tool_node.invoke({"messages": [final_response]})
            tool_messages = tool_result["messages"]
            final_messages = final_messages + [final_response] + tool_messages
            final_response = llm_with_tools.invoke(final_messages)

        resolution = final_response.content
    else:
        resolution = response.content
    print(f"\n Billing agent resolution ready")

    return {
        "messages": [response],
        "resolution": resolution,
        "assigned_agent": "billing_agent"
    }