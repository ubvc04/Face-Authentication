import { createContext, useContext, useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import toast from 'react-hot-toast';

const SocketContext = createContext();

export function SocketProvider({ children }) {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Initialize socket connection
    const socketInstance = io(process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000', {
      withCredentials: true,
      transports: ['websocket', 'polling'],
    });

    setSocket(socketInstance);

    // Connection event handlers
    socketInstance.on('connect', () => {
      console.log('Connected to WebSocket server');
      setConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
      setConnected(false);
    });

    socketInstance.on('connected', (data) => {
      console.log('WebSocket authentication successful:', data);
    });

    // Notification handlers
    socketInstance.on('notification', (data) => {
      handleNotification(data);
    });

    socketInstance.on('user_login', (data) => {
      toast.success(`🎉 Welcome back! Login detected at ${new Date(data.login_time).toLocaleTimeString()}`);
    });

    socketInstance.on('user_logout', (data) => {
      console.log('User logout detected:', data);
    });

    // Error handler
    socketInstance.on('error', (data) => {
      console.error('Socket error:', data);
      toast.error(data.message || 'Connection error');
    });

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  const handleNotification = (notification) => {
    const { type, message, timestamp } = notification;
    
    console.log('Received notification:', notification);
    
    switch (type) {
      case 'success':
        toast.success(message);
        break;
      case 'error':
        toast.error(message);
        break;
      case 'warning':
        toast(message, {
          icon: '⚠️',
          style: {
            background: '#f59e0b',
            color: '#fff',
          },
        });
        break;
      case 'info':
        toast(message, {
          icon: 'ℹ️',
          style: {
            background: '#3b82f6',
            color: '#fff',
          },
        });
        break;
      default:
        toast(message);
    }
  };

  const joinNotifications = () => {
    if (socket) {
      socket.emit('join_notifications');
    }
  };

  const ping = () => {
    if (socket) {
      socket.emit('ping');
    }
  };

  const value = {
    socket,
    connected,
    joinNotifications,
    ping,
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
}