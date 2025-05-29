from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    customer_phone: str
    content: str
    type: Optional[str] = "text" 