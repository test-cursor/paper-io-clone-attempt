# Paper.io Clone Implementation Plan

## 1. Project Structure

```
paper-io-clone/
├── client/                 # Next.js frontend
│   ├── components/         # React components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Client-side utilities
│   ├── pages/             # Next.js pages
│   └── styles/            # CSS/SCSS files
├── server/                # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core game logic
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── shared/                # Shared types and constants
│   ├── types/             # TypeScript interfaces
│   └── constants/         # Game constants
└── tests/                 # Test suite
    ├── client/            # Frontend tests
    └── server/            # Backend tests
```

## 2. Core Components

### 2.1 Game State Management

```python
# server/models/game.py
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

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
    territory: List[Position]  # List of owned positions
    territory_percentage: float
    is_alive: bool

class GameState:
    def __init__(self, grid_size: int):
        self.players: Dict[str, Player] = {}
        self.grid: List[List[Optional[str]]] = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.grid_size = grid_size
        self.last_update: float = 0.0

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
```

### 2.2 Territory Calculation

```python
# server/core/territory.py
from collections import deque
from typing import Set, Tuple, List, Dict
from dataclasses import dataclass

@dataclass
class GridCell:
    owner: Optional[str] = None
    is_trail: bool = False

class TerritoryCalculator:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.visited: Dict[Tuple[Position, Direction], bool] = {}
        
    def calculate_captured_territory(
        self,
        trail: List[Position],
        grid: List[List[GridCell]]
    ) -> Set[Position]:
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
                grid[position.x][position.y].owner = trail[0].owner
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
        return all(
            self.visited.get((position, direction), False)
            for direction in Direction
        )
    
    def _get_next_position(self, position: Position, direction: Direction) -> Position:
        if direction == Direction.LEFT:
            return Position(position.x - 1, position.y)
        elif direction == Direction.RIGHT:
            return Position(position.x + 1, position.y)
        elif direction == Direction.UP:
            return Position(position.x, position.y - 1)
        else:  # DOWN
            return Position(position.x, position.y + 1)
    
    def _is_out_of_bounds(self, position: Position) -> bool:
        # Implement circular boundary check
        radius = self.grid_size // 2
        center = Position(radius, radius)
        distance = ((position.x - center.x) ** 2 + (position.y - center.y) ** 2) ** 0.5
        return distance > radius

    def check_collision(self, position: Position, grid: List[List[GridCell]]) -> bool:
        """Check if position collides with any trail"""
        cell = grid[position.x][position.y]
        return cell.is_trail and cell.owner != position.owner
```

### 2.2 Game Loop Implementation

```typescript
// server/core/game_loop.ts
class GameLoop {
  private readonly TICK_RATE = 30;
  private gameState: GameState;
  private lastTick: number;

  constructor() {
    this.gameState = this.initializeGameState();
    this.lastTick = Date.now();
  }

  public start(): void {
    setInterval(() => this.tick(), 1000 / this.TICK_RATE);
  }

  private tick(): void {
    const now = Date.now();
    const delta = now - this.lastTick;
    this.lastTick = now;

    this.updatePlayerPositions(delta);
    this.updateTerritory();
    this.broadcastGameState();
  }
}
```

## 3. Implementation Phases

### Phase 1: Core Infrastructure
1. Set up Next.js project with TypeScript
2. Set up FastAPI backend with WebSocket support
3. Implement basic project structure
4. Set up testing framework (Jest for frontend, pytest for backend)

### Phase 2: Game Logic
1. Implement grid-based territory system
2. Create player movement and trail system
3. Implement territory capture algorithm
4. Add player joining/leaving logic

### Phase 3: Networking
1. Implement WebSocket communication
2. Create state synchronization system
3. Add reconnection handling
4. Implement basic error handling

### Phase 4: Frontend
1. Create Three.js game canvas
2. Implement player rendering
3. Add territory visualization
4. Create minimap and leaderboard

### Phase 5: Polish
1. Add visual feedback
2. Implement proper logging
3. Add performance optimizations
4. Write comprehensive tests

## 4. Key Implementation Details

### 4.1 Territory Calculation
```typescript
// server/core/territory.ts
class TerritoryCalculator {
  public calculateCapturedTerritory(
    trail: Trail,
    grid: TerritoryGrid
  ): TerritoryUpdate {
    const visited = new Set<string>();
    const captured = new Set<string>();
    
    // Multi-source BFS implementation
    const queue = trail.getEndpoints();
    
    while (queue.length > 0) {
      const current = queue.shift()!;
      const key = this.getCellKey(current);
      
      if (visited.has(key)) continue;
      visited.add(key);
      
      // Check if cell is captured by all directions
      if (this.isFullyEnclosed(current, grid)) {
        captured.add(key);
      }
      
      // Add neighbors to queue
      this.getNeighbors(current).forEach(neighbor => {
        if (!visited.has(this.getCellKey(neighbor))) {
          queue.push(neighbor);
        }
      });
    }
    
    return { captured: Array.from(captured) };
  }
}
```

### 4.2 WebSocket Communication
```typescript
// server/api/websocket.py
class GameWebSocket:
    def __init__(self, game_loop: GameLoop):
        self.game_loop = game_loop
        self.connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.connections[player_id] = websocket
        
    async def broadcast(self, message: GameState):
        for connection in self.connections.values():
            await connection.send_json(message)
```

### 4.3 Client-Side Rendering
```typescript
// client/components/GameCanvas.tsx
class GameCanvas extends React.Component {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  
  componentDidMount() {
    this.setupThreeJS();
    this.animate();
  }
  
  private animate = () => {
    requestAnimationFrame(this.animate);
    this.renderer.render(this.scene, this.camera);
  }
}
```

## 5. Testing Strategy

### 5.1 Unit Tests
- Territory calculation with multi-directional BFS
- Player movement and collision detection
- Grid operations
- WebSocket communication
- Circular boundary handling
- Player respawn logic
- Trail intersection detection

### 5.2 Integration Tests
- Game loop with death conditions
- State synchronization
- Territory capture scenarios
- Player interactions including deaths
- WebSocket protocol compliance
- Respawn mechanics

### 5.3 Performance Tests
- Territory calculation benchmarks
- WebSocket message throughput
- Rendering performance
- Memory usage

## 6. Logging Strategy

```python
# server/utils/logger.py
class GameLogger:
    def __init__(self):
        self.logger = logging.getLogger('game')
        self.setup_logging()
        
    def setup_logging(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def log_game_event(self, event: GameEvent):
        self.logger.info(f"Game Event: {event.type} - {event.details}")
```

## 7. Performance Considerations

1. Use efficient data structures for territory grid
2. Implement spatial partitioning for player updates
3. Optimize WebSocket message size
4. Use object pooling for Three.js objects
5. Implement efficient territory update algorithm
6. Use WebGL for rendering
7. Implement client-side prediction for smooth movement

## 8. Code Reuse Strategy

1. Create shared types and interfaces
2. Implement utility functions for common operations
3. Use composition over inheritance
4. Create reusable React components
5. Implement generic grid operations
6. Create shared math utilities
7. Use dependency injection for services

## 9. Error Handling

1. Implement graceful degradation
2. Add proper error boundaries in React
3. Handle WebSocket disconnections
4. Implement retry mechanisms
5. Add proper error logging
6. Handle edge cases in territory calculation
7. Implement proper cleanup on component unmount

## 10. Monitoring

1. Track player count
2. Monitor territory calculation time
3. Track WebSocket message latency
4. Monitor memory usage
5. Track error rates
6. Monitor frame rate
7. Track territory update frequency

## 11. Game Rules Implementation

### 11.1 Death Conditions
1. Player collides with another player's trail
2. Player moves outside the circular boundary
3. Player's connection drops (after 1 minute of inactivity)

### 11.2 Respawn Rules
1. Player respawns at random position within their territory
2. If player has no territory, spawn at random valid position
3. Player starts with empty trail at respawn position
4. Player's territory remains unchanged after death

### 11.3 Territory Rules
1. Territory is captured when trail forms a closed loop
2. Territory is calculated using multi-directional BFS
3. Territory ownership is immediate upon calculation
4. Territory remains owned until captured by another player
5. No special handling for self-intersecting trails
