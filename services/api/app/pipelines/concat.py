"""PRD §4.1 P0 视频拼接 + 转场."""
from typing import Any
from app.pipelines.base import BasePipeline


class Concat(BasePipeline):
    name = "concat"
    endpoint = "/pipeline/concat"
    default_priority = "realtime"

    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Inputs: { video_urls: [...], transition_type }
        return {"status": "stub", "pipeline": self.name, "inputs": inputs}
