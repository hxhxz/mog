"""模型后端封装 — LiteLLM / HfApi / Transformers 可切换."""
from app.settings import settings


def make_model():
    """返回一个 smolagents-compatible model 对象."""
    try:
        from smolagents import LiteLLMModel
    except ImportError:
        return None
    return LiteLLMModel(model_id=settings.model_name, api_key=settings.model_api_key or None)
