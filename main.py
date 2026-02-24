import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rich.console import Console
from agents.models import AgentState, SupportTicket
from agents.graph import resolveai
from langchain_core.messages import HumanMessage

app = FastAPI(
    title="ResolveAI",
    description="Multi-Agent Customer Support System powered by AWS Bedrock + LangGraph",
    version="1.0.0"
)

console = Console()


class TicketRequest(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str


class TicketResponse(BaseModel):
    ticket_id: str
    assigned_agent: str
    category: str
    priority: str
    resolution: str


@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "ResolveAI",
        "version": "1.0.0",
        "agents": ["triage", "technical", "billing", "escalation"]
    }


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(request: TicketRequest):
    ticket = SupportTicket(
        ticket_id=str(uuid.uuid4())[:8],
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        subject=request.subject,
        description=request.description
    )

    console.print(f"\n[yellow]New ticket from {request.customer_name}[/yellow]")
    console.print(f"[dim]Subject: {request.subject}[/dim]")

    initial_state = AgentState(
        messages=[HumanMessage(content=request.description)],
        ticket=ticket
    )

    try:
        result = resolveai.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return TicketResponse(
        ticket_id=ticket.ticket_id,
        assigned_agent=result.get("assigned_agent", "unknown"),
        category=result.get("category").value if result.get("category") else "unknown",
        priority=result.get("priority").value if result.get("priority") else "unknown",
        resolution=result.get("resolution", "No resolution generated")
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)