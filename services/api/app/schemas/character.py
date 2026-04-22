from pydantic import BaseModel


class CharacterCreate(BaseModel):
    project_id: str
    name: str


class CharacterOut(BaseModel):
    id: str
    project_id: str
    name: str
    reference_image_url: str | None = None
    character_lora_id: str | None = None

    model_config = {"from_attributes": True}
