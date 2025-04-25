"use client";

import React, { useState, useEffect } from 'react';
import { GameLobby } from './GameLobby';
import { GameBoard } from './GameBoard';
import { useGame } from '../contexts/GameContext';
import { initializeSocket } from '../utils/socket';

export const GameContainer: React.FC = () => {
  const { gameState, currentPlayer } = useGame();
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = initializeSocket();
    
    socket.onopen = () => {
      setIsConnected(true);
    };

    socket.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      socket.onopen = null;
      socket.onclose = null;
    };
  }, []);

  if (!isConnected) {
    return (
      <div className="game-container">
        <div className="connection-status">
          Connecting to server...
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      {!currentPlayer ? (
        <GameLobby />
      ) : (
        <GameBoard />
      )}
    </div>
  );
}; 