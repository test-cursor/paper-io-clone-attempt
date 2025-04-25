"use client";

import React, { useState } from 'react';
import { useGame } from '../contexts/GameContext';

export const GameLobby: React.FC = () => {
  const { joinGame } = useGame();
  const [playerName, setPlayerName] = useState('');

  const handleJoin = (e: React.FormEvent) => {
    e.preventDefault();
    if (playerName.trim()) {
      joinGame(playerName.trim());
    }
  };

  return (
    <div className="game-lobby">
      <h2>Join Game</h2>
      <form onSubmit={handleJoin}>
        <input
          type="text"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          placeholder="Enter your name"
          maxLength={20}
        />
        <button type="submit" disabled={!playerName.trim()}>
          Join Game
        </button>
      </form>
    </div>
  );
}; 