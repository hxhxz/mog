import { useState } from "react";

export default function Composer({ onSend }: { onSend: (text: string) => void }) {
  const [text, setText] = useState("");

  function submit() {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  }

  return (
    <div className="chat-composer">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder="输入消息，或粘贴剧本/文案..."
      />
      <button onClick={submit}>发送</button>
    </div>
  );
}
