"""项目 Context 读/写 — PRD §3.3."""
import httpx
from app.settings import settings


try:
    from smolagents import tool
except ImportError:
    def tool(f):
        return f


@tool
def get_project_context(project_id: str) -> dict:
    """查询一个项目的完整 Context（风格 LoRA / 角色 / 片段 / 音轨）.
    
    Args:
        project_id: 项目的唯一标识符 (UUID)，用于获取特定的项目配置。
    """
    resp = httpx.get(f"{settings.api_base_url}/api/v1/projects/{project_id}/context", timeout=15.0)
    resp.raise_for_status()
    return resp.json()
