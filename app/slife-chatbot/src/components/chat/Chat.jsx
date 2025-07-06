import { useMessages } from "../../contexts/messages-context/MessagesContext";
import "./chat-content.css";
import ChatMessage from "./chat-message/ChatMessage";
import InputChat from "./input-chat/InputChat";

export default function Chat() {
  const { messages } = useMessages();

  return (
    <>
      <div className="chat-content chat-content-container">
        {messages &&
          messages.map((msg, index) => (
            <ChatMessage
              key={index}
              content={msg.content}
              fromUser={msg.role === "user"}
            />
          ))}
      </div>
      <InputChat />
    </>
  );
}
