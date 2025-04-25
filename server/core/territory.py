from collections import deque
from typing import Set, List, Dict, Tuple
from dataclasses import dataclass
from models.game import Position, Direction, GridCell

class TerritoryCalculator:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.visited: Dict[Tuple[Position, Direction], bool] = {}
        
    def calculate_captured_territory(
        self,
        trail: List[Position],
        grid: List[List[GridCell]],
        player_id: str
    ) -> Set[Position]:
        """Calculate territory captured by a closed trail"""
        # Reset visited state
        self.visited.clear()
        
        # Initialize queue with trail endpoints
        queue = deque()
        for position in trail:
            for direction in Direction:
                queue.append((position, direction))
                self.visited[(position, direction)] = True
        
        captured = set()
        
        while queue:
            position, direction = queue.popleft()
            
            # Check if cell is fully enclosed
            if self._is_fully_enclosed(position):
                captured.add(position)
                # Mark as owned immediately
                grid[position.x][position.y].owner = player_id
                grid[position.x][position.y].is_trail = False
            
            # Get next position based on direction
            next_pos = self._get_next_position(position, direction)
            
            # Skip if out of bounds or already visited in this direction
            if (next_pos, direction) in self.visited or self._is_out_of_bounds(next_pos):
                continue
                
            self.visited[(next_pos, direction)] = True
            queue.append((next_pos, direction))
            
        return captured
    
    def _is_fully_enclosed(self, position: Position) -> bool:
        """Check if a position has been visited from all directions"""
        return all(
            self.visited.get((position, direction), False)
            for direction in Direction
        )
    
    def _get_next_position(self, position: Position, direction: Direction) -> Position:
        """Get the next position based on direction"""
        if direction == Direction.LEFT:
            return Position(position.x - 1, position.y)
        elif direction == Direction.RIGHT:
            return Position(position.x + 1, position.y)
        elif direction == Direction.UP:
            return Position(position.x, position.y - 1)
        else:  # DOWN
            return Position(position.x, position.y + 1)
    
    def _is_out_of_bounds(self, position: Position) -> bool:
        """Check if position is outside the circular boundary"""
        radius = self.grid_size // 2
        center = Position(radius, radius)
        distance = ((position.x - center.x) ** 2 + (position.y - center.y) ** 2) ** 0.5
        return distance > radius

    def check_collision(self, position: Position, grid: List[List[GridCell]], player_id: str) -> bool:
        """Check if position collides with any trail"""
        # Check if position is out of bounds
        if self._is_out_of_bounds(position):
            return True
            
        cell = grid[position.x][position.y]
        # Collision if cell is a trail and not owned by the player
        return cell.is_trail and cell.owner != player_id 