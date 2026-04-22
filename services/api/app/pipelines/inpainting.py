"""PRD §4.2 P1 图像局部重绘."""
from typing import Any
from app.pipelines.base import BasePipeline


class Inpainting(BasePipeline):
    name = "inpainting"
    endpoint = "/pipeline/inpainting"
    default_priority = "realtime"

    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Inputs: { image_url, mask_url, prompt }
        return {"status": "stub", "pipeline": self.name, "inputs": inputs}
