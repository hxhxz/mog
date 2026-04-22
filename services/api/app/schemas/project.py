from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    style_lora_id: str | None = None


class ProjectOut(BaseModel):
    id: str
    name: str
    style_lora_id: str | None = None
    audio_track_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterRef(BaseModel):
    id: str
    name: str
    reference_image_url: str | None = None
    character_lora_id: str | None = None


class SegmentRef(BaseModel):
    id: str
    order_index: int
    status: str
    storyboard_url: str | None = None
    video_url: str | None = None


class ProjectContext(BaseModel):
    """PRD §3.3 Context 对象（响应 DTO）."""
    project_id: str
    style_lora: str | None = None
    characters: list[CharacterRef] = []
    segments: list[SegmentRef] = []
    audio_track: str | None = None
