import Sidebar from "./features/assets/Sidebar";
import ChatPane from "./features/chat/ChatPane";
import PreviewPane from "./features/preview/PreviewPane";

export default function App() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <Sidebar />
      </aside>
      <section className="chat">
        <ChatPane />
      </section>
      <section className="preview">
        <PreviewPane />
      </section>
    </div>
  );
}
