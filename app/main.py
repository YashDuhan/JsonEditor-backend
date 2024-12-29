from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import app_router
from .api.websocket import websocket_router

app = FastAPI(title="Json Editor API")

# allow requests from all origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(app_router)
app.include_router(websocket_router)

# Default route
@app.get("/")
def root():
    return {"message" : "Welcome to the backend"}