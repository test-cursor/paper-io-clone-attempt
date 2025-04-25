export interface Position {
  x: number;
  y: number;
}

export interface Player {
  id: string;
  name: string;
  position: Position;
  color: string;
  trail: Position[];
  score: number;
}

export interface GameState {
  players: Player[];
  grid: number[][];
  width: number;
  height: number;
} 