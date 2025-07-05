import "./chat-message.css";

export default function ChatMessage({ content, fromUser }) {
  return (
    <div className={`chat-message ${fromUser ? "from-user" : "from-bot"}`}>
      <div
        className={`chat-message-content ${
          fromUser ? "user-color" : "bot-color"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
