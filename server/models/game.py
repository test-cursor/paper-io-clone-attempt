from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Player:
    id: str
    username: str
    color: str
    position: Position
    trail: List[Position]
    territory: List[Position]
    territory_percentage: float
    is_alive: bool

@dataclass
class GridCell:
    owner: Optional[str] = None
    is_trail: bool = False

class GameState:
    def __init__(self, grid_size: int):
        self.players: Dict[str, Player] = {}
        self.grid: List[List[GridCell]] = [[GridCell() for _ in range(grid_size)] for _ in range(grid_size)]
        self.grid_size = grid_size
        self.last_update: float = 0.0

    def add_player(self, player_id: str, username: str, color: str) -> None:
        """Add a new player to the game"""
        x = random.randint(0, self.grid_size - 1)
        y = random.randint(0, self.grid_size - 1)
        position = Position(x, y)
        
        self.players[player_id] = Player(
            id=player_id,
            username=username,
            color=color,
            position=position,
            trail=[position],
            territory=[],
            territory_percentage=0.0,
            is_alive=True
        )
        
        # Mark initial position as trail
        self.grid[x][y].is_trail = True
        self.grid[x][y].owner = player_id

    def respawn_player(self, player_id: str) -> None:
        """Respawn player at a random position within their territory"""
        player = self.players[player_id]
        if not player.territory:
            # If no territory, spawn at random position
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
        else:
            # Spawn within owned territory
            spawn_pos = random.choice(player.territory)
            x, y = spawn_pos.x, spawn_pos.y
            
        player.position = Position(x, y)
        player.trail = [player.position]
        player.is_alive = True
        
        # Mark new position as trail
        self.grid[x][y].is_trail = True
        self.grid[x][y].owner = player_id

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the game and make their territory neutral"""
        if player_id in self.players:
            # Make all territory neutral
            for pos in self.players[player_id].territory:
                self.grid[pos.x][pos.y].owner = None
                self.grid[pos.x][pos.y].is_trail = False
                
            # Remove player
            del self.players[player_id]

    def update_territory_percentage(self) -> None:
        """Update territory percentage for all players"""
        total_cells = self.grid_size * self.grid_size
        for player in self.players.values():
            player.territory_percentage = len(player.territory) / total_cells * 100 