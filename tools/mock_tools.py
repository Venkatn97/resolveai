from langchain_core.tools import tool
import random
import string
from datetime import datetime


def generate_id(prefix: str) -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


@tool
def create_jira_ticket(
    title: str,
    description: str,
    priority: str,
    category: str
) -> str:
    """
    Creates a Jira support ticket for the customer issue.

    Args:
        title: Short title of the issue
        description: Full description of the issue
        priority: low, medium, high or critical
        category: technical, billing, escalation or general
    """
    ticket_id = generate_id("JIRA")
    return f"Jira ticket {ticket_id} created. Priority: {priority}. Category: {category}."


@tool
def notify_slack(
    channel: str,
    message: str,
    priority: str
) -> str:
    """
    Sends a Slack notification to the engineering or support team.

    Args:
        channel: Slack channel name e.g. engineering, support, escalations
        message: The notification message
        priority: low, medium, high or critical
    """
    timestamp = datetime.now().strftime("%H:%M")
    return f"Slack notification sent to #{channel} at {timestamp}. Priority: {priority}."


@tool
def search_github_issues(query: str) -> str:
    """
    Searches GitHub issues for known bugs matching the customer problem.

    Args:
        query: Search query describing the technical issue
    """
    mock_issues = {
        "429": "Known issue #1234 — Rate limiting bug fixed in v2.3.1. Upgrade recommended.",
        "api": "Known issue #1456 — API timeout under high load. Fix in progress.",
        "webhook": "Known issue #1567 — Webhook retry logic fixed in v2.4.0.",
        "auth": "Known issue #1678 — OAuth token expiry bug fixed in v2.2.5.",
        "timeout": "Known issue #1789 — Connection timeout fixed in v2.3.2."
    }

    for keyword in mock_issues:
        if keyword.lower() in query.lower():
            return mock_issues[keyword]

    return "No known GitHub issues found matching this query."


@tool
def send_resolution_email(
    customer_email: str,
    customer_name: str,
    subject: str,
    resolution: str
) -> str:
    """
    Sends a resolution email to the customer.

    Args:
        customer_email: Customer email address
        customer_name: Customer name
        subject: Email subject
        resolution: The resolution message to send
    """
    return f"Resolution email sent to {customer_name} at {customer_email}. Subject: {subject}."


@tool
def check_billing_status(customer_email: str) -> str:
    """
    Checks the billing and subscription status for a customer.

    Args:
        customer_email: Customer email address
    """
    return f"Customer {customer_email} is on the Pro plan. Status: Active. Next billing date: March 1 2026. No outstanding invoices."


ALL_TOOLS = [
    create_jira_ticket,
    notify_slack,
    search_github_issues,
    send_resolution_email,
    check_billing_status
]