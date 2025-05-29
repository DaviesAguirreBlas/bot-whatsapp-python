from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from ..agents.router_agent import RouterAgent
from ..schemas.agent_schema import Message
from typing import Dict, Any

router = APIRouter()

# Dummy context loader (replace with DB lookup as needed)
def get_context(customer_phone: str):
    # In production, load from DB or external service
    return {
        "store_name": "Tienda Demo",
        "user_name": "Usuario Demo",
        "user_role": "admin"
    }

@router.post("/webhook")
async def webhook(message: Message) -> Dict[str, Any]:
    try:
        context = get_context(message.customer_phone)
        agent = RouterAgent(
            customer_phone=message.customer_phone,
            store_name=context["store_name"],
            user_name=context["user_name"],
            user_role=context["user_role"]
        )
        response = await agent.process_message(message.content)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/image")
async def upload_image(
    customer_phone: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        message = Message(customer_phone=customer_phone, content=file_path, type="image")
        return await webhook(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/audio")
async def upload_audio(
    customer_phone: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        message = Message(customer_phone=customer_phone, content=file_path, type="audio")
        return await webhook(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 