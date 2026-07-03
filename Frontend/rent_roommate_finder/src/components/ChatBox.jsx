import { useEffect, useRef, useState } from "react";
import { getChatHistory, connectChatSocket } from "../services/chatService";
import Loader from "./Loader";

export default function ChatBox({ interestId, currentUserId }) {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [peerTyping, setPeerTyping] = useState(false);
  const socketRef = useRef(null);
  const bottomRef = useRef(null);
  const typingTimeout = useRef(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    getChatHistory(interestId)
      .then((history) => {
        if (!cancelled) setMessages(history.messages || history || []);
      })
      .finally(() => !cancelled && setLoading(false));

    const socket = connectChatSocket(interestId);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === "message") {
        setMessages((prev) => [...prev, payload.data]);
        setPeerTyping(false);
      } else if (payload.type === "typing") {
        setPeerTyping(true);
        clearTimeout(typingTimeout.current);
        typingTimeout.current = setTimeout(() => setPeerTyping(false), 2000);
      }
    };

    return () => {
      cancelled = true;
      socket.close();
    };
  }, [interestId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  function sendMessage(e) {
    e.preventDefault();
    if (!draft.trim() || socketRef.current?.readyState !== WebSocket.OPEN) return;
    socketRef.current.send(JSON.stringify({ type: "message", message: draft }));
    setDraft("");
  }

  function handleTyping(value) {
    setDraft(value);
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "typing" }));
    }
  }

  if (loading) return <Loader />;

  return (
    <div className="chat-shell">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p style={{ textAlign: "center" }}>No messages yet. Say hello.</p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id || `${msg.sender_id}-${msg.created_at}`}
            className={`chat-bubble ${msg.sender_id === currentUserId ? "mine" : ""}`}
          >
            {msg.message}
            <span className="chat-meta">
              {new Date(msg.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {peerTyping && <div className="chat-typing">Typing…</div>}

      <form className="chat-input-row" onSubmit={sendMessage}>
        <input
          placeholder="Write a message"
          value={draft}
          onChange={(e) => handleTyping(e.target.value)}
        />
        <button type="submit" className="btn btn-primary btn-sm">
          Send
        </button>
      </form>
    </div>
  );
}
