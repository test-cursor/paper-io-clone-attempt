import React from 'react';
import { GameProvider } from './contexts/GameContext';
import { GameContainer } from './components/GameContainer';
import './styles/Game.css';

function App() {
  return (
    <GameProvider>
      <GameContainer />
    </GameProvider>
  );
}

export default App; 