import { useEffect, useState } from "react";
import { useMessages } from "../../../contexts/messages-context/MessagesContext";
import "./input-chat.css";
import api from "../../../api/axios";

export default function InputChat() {
  const [message, setMessage] = useState("");
  const { setMessages, clearMessages, messages } = useMessages();

  const sendWelcomeMessage = () => {
    clearMessages();
    addGhostMessage(
      "Olá, bem vindo ao atendimento automatizado da S4Life! Para iniciar a conversa, envie uma mensagem.",
      "assistant"
    );
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  useEffect(() => {
    const history = loadChatHistory();
    if (!history) {
      sendWelcomeMessage();
    }
  }, []);

  const getChatToken = async () => {
    const token = localStorage.getItem("chat-token");
    if (token) return token;

    const res = await api.get("/start");

    if (res.status !== 200) {
      console.error("Error fetching chat token:", res);
      return null;
    }
    localStorage.setItem("chat-token", res.data.token);
    return res.data.token;
  };

  const loadChatHistory = () => {
    const history = localStorage.getItem("chat-history");
    if (history) {
      try {
        const parsedHistory = JSON.parse(history);
        setMessages(parsedHistory);
        return true;
      } catch (e) {
        setMessages([]);
        return false;
      }
    }
  };

  const sendMessage = async () => {
    if (!message || !message.trim()) return;

    handleGhostMessagesOnSend();
    setMessage("");

    try {
      const token = await getChatToken();

      const response = await api.post("/chat/", {
        message: message.trim(),
        token,
      });
      setMessages(response.data.messages);
      localStorage.setItem(
        "chat-history",
        JSON.stringify(response.data.messages)
      );
    } catch (error) {
      handleClearMessages();
    }
  };

  const handleGhostMessagesOnSend = () => {
    addGhostMessage(message, "user");
    addGhostMessage("...", "assistant", true);
  };

  const addGhostMessage = (content, role, writing) => {
    if (!content || !role) return;
    setMessages((prevMessages) => [
      ...prevMessages,
      { content: content, role: role, ghost: true, writing: writing },
    ]);
  };

  const handleClearMessages = () => {
    clearMessages();
    localStorage.removeItem("chat-token");
    localStorage.removeItem("chat-history");
    sendWelcomeMessage();
  };

  return (
    <>
      <button
        type="button"
        className="new-chat-button circular-button"
        title="Criar nova conversa"
        onClick={handleClearMessages}
      >
        <img src="src/assets/new_chat.svg" alt="New Chat" />
      </button>
      <div className="input-chat">
        <input
          type="text"
          name="msg-input"
          id="msg-input"
          placeholder="Digite a sua mensagem..."
          onChange={(e) => setMessage(e.target.value)}
          value={message}
          onKeyDown={handleKeyDown}
        />
        <button
          type="button"
          className="send-button circular-button"
          onClick={sendMessage}
        >
          <img src="src/assets/send.svg" alt="send button" />
        </button>
      </div>
    </>
  );
}
