"""意图分类 — PRD §3.2 区分 regenerate / edit_local / adjust_prompt / confirm / cancel."""
from enum import Enum


class Intent(str, Enum):
    REGENERATE = "regenerate"
    EDIT_LOCAL = "edit_local"
    ADJUST_PROMPT = "adjust_prompt"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


INTENT_KEYWORDS: dict[Intent, list[str]] = {
    Intent.REGENERATE: ["重新生成", "重画", "重新来"],
    Intent.EDIT_LOCAL: ["局部", "背景", "换成", "框选"],
    Intent.ADJUST_PROMPT: ["改提示词", "调整风格", "更"],
    Intent.CONFIRM: ["确认", "可以", "没问题", "下一步"],
    Intent.CANCEL: ["取消", "停止", "别跑了"],
}


def classify(message: str) -> Intent:
    """极简关键词兜底；真实实现由 Agent LLM 判别."""
    for intent, kws in INTENT_KEYWORDS.items():
        if any(kw in message for kw in kws):
            return intent
    return Intent.UNKNOWN
