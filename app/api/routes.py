from fastapi import APIRouter
from .endpoints import ask_ai, push_logs, fetch_logs
from .websocket import websocket_router

app_router = APIRouter()

# Include websocket
app_router.include_router(websocket_router)

# Push Logs
app_router.post("/push")(push_logs)

# Fetch Code
app_router.get("/fetch")(fetch_logs)

# Ask AI
app_router.post("/ask")(ask_ai)

