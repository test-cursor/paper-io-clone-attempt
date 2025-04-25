from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import uuid
import random
from core.game_loop import GameLoop
from models.game import Position, Player

class GameWebSocket:
    def __init__(self, game_loop: GameLoop):
        self.game_loop = game_loop
        self.connections: Dict[str, WebSocket] = {}
        self.colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00",
            "#FF00FF", "#00FFFF", "#FFA500", "#800080",
            "#008000", "#000080"
        ]
        self.used_colors: List[str] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        player_id = str(uuid.uuid4())
        self.connections[player_id] = websocket
        
        # Generate random username
        username = f"Player{random.randint(1000, 9999)}"
        
        # Assign unique color
        if not self.colors:
            self.colors = self.used_colors.copy()
            self.used_colors = []
        color = self.colors.pop()
        self.used_colors.append(color)
        
        # Add player to game
        self.game_loop.game_state.add_player(player_id, username, color)
        
        return player_id

    async def disconnect(self, player_id: str):
        if player_id in self.connections:
            del self.connections[player_id]
            self.game_loop.game_state.remove_player(player_id)
            
            # Return color to pool
            if player_id in self.game_loop.game_state.players:
                color = self.game_loop.game_state.players[player_id].color
                if color in self.used_colors:
                    self.used_colors.remove(color)
                    self.colors.append(color)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.connections.values():
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                continue

    async def handle_message(self, message: dict) -> dict:
        """Handle incoming messages from clients"""
        try:
            message_type = message.get("type")
            
            if message_type == "join":
                # Handle player joining
                player_id = await self.connect(message.get("websocket"))
                return {"type": "join_success", "player_id": player_id}
                
            elif message_type == "move":
                # Handle player movement
                player_id = message.get("player_id")
                if player_id in self.connections:
                    target_pos = Position(
                        x=message.get("x", 0),
                        y=message.get("y", 0)
                    )
                    self.game_loop.update_player_movement(player_id, target_pos)
                    return self._serialize_game_state()
                    
            elif message_type == "disconnect":
                # Handle player disconnection
                player_id = message.get("player_id")
                if player_id:
                    await self.disconnect(player_id)
                    return {"type": "disconnect_success"}
                    
            return {"type": "error", "message": "Invalid message type"}
            
        except Exception as e:
            return {"type": "error", "message": str(e)}

    def _serialize_game_state(self) -> dict:
        """Serialize game state for client"""
        players = {}
        for player_id, player in self.game_loop.game_state.players.items():
            players[player_id] = {
                "id": player.id,
                "username": player.username,
                "color": player.color,
                "position": {"x": player.position.x, "y": player.position.y},
                "trail": [{"x": p.x, "y": p.y} for p in player.trail],
                "territory": [{"x": p.x, "y": p.y} for p in player.territory],
                "territory_percentage": player.territory_percentage,
                "is_alive": player.is_alive
            }
            
        return {
            "players": players,
            "last_update": self.game_loop.game_state.last_update
        } 