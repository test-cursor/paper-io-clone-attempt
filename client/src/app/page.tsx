"use client";

import { GameProvider } from '../contexts/GameContext';
import { GameContainer } from '../components/GameContainer';
import '../styles/Game.css';

export default function Home() {
  return (
    <GameProvider>
      <GameContainer />
    </GameProvider>
  );
}
