from pydantic import BaseModel


class AssetOut(BaseModel):
    id: str
    kind: str
    name: str
    url: str

    model_config = {"from_attributes": True}
