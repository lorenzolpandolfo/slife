import { useEffect, useRef } from "react";
import { useMessages } from "../../contexts/messages-context/MessagesContext";
import "./chat-content.css";
import ChatMessage from "./chat-message/ChatMessage";
import InputChat from "./input-chat/InputChat";

export default function Chat() {
  const { messages } = useMessages();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <>
      <div className="chat-content chat-content-container">
        {messages &&
          messages.map((msg, index) => (
            <ChatMessage
              key={index}
              content={msg.content}
              fromUser={msg.role === "user"}
              writing={msg.writing}
            />
          ))}
        <div ref={bottomRef} className="chat-bottom-ref" />
      </div>
      <InputChat />
    </>
  );
}
