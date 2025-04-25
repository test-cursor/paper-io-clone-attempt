import time
from typing import Dict, Set, List
from models.game import GameState, Position, Player
from .territory import TerritoryCalculator

class GameLoop:
    def __init__(self, grid_size: int = 1000):
        self.game_state = GameState(grid_size)
        self.territory_calculator = TerritoryCalculator(grid_size)
        self.tick_rate = 30  # 30 FPS
        self.last_tick = time.time()
        self.player_movements: Dict[str, Position] = {}

    def start(self):
        """Start the game loop"""
        while True:
            current_time = time.time()
            delta_time = current_time - self.last_tick
            
            if delta_time >= 1.0 / self.tick_rate:
                self.tick()
                self.last_tick = current_time
                
            # Small sleep to prevent CPU overuse
            time.sleep(0.001)

    def tick(self):
        """Process one game tick"""
        # Update player positions
        for player_id, target_pos in self.player_movements.items():
            if player_id not in self.game_state.players:
                continue
                
            player = self.game_state.players[player_id]
            if not player.is_alive:
                continue
                
            # Calculate new position
            current_pos = player.position
            dx = target_pos.x - current_pos.x
            dy = target_pos.y - current_pos.y
            
            # Normalize movement to one cell per tick
            if dx != 0 or dy != 0:
                new_x = current_pos.x + (1 if dx > 0 else -1 if dx < 0 else 0)
                new_y = current_pos.y + (1 if dy > 0 else -1 if dy < 0 else 0)
                new_pos = Position(new_x, new_y)
                
                # Check for collisions
                if self.territory_calculator.check_collision(new_pos, self.game_state.grid, player_id):
                    # Player died
                    player.is_alive = False
                    # Clear their trail
                    for pos in player.trail:
                        self.game_state.grid[pos.x][pos.y].is_trail = False
                        self.game_state.grid[pos.x][pos.y].owner = None
                    player.trail = []
                    # Respawn player
                    self.game_state.respawn_player(player_id)
                else:
                    # Update position and trail
                    player.position = new_pos
                    player.trail.append(new_pos)
                    self.game_state.grid[new_x][new_y].is_trail = True
                    self.game_state.grid[new_x][new_y].owner = player_id
                    
                    # Check if trail is closed
                    if len(player.trail) >= 4 and self._is_trail_closed(player.trail):
                        # Calculate captured territory
                        captured = self.territory_calculator.calculate_captured_territory(
                            player.trail,
                            self.game_state.grid,
                            player_id
                        )
                        # Update player's territory
                        player.territory.extend(captured)
                        # Clear trail
                        player.trail = [player.position]
                        # Update territory percentages
                        self.game_state.update_territory_percentage()
                        
        self.game_state.last_update = time.time()

    def _is_trail_closed(self, trail: List[Position]) -> bool:
        """Check if a trail forms a closed loop"""
        if len(trail) < 4:
            return False
            
        # Check if the last position is adjacent to any previous position
        last_pos = trail[-1]
        for i in range(len(trail) - 3):  # Skip the last 3 positions
            pos = trail[i]
            if (abs(last_pos.x - pos.x) == 1 and last_pos.y == pos.y) or \
               (abs(last_pos.y - pos.y) == 1 and last_pos.x == pos.x):
                return True
        return False

    def update_player_movement(self, player_id: str, target_pos: Position):
        """Update a player's target position"""
        self.player_movements[player_id] = target_pos 