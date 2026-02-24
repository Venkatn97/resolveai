from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import operator
from typing import Annotated
from langchain_core.messages import BaseMessage

class TicketCategory(str,Enum):
    TECHNICAL="technical"
    BILLING="billing"
    ESCALATION="escalation"
    GENERAL="general"

class TicketPriority(str,Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    CRITICAL="critical"

class SupportTicket(BaseModel):
    ticket_id:str
    customer_name:str
    customer_email:str
    subject:str 
    description: str 
    category: Optional[TicketCategory]=None
    priority: Optional[TicketPriority]=None 

class AgentState(BaseModel):
    class Config:
        arbitrary_types_allowed= True
    messages: Annotated[List[BaseMessage],operator.add]
    ticket: SupportTicket
    category: Optional[TicketCategory]=None
    priority: Optional[TicketPriority]=None 

    assigned_agent: Optional[str]=None
    resolution : Optional[str] =None
    