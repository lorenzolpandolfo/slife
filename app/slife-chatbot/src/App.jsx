import { useState } from "react";
import "./App.css";
import Header from "./components/header/Header";
import Footer from "./components/footer/Footer";
import ChatPage from "./pages/chat/ChatPage";
import { MessagesProvider } from "./contexts/messages-context/MessagesContext";

function App() {
  return (
    <MessagesProvider>
      <Header />
      <ChatPage />
    </MessagesProvider>
  );
}

export default App;
