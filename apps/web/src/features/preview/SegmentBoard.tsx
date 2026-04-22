import FrameCard from "./FrameCard";

const DEMO_SEGMENTS = [
  { id: "s1", order: 1, text: "清晨街道，女孩走向咖啡馆门口", status: "draft" },
  { id: "s2", order: 2, text: "咖啡馆内，女孩点单拿到草莓奶茶", status: "draft" },
  { id: "s3", order: 3, text: "阳光下，女孩微笑举杯拍照", status: "draft" },
];

export default function SegmentBoard() {
  return (
    <div>
      {DEMO_SEGMENTS.map((s) => (
        <FrameCard key={s.id} segment={s} />
      ))}
    </div>
  );
}
