import { createContext, useContext, useState } from "react";

const MessagesContext = createContext();

export function useMessages() {
  return useContext(MessagesContext);
}

export function MessagesProvider({ children }) {
  const [messages, setMessages] = useState([]);

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <MessagesContext.Provider value={{ messages, setMessages, clearMessages }}>
      {children}
    </MessagesContext.Provider>
  );
}
