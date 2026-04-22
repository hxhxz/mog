type Segment = { id: string; order: number; text: string; status: string };

export default function FrameCard({ segment }: { segment: Segment }) {
  return (
    <div className="segment-card">
      <div style={{ fontSize: 12, opacity: 0.6 }}>
        片段 #{segment.order} · {segment.status}
      </div>
      <div style={{ marginTop: 4 }}>{segment.text}</div>
    </div>
  );
}
