"""Pipeline 基类 — 所有 ComfyUI 工作流封装的公共契约.

执行路径：
  - 直接调用（legacy）：submit(inputs)，由 pipeline 子类自带 workflow 定义
  - 模板驱动：submit_workflow(workflow_json)，workflow 由 TemplateService 注入 materials 后传入
两条路径最终都 POST 到 ComfyUI /prompt API。
"""
from __future__ import annotations
from typing import Any, Literal
from abc import ABC, abstractmethod


class BasePipeline(ABC):
    name: str = ""
    default_priority: Literal["realtime", "background"] = "realtime"

    @abstractmethod
    def submit(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """直接调用模式：子类自带 workflow 定义，inputs 为高层参数.
        Returns {"remote_id": str, ...}。
        """

    def submit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """模板驱动模式：接收已注入 materials 的完整 ComfyUI /prompt JSON，直接 POST.

        子类可覆写此方法以添加 pipeline 特定的预处理（如客户端 ID 注入）。
        默认实现把 workflow 透传给 _post_prompt()。
        """
        return self._post_prompt(workflow)

    def poll(self, remote_id: str) -> dict[str, Any]:
        return {"status": "stub", "remote_id": remote_id}

    def cancel(self, remote_id: str) -> None:
        return None

    def _post_prompt(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """POST workflow 到 ComfyUI /prompt。MVP 为 stub，真实实现用 httpx。"""
        return {"status": "stub", "workflow_nodes": list(workflow.keys())}
