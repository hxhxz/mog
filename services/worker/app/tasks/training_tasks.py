"""角色 LoRA 异步训练 — PRD §4.4."""
from app.celery_app import celery_app


@celery_app.task(name="mog.training.character_lora")
def train_character_lora(character_id: str, reference_urls: list[str]) -> dict:
    # MVP stub. 后续接入 kohya_ss / sd-scripts 训练 pipeline.
    return {"character_id": character_id, "status": "stub", "inputs": reference_urls}
