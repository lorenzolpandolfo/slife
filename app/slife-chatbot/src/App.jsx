import { useState } from "react";
import "./App.css";
import Header from "./components/header/Header";
import Footer from "./components/footer/Footer";
import ChatPage from "./pages/chat/ChatPage";

function App() {
  return (
    <>
      <Header />
      <ChatPage />
    </>
  );
}

export default App;
