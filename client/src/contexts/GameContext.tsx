import React, { createContext, useContext, useEffect, useState } from 'react';
import { initializeSocket, getSocket, disconnectSocket, sendMessage } from '../utils/socket';
import { GameState, Player } from '../types/game';

interface GameContextType {
  gameState: GameState | null;
  currentPlayer: Player | null;
  joinGame: (playerName: string) => void;
  movePlayer: (direction: 'up' | 'down' | 'left' | 'right') => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export const GameProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [currentPlayer, setCurrentPlayer] = useState<Player | null>(null);

  useEffect(() => {
    const socket = initializeSocket();

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'gameState':
          setGameState(data.state);
          break;
        case 'playerJoined':
          setCurrentPlayer(data.player);
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    };

    return () => {
      disconnectSocket();
    };
  }, []);

  const joinGame = (playerName: string) => {
    sendMessage({
      type: 'joinGame',
      name: playerName
    });
  };

  const movePlayer = (direction: 'up' | 'down' | 'left' | 'right') => {
    sendMessage({
      type: 'movePlayer',
      direction
    });
  };

  return (
    <GameContext.Provider value={{ gameState, currentPlayer, joinGame, movePlayer }}>
      {children}
    </GameContext.Provider>
  );
};

export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}; 