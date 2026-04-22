"""PRD §4.1 P0 首尾帧控制视频 — 解决痛点 3 转场连贯."""
from typing import Any
from app.pipelines.base import BasePipeline


class Keyframe2Video(BasePipeline):
    name = "keyframe2video"
    endpoint = "/pipeline/keyframe2video"
    default_priority = "realtime"

    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Inputs: { first_frame_url, last_frame_url, prompt }
        return {"status": "stub", "pipeline": self.name, "inputs": inputs}
