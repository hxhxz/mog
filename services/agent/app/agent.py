"""smolagents Agent 初始化.

- 模型后端通过 LiteLLM 适配，可切 Claude / OpenAI / 本地 vLLM / Ollama
- 工具集：每个 Pipeline 一个 @tool + context 读写 + asset 查询
"""
from functools import lru_cache

from app.models import make_model
from app.tools.pipeline_tools import all_pipeline_tools
from app.tools.template_tools import load_template_tools
from app.tools.context_tools import get_project_context
from app.tools.asset_tools import list_style_loras


@lru_cache
def get_agent():
    """延迟导入 smolagents，方便 MVP 跑通时先放空."""
    try:
        from smolagents import ToolCallingAgent
    except ImportError:
        return _StubAgent()

    # 模板工具优先；pipeline 直调工具作为兜底保留
    tools = [
        *load_template_tools(),
        *all_pipeline_tools(),
        get_project_context,
        list_style_loras,
    ]
    return ToolCallingAgent(tools=tools, model=make_model(), max_steps=8)


class _StubAgent:
    def run(self, message: str, **_: object) -> str:
        return f"[stub agent] received: {message}"
