"""LoRA / 角色卡资产查询."""
import httpx
from app.settings import settings


try:
    from smolagents import tool
except ImportError:
    def tool(f):
        return f


@tool
def list_style_loras() -> list[dict]:
    """列出平台预置的风格 LoRA（古装国风 / 都市现代写实 / 甜宠日系 / ...）."""
    resp = httpx.get(f"{settings.api_base_url}/api/v1/assets/loras/style", timeout=15.0)
    resp.raise_for_status()
    return resp.json()
