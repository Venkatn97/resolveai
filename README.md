# ResolveAI — Multi-Agent Customer Support System

> Production-grade AI customer support system that automatically triages, routes, and resolves support tickets using specialized agents. Built with LangGraph, AWS Bedrock Claude Sonnet, and FastAPI. Deployed on AWS ECS Fargate.

---

## The Problem

TechFlow SaaS was drowning in support tickets. Their single support team handled everything from billing questions to critical API outages — with no intelligent routing, no priority system, and slow resolution times.

**Result with ResolveAI:**
- Tickets routed to the right specialist in seconds
- Technical issues resolved with GitHub bug search and Jira tracking
- Billing issues handled with automatic status checks
- Critical escalations trigger immediate Slack alerts
- 100% automated resolution with no human intervention needed

---

## Architecture

```
Customer submits ticket (POST /tickets)
          │
          ▼
    Triage Agent
    (classifies category and priority)
          │
    ┌─────┼─────────┐
    ▼     ▼         ▼
Technical  Billing  Escalation
 Agent     Agent     Agent
    │        │          │
    └────────┴──────────┘
             │
             ▼
    Tools (Jira, Slack, GitHub, Email, Billing)
             │
             ▼
    JSON Resolution Response
```

---

## Agents

**Triage Agent**
Reads every incoming ticket and classifies it by category (technical, billing, escalation) and priority (low, medium, high, critical). Routes to the correct specialist agent.

**Technical Agent**
Handles API issues, bugs, errors, webhook problems, and SDK integration issues. Searches GitHub for known bugs, creates Jira tickets, notifies engineering on Slack, and sends resolution emails.

**Billing Agent**
Handles payments, refunds, subscription changes, and invoice questions. Checks billing status, creates Jira tickets, and sends resolution emails. Escalates to Slack for refunds over $500.

**Escalation Agent**
Handles angry customers, legal threats, critical outages, and churn risk. Immediately notifies multiple Slack channels, creates P0 Jira tickets, checks billing history, and sends a personal response with executive-level follow-up.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph |
| AI Model | AWS Bedrock Claude Sonnet |
| API | FastAPI + Uvicorn |
| Data Validation | Pydantic V2 |
| Mock Tools | Jira, Slack, GitHub, SendGrid, Stripe |
| Deployment | Docker + AWS ECR + ECS Fargate |
| Monitoring | AWS CloudWatch |

---

## Project Structure

```
resolveai/
├── agents/
│   ├── __init__.py
│   ├── models.py          # Pydantic models — SupportTicket, AgentState
│   ├── graph.py           # LangGraph multi-agent graph and routing
│   ├── triage_agent.py    # Classifies and routes tickets
│   ├── technical_agent.py # Handles technical issues
│   ├── billing_agent.py   # Handles billing issues
│   └── escalation_agent.py # Handles critical escalations
├── tools/
│   ├── __init__.py
│   └── mock_tools.py      # Mock Jira, Slack, GitHub, Email, Billing tools
├── evals/
│   ├── __init__.py
│   └── test_cases.py      # 8 automated test cases
├── main.py                # FastAPI app with /tickets endpoint
├── Dockerfile             # Production container
├── .dockerignore
└── requirements.txt
```

---

## API Endpoints

**Health Check**
```
GET /
```
```json
{
  "status": "online",
  "service": "ResolveAI",
  "version": "1.0.0",
  "agents": ["triage", "technical", "billing", "escalation"]
}
```

**Create Ticket**
```
POST /tickets
```
```json
{
  "customer_name": "John Smith",
  "customer_email": "john@acme.com",
  "subject": "API returning 429 errors",
  "description": "Our integration keeps getting rate limited..."
}
```
```json
{
  "ticket_id": "3c48a4d0",
  "assigned_agent": "technical_agent",
  "category": "technical",
  "priority": "high",
  "resolution": "Full resolution with Jira ticket, GitHub issue found, email sent..."
}
```

**Interactive Docs**
```
GET /docs
```
Full Swagger UI for testing all endpoints.

---

## Local Development

**Prerequisites:**
- Python 3.11+
- AWS account with Bedrock access
- Docker

**Setup:**
```bash
git clone https://github.com/Venkatn97/resolveai
cd resolveai
pip install -r requirements.txt
```

Create `.env`:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_REGION=us-east-1
```

**Run locally:**
```bash
python main.py
```

Visit `http://localhost:8000/docs` for Swagger UI.

---

## Running Evals

```bash
python evals/test_cases.py
```

**Results: 8/8 passed (100%)**

| Test | Status | Category | Agent |
|---|---|---|---|
| API Rate Limiting | PASS | technical | technical_agent |
| Webhook Not Working | PASS | technical | technical_agent |
| Duplicate Charge | PASS | billing | billing_agent |
| Subscription Upgrade | PASS | billing | billing_agent |
| Legal Threat | PASS | escalation | escalation_agent |
| Angry Customer | PASS | escalation | escalation_agent |
| Auth Token Issue | PASS | technical | technical_agent |
| Invoice Question | PASS | billing | billing_agent |

---

## Deployment

**Build and push Docker image:**
```bash
docker build -t resolveai .
docker tag resolveai:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/resolveai:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/resolveai:latest
```

**Deploy to ECS Fargate:**
1. Create ECS cluster with Fargate
2. Create task definition with ECR image URI and environment variables
3. Create service with desired count 1
4. Open port 8000 in security group
5. Access via public IP on port 8000

---

## Example Resolutions

**Technical — API Rate Limiting:**
```
Found GitHub issue #1234 — rate limiting bug fixed in v2.3.1
Created Jira ticket JIRA-DVSVRP (High Priority)
Notified #engineering on Slack
Sent resolution email with upgrade instructions
```

**Billing — Duplicate Charge:**
```
Checked billing status — Pro plan active
Created Jira ticket JIRA-H08W0Z (High Priority)
Processed $99 refund within 5-7 business days
Sent resolution email to customer
```

**Escalation — Legal Threat:**
```
Notified #escalations and #engineering on Slack (Critical)
Created P0 Jira ticket
Checked billing — $5000/month contract verified
Sent personal response with 30-minute update cadence
Offered full month credit + additional compensation
```

---

## Roadmap

- [ ] Real Jira API integration
- [ ] Real Slack webhook integration
- [ ] Real Stripe billing API
- [ ] Redis shared memory between agents
- [ ] PostgreSQL ticket history
- [ ] LangSmith tracing and observability
- [ ] GitHub Actions CI/CD pipeline
- [ ] HTTPS via AWS ALB

---

## Built By

Built as a Forward Deployed Engineer portfolio project demonstrating multi-agent AI system design and deployment.

**Skills demonstrated:** LangGraph multi-agent orchestration, AWS Bedrock, agent routing, tool calling, FastAPI, Docker, ECS Fargate, Pydantic, automated evals