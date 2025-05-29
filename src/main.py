from fastapi import FastAPI
from .config import get_settings
from .routers import agent_router

settings = get_settings()

app = FastAPI(title="WhatsApp Sales Bot")

# Include the agent router
app.include_router(agent_router.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 