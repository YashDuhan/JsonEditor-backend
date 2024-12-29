from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

# Debug log setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the WebSocket router
websocket_router = APIRouter()

# Store active WebSocket connections
active_connections = set()

@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
   # Debug log: Connection attempt
   logger.debug("New WebSocket connection attempt")
   
   try:
       # Accept the WebSocket connection
       await websocket.accept()
       active_connections.add(websocket)
       # Debug log: Connection accepted
       logger.debug(f"WebSocket connection accepted. Total active connections: {len(active_connections)}")

       while True:
           # Receive text
           data = await websocket.receive_text()
           # Debug log: Message received
           logger.debug(f"Received message: {data}")

           # Broadcast text
           for connection in active_connections:
               try:
                   await connection.send_text(data)
                   # Debug log: Message sent
                   logger.debug(f"Message broadcast: {data}")
               except Exception as e:
                   # Debug log: Send error
                   logger.error(f"Error sending message: {e}")
                   print(f"Error sending message: {e}")

   except WebSocketDisconnect:
       # Remove the WebSocket from active connections
       active_connections.remove(websocket)
       # Debug log: Disconnection
       logger.debug(f"WebSocket disconnected. Remaining connections: {len(active_connections)}")
       print("WebSocket disconnected")
       
   except Exception as e:
       # Debug log: General error
       logger.error(f"WebSocket error occurred: {e}")
       print(f"Error: {e}")
       if websocket in active_connections:
           active_connections.remove(websocket)
           logger.debug("Cleaned up connection after error")