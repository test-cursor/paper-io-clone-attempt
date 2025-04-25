"use client";

import React, { useEffect, useRef, useState } from 'react';
import { useGame } from '../contexts/GameContext';
import * as THREE from 'three';
import { initializeSocket, sendMoveMessage } from '../utils/socket';

export const GameBoard: React.FC = () => {
  const { gameState, currentPlayer, movePlayer } = useGame();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const [socketInitialized, setSocketInitialized] = useState(false);

  useEffect(() => {
    if (!socketInitialized) {
      initializeSocket();
      setSocketInitialized(true);
    }
  }, [socketInitialized]);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    
    // Set up camera
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 10);
    camera.lookAt(0, 0, 0);

    // Set up renderer
    const renderer = new THREE.WebGLRenderer({ 
      canvas: canvasRef.current,
      antialias: true 
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    // Add grid helper
    const gridHelper = new THREE.GridHelper(20, 20);
    scene.add(gridHelper);

    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;

    // Handle window resize
    const handleResize = () => {
      if (!cameraRef.current || !rendererRef.current) return;
      
      cameraRef.current.aspect = window.innerWidth / window.innerHeight;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    // Handle keyboard input
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!currentPlayer) return;

      const moveAmount = 0.5;
      let newX = currentPlayer.position.x;
      let newY = currentPlayer.position.y;

      switch (e.key) {
        case 'ArrowUp':
          movePlayer('up');
          newY += moveAmount;
          break;
        case 'ArrowDown':
          movePlayer('down');
          newY -= moveAmount;
          break;
        case 'ArrowLeft':
          movePlayer('left');
          newX -= moveAmount;
          break;
        case 'ArrowRight':
          movePlayer('right');
          newX += moveAmount;
          break;
        default:
          return;
      }

      sendMoveMessage(newX, newY);
    };

    window.addEventListener('keydown', handleKeyDown);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('keydown', handleKeyDown);
      
      // Clean up Three.js resources
      if (sceneRef.current) {
        sceneRef.current.traverse((object) => {
          if (object instanceof THREE.Mesh) {
            object.geometry.dispose();
            if (Array.isArray(object.material)) {
              object.material.forEach(material => material.dispose());
            } else {
              object.material.dispose();
            }
          }
        });
      }
      
      sceneRef.current = null;
      cameraRef.current = null;
      rendererRef.current = null;
    };
  }, [currentPlayer, movePlayer]);

  // Update game objects when game state changes
  useEffect(() => {
    if (!sceneRef.current || !gameState) return;

    // Clear existing objects
    while (sceneRef.current.children.length > 0) {
      const child = sceneRef.current.children[0];
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose();
        if (Array.isArray(child.material)) {
          child.material.forEach(material => material.dispose());
        } else {
          child.material.dispose();
        }
      }
      sceneRef.current.remove(child);
    }

    // Add game objects based on game state
    Object.values(gameState.players).forEach(player => {
      // Player cube
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const material = new THREE.MeshPhongMaterial({ 
        color: player.color,
        shininess: 100 
      });
      const cube = new THREE.Mesh(geometry, material);
      cube.position.set(player.position.x, player.position.y, 0);
      sceneRef.current?.add(cube);

      // Player trail
      player.trail.forEach((position, index) => {
        const trailGeometry = new THREE.BoxGeometry(1, 1, 0.1);
        const trailMaterial = new THREE.MeshPhongMaterial({ 
          color: player.color,
          transparent: true,
          opacity: 0.5
        });
        const trailCube = new THREE.Mesh(trailGeometry, trailMaterial);
        trailCube.position.set(position.x, position.y, -0.1);
        sceneRef.current?.add(trailCube);
      });
    });
  }, [gameState]);

  return (
    <div className="game-board" style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <canvas 
        ref={canvasRef} 
        style={{ 
          width: '100%', 
          height: '100%',
          display: 'block'
        }} 
      />
      <div className="game-info" style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        background: 'rgba(0, 0, 0, 0.5)',
        color: 'white',
        padding: '10px',
        borderRadius: '5px'
      }}>
        {currentPlayer && (
          <>
            <div>Player: {currentPlayer.id}</div>
            <div>Score: {currentPlayer.score}</div>
          </>
        )}
      </div>
    </div>
  );
}; 