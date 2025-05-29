from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from .agents.general_agent import GeneralAgent
from .config import get_settings

settings = get_settings()

app = FastAPI(title="WhatsApp Sales Bot")

class Message(BaseModel):
    customer_phone: str
    content: str
    type: str = "text"

@app.post("/webhook")
async def webhook(message: Message) -> Dict[str, Any]:
    """Process incoming WhatsApp messages."""
    try:
        agent = GeneralAgent(message.customer_phone)
        response = await agent.process_message(message.content)
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/image")
async def upload_image(
    customer_phone: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Handle image uploads for OCR processing."""
    try:
        # Save file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process image as a message
        message = Message(
            customer_phone=customer_phone,
            content=file_path,
            type="image"
        )
        
        return await webhook(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/audio")
async def upload_audio(
    customer_phone: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Handle audio uploads for transcription."""
    try:
        # Save file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process audio as a message
        message = Message(
            customer_phone=customer_phone,
            content=file_path,
            type="audio"
        )
        
        return await webhook(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 