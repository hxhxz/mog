"""PRD §4.1 P0 角色一致性生成（IP-Adapter + InstantID，§4.4）."""
from typing import Any
from app.pipelines.base import BasePipeline


class Character2Image(BasePipeline):
    name = "character2image"
    endpoint = "/pipeline/character2image"
    default_priority = "realtime"

    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Inputs: { reference_image_url, character_lora_id, prompt }
        return {"status": "stub", "pipeline": self.name, "inputs": inputs}
