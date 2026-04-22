export default function MessageList({ messages }: { messages: { role: string; content: string }[] }) {
  return (
    <div className="chat-messages">
      {messages.map((m, i) => (
        <div key={i} style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 11, opacity: 0.6 }}>{m.role}</div>
          <div>{m.content}</div>
        </div>
      ))}
    </div>
  );
}
