from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import json
from core.game_loop import GameLoop
from api.websocket import GameWebSocket

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize game components
game_loop = GameLoop()
game_websocket = GameWebSocket(game_loop)

# Store active connections
active_connections: set[WebSocket] = set()

@app.on_event("startup")
async def startup_event():
    # Start game loop in a separate thread
    game_thread = threading.Thread(target=game_loop.start)
    game_thread.daemon = True
    game_thread.start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process the received data
            message = json.loads(data)
            # Handle the message through game_websocket
            response = await game_websocket.handle_message(message)
            if response:
                await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"Error in websocket connection: {e}")
        active_connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 