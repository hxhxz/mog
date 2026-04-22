export default function Sidebar() {
  return (
    <div>
      <h3 style={{ marginTop: 0 }}>mog</h3>
      <div style={{ fontSize: 12, opacity: 0.6, marginBottom: 16 }}>AI 短剧视频生成平台</div>

      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>项目列表</div>
      <div style={{ padding: 8, background: "#2a3145", borderRadius: 4, marginBottom: 16 }}>
        demo-project
      </div>

      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>资产库</div>
      <div style={{ opacity: 0.7, fontSize: 12 }}>风格 LoRA / 角色卡</div>
    </div>
  );
}
