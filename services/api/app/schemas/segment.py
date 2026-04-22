from pydantic import BaseModel


class SegmentOut(BaseModel):
    id: str
    project_id: str
    order_index: int
    text: str
    emotion: str | None = None
    duration_sec: int | None = None
    storyboard_url: str | None = None
    video_url: str | None = None
    status: str

    model_config = {"from_attributes": True}


class SegmentUpdate(BaseModel):
    text: str | None = None
    emotion: str | None = None
    duration_sec: int | None = None
