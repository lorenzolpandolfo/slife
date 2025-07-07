import "./chat-message.css";
import MarkdownRenderer from "../../markdown-renderer/MarkdownRenderer";

export default function ChatMessage({ content, fromUser, writing }) {
  return (
    <div className={`chat-message ${fromUser ? "from-user" : "from-bot"}`}>
      <img
        src={`src/assets/${fromUser ? "user_pfp.svg" : "lucas_pfp.svg"}`}
        alt="Icon"
        className={`message-author-icon ${fromUser ? "from-user" : "from-bot"}`}
      />

      <div
        className={`chat-message-content ${
          fromUser ? "user-color" : "bot-color"
        }
        ${writing ? "writing" : ""}
        `}
      >
        <span className="message-author-name">
          {fromUser ? "" : "Assistente Lucas"}
        </span>
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
