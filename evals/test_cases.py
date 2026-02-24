import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from rich.console import Console
from rich.table import Table
from agents.models import AgentState, SupportTicket
from agents.graph import resolveai
from langchain_core.messages import HumanMessage

console = Console()

TEST_CASES = [
    {
        "name": "API Rate Limiting",
        "customer_name": "John Smith",
        "customer_email": "john@acme.com",
        "subject": "API returning 429 errors",
        "description": "Our integration keeps getting 429 Too Many Requests errors.",
        "expected_category": "technical",
        "expected_agent": "technical_agent"
    },
    {
        "name": "Webhook Not Working",
        "customer_name": "Alice Chen",
        "customer_email": "alice@tech.com",
        "subject": "Webhooks stopped firing",
        "description": "Our webhooks stopped sending events since yesterday. No errors in logs.",
        "expected_category": "technical",
        "expected_agent": "technical_agent"
    },
    {
        "name": "Duplicate Charge",
        "customer_name": "Sarah Johnson",
        "customer_email": "sarah@startup.com",
        "subject": "Charged twice this month",
        "description": "I was charged twice for my Pro subscription. Need refund immediately.",
        "expected_category": "billing",
        "expected_agent": "billing_agent"
    },
    {
        "name": "Subscription Upgrade",
        "customer_name": "Bob Wilson",
        "customer_email": "bob@company.com",
        "subject": "Want to upgrade to Enterprise",
        "description": "We need to upgrade from Pro to Enterprise plan. How do I do this?",
        "expected_category": "billing",
        "expected_agent": "billing_agent"
    },
    {
        "name": "Legal Threat",
        "customer_name": "Michael Brown",
        "customer_email": "michael@enterprise.com",
        "subject": "Calling lawyers if not resolved",
        "description": "Platform down 6 hours, lost $50000. Calling lawyers and cancelling $5000/month contract.",
        "expected_category": "escalation",
        "expected_agent": "escalation_agent"
    },
    {
        "name": "Angry Customer",
        "customer_name": "Karen Davis",
        "customer_email": "karen@firm.com",
        "subject": "This is completely unacceptable",
        "description": "I have been ignored for 2 days. This is the worst service I have ever experienced. I want to speak to a manager NOW.",
        "expected_category": "escalation",
        "expected_agent": "escalation_agent"
    },
    {
        "name": "Auth Token Issue",
        "customer_name": "Dev Team",
        "customer_email": "dev@startup.io",
        "subject": "OAuth tokens expiring too fast",
        "description": "Our OAuth tokens are expiring after 10 minutes instead of 24 hours. Breaking our integration.",
        "expected_category": "technical",
        "expected_agent": "technical_agent"
    },
    {
        "name": "Invoice Question",
        "customer_name": "Finance Team",
        "customer_email": "finance@corp.com",
        "subject": "Need invoice for tax purposes",
        "description": "We need a detailed invoice for Q4 2025 for our tax filing. Can you send it?",
        "expected_category": "billing",
        "expected_agent": "billing_agent"
    }
]


def run_evals():
    console.print("\n[bold cyan]ResolveAI — Automated Evals[/bold cyan]")
    console.print(f"Running {len(TEST_CASES)} test cases...\n")

    results = []
    passed = 0
    failed = 0

    for i, test in enumerate(TEST_CASES):
        console.print(f"[dim]Test {i+1}/{len(TEST_CASES)}: {test['name']}...[/dim]")

        ticket = SupportTicket(
            ticket_id=str(uuid.uuid4())[:8],
            customer_name=test["customer_name"],
            customer_email=test["customer_email"],
            subject=test["subject"],
            description=test["description"]
        )

        initial_state = AgentState(
            messages=[HumanMessage(content=test["description"])],
            ticket=ticket
        )

        try:
            result = resolveai.invoke(initial_state)

            category_correct = (
                result.get("category") and
                result.get("category").value == test["expected_category"]
            )
            agent_correct = result.get("assigned_agent") == test["expected_agent"]
            has_resolution = bool(result.get("resolution"))

            test_passed = category_correct and agent_correct and has_resolution

            if test_passed:
                passed += 1
                status = "[green]PASS[/green]"
            else:
                failed += 1
                status = "[red]FAIL[/red]"

            results.append({
                "name": test["name"],
                "status": status,
                "expected_category": test["expected_category"],
                "actual_category": result.get("category").value if result.get("category") else "none",
                "expected_agent": test["expected_agent"],
                "actual_agent": result.get("assigned_agent", "none"),
                "has_resolution": "yes" if has_resolution else "no"
            })

        except Exception as e:
            failed += 1
            results.append({
                "name": test["name"],
                "status": "[red]ERROR[/red]",
                "expected_category": test["expected_category"],
                "actual_category": "error",
                "expected_agent": test["expected_agent"],
                "actual_agent": "error",
                "has_resolution": "no"
            })
            console.print(f"[red]Error: {str(e)}[/red]")

    table = Table(title="ResolveAI Eval Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status")
    table.add_column("Expected Category")
    table.add_column("Actual Category")
    table.add_column("Expected Agent")
    table.add_column("Actual Agent")
    table.add_column("Resolution")

    for r in results:
        table.add_row(
            r["name"],
            r["status"],
            r["expected_category"],
            r["actual_category"],
            r["expected_agent"],
            r["actual_agent"],
            r["has_resolution"]
        )

    console.print(table)

    pass_rate = (passed / len(TEST_CASES)) * 100
    console.print(f"\n[bold]Results: {passed}/{len(TEST_CASES)} passed ({pass_rate:.0f}%)[/bold]")

    if pass_rate >= 80:
        console.print("[green]PASSED — ResolveAI is ready for deployment[/green]")
    else:
        console.print("[red]FAILED — Fix failing tests before deploying[/red]")

    return pass_rate


if __name__ == "__main__":
    run_evals()