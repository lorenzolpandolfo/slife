import { useEffect, useState } from "react";
import { useMessages } from "../../../contexts/messages-context/MessagesContext";
import "./input-chat.css";
import api from "../../../api/axios";

export default function InputChat() {
  const [message, setMessage] = useState("");
  const { setMessages, clearMessages, messages } = useMessages();

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  useEffect(() => {
    loadChatHistory();
  }, []);

  const getChatToken = async () => {
    const token = localStorage.getItem("chat-token");
    if (token) return token;

    const res = await api.get("/start");

    if (res.status !== 200) {
      console.error("Error fetching chat token:", res);
      return null;
    }
    console.log("Chat token received:", res.data.token);
    localStorage.setItem("chat-token", res.data.token);
    return res.data.token;
  };

  const loadChatHistory = () => {
    const history = localStorage.getItem("chat-history");
    if (history) {
      try {
        const parsedHistory = JSON.parse(history);
        setMessages(parsedHistory);
      } catch (e) {
        setMessages([]);
      }
    }
  };

  const sendMessage = async () => {
    console.log("enviando mensagem:", message);
    setMessage("");

    if (!message.trim()) return;

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
    } finally {
      // scrollar o chat para o final
    }
  };

  const handleClearMessages = () => {
    clearMessages();
    localStorage.removeItem("chat-token");
  };

  return (
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
      <button type="button" className="send-button">
        <img src="src/assets/send.svg" alt="send button" />
      </button>
    </div>
  );
}
