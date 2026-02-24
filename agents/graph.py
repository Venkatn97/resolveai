import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from agents.models import AgentState, TicketCategory
from agents.triage_agent import triage_node
from agents.technical_agent import technical_node
from agents.billing_agent import billing_node
from agents.escalation_agent import escalation_node

load_dotenv()

def route_ticket(state: AgentState) -> str:
    category = state.category

    if category is None:
        print(f"\n No category assigned — routing to Technical Agent (default)")
        return "technical"
    elif category == TicketCategory.TECHNICAL:
        print(f"\n Routing to Technical Agent")
        return "technical"
    elif category == TicketCategory.BILLING:
        print(f"\n Routing to Billing Agent")
        return "billing"
    elif category == TicketCategory.ESCALATION:
        print(f"\n Routing to Escalation Agent")
        return "escalation"
    else:
        print(f"\n Routing to Technical Agent (default)")
        return "technical"

def build_resolveai_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node("triage",triage_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("billing", billing_node)
    workflow.add_node("escalation", escalation_node)

    workflow.set_entry_point("triage")

    workflow.add_conditional_edges(
        "triage",
        route_ticket,
        {
            "technical": "technical",
            "billing": "billing",
            "escalation":"escalation",


        }


    )
    workflow.add_edge("technical",END)
    workflow.add_edge("billing",END)
    workflow.add_edge("escalation",END)

    return workflow.compile()

resolveai=build_resolveai_graph()

