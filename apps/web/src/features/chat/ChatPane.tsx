import { useEffect, useState } from "react";
import { useAgentSocket } from "../../ws/agentSocket";
import MessageList from "./MessageList";
import Composer from "./Composer";

export default function ChatPane() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "你好，我是 mog Agent。上传你的剧本/文案，我们开始创作吧。" },
  ]);
  const { send, subscribe } = useAgentSocket("demo-project");

  useEffect(() => {
    return subscribe((msg) => {
      setMessages((prev) => [...prev, { role: "assistant", content: JSON.stringify(msg) }]);
    });
  }, [subscribe]);

  function handleSend(text: string) {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    send({ type: "user_message", content: text });
  }

  return (
    <>
      <MessageList messages={messages} />
      <Composer onSend={handleSend} />
    </>
  );
}
