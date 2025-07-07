import MarkdownRenderer from "../../markdown-renderer/MarkdownRenderer";
import "./chat-message.css";

export default function ChatMessage({ content, fromUser, writing }) {
  return (
    <div className={`chat-message ${fromUser ? "from-user" : "from-bot"}`}>
      <div
        className={`chat-message-content ${
          fromUser ? "user-color" : "bot-color"
        }
        ${writing ? "writing" : ""}
        `}
      >
        <MarkdownRenderer content={content} />
        <div
          className={`sent-by-detail ${fromUser ? "user-color" : "bot-color"}`}
        />
      </div>
      {writing && (
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      )}
    </div>
  );
}
