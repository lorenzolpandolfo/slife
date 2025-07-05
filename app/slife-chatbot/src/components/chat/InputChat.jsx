import "./input-chat.css";

export default function InputChat() {
  return (
    <div className="input-chat">
      <input
        type="text"
        name="msg-input"
        id="msg-input"
        placeholder="Digite a sua mensagem..."
      />
      <button type="button" className="send-button">
        <img src="src/assets/send.svg" alt="send button" />
      </button>
    </div>
  );
}
