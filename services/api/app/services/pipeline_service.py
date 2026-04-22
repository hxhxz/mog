"""Pipeline 业务语义 → 具体 Pipeline client 调用."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.pipelines.registry import PIPELINE_REGISTRY


class PipelineService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def get_pipeline(self, name: str):
        if name not in PIPELINE_REGISTRY:
            raise ValueError(f"Unknown pipeline: {name}")
        return PIPELINE_REGISTRY[name]()

    def list_names(self) -> list[str]:
        return list(PIPELINE_REGISTRY.keys())
