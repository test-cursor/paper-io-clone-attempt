interface GameMessage {
  type: 'join' | 'move' | 'disconnect';
  player_id?: string;
  x?: number;
  y?: number;
  websocket?: WebSocket;
}

let socket: WebSocket | null = null;

export const initializeSocket = () => {
  if (!socket) {
    socket = new WebSocket('ws://localhost:8000/ws');
    
    socket.onopen = () => {
      console.log('WebSocket connection established');
      // Send join message when connection is established
      sendMessage({ type: 'join' });
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
      socket = null;
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      socket = null;
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };
  }
  return socket;
};

export const getSocket = () => {
  if (!socket) {
    throw new Error('Socket not initialized');
  }
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    sendMessage({ type: 'disconnect' });
    socket.close();
    socket = null;
  }
};

export const sendMessage = (message: GameMessage) => {
  const socket = getSocket();
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.error('WebSocket is not open');
  }
};

export const sendMoveMessage = (x: number, y: number) => {
  sendMessage({
    type: 'move',
    x,
    y
  });
}; 