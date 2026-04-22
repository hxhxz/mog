"""PRD §4.2 P1 视频超分 — 后台静默运行."""
from typing import Any
from app.pipelines.base import BasePipeline


class Upscale(BasePipeline):
    name = "upscale"
    endpoint = "/pipeline/upscale"
    default_priority = "background"  # PRD §4.3 规律总结：Pipeline 6 后台静默

    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Inputs: { video_url, scale }
        return {"status": "stub", "pipeline": self.name, "inputs": inputs}
