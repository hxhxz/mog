"""PRD §4.1 P0 文生图 / 图生图."""
from typing import Any
from app.pipelines.base import BasePipeline


class Text2Image(BasePipeline):
    name = "text2image"
    endpoint = "/pipeline/text2image"
    default_priority = "realtime"

    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Inputs: { prompt, style_lora, negative_prompt, size }
        return {"status": "stub", "pipeline": self.name, "inputs": inputs}
