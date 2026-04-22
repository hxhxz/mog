"""每个 Pipeline 暴露为一个 smolagents tool — 通过 REST 调 API 侧 JobService."""
from typing import Any
import httpx

from app.settings import settings


def _submit(project_id: str, pipeline: str, inputs: dict[str, Any], priority: str = "realtime") -> dict:
    resp = httpx.post(
        f"{settings.api_base_url}/api/v1/pipelines/{pipeline}/invoke",
        json={"project_id": project_id, "inputs": inputs, "priority": priority},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()


def all_pipeline_tools() -> list:
    """返回全部 Pipeline 工具.

    在运行时用 smolagents `@tool` 装饰器注册（此处给出模板）.
    """
    try:
        from smolagents import tool
    except ImportError:
        return []

    @tool
    def text2image(project_id: str, prompt: str, style_lora: str | None = None) -> dict:
        """文生图：根据 prompt 生成分镜图（PRD §4.1 Pipeline 1）"""
        return _submit(project_id, "text2image", {"prompt": prompt, "style_lora": style_lora})

    @tool
    def character2image(project_id: str, reference_image_url: str, prompt: str,
                        character_lora_id: str | None = None) -> dict:
        """角色一致性生成：保证主角跨片段一致（PRD §4.1 Pipeline 2）"""
        return _submit(project_id, "character2image", {
            "reference_image_url": reference_image_url,
            "prompt": prompt,
            "character_lora_id": character_lora_id,
        })

    @tool
    def image2video(project_id: str, image_url: str, camera_motion: str = "static",
                    duration_sec: int = 3) -> dict:
        """图生视频（PRD §4.1 Pipeline 3）"""
        return _submit(project_id, "image2video", {
            "image_url": image_url, "camera_motion": camera_motion, "duration_sec": duration_sec,
        })

    @tool
    def keyframe2video(project_id: str, first_frame_url: str, last_frame_url: str,
                       prompt: str) -> dict:
        """首尾帧控制视频：上一段末帧→下一段首帧，保证转场连贯（PRD §4.1 Pipeline 4）"""
        return _submit(project_id, "keyframe2video", {
            "first_frame_url": first_frame_url,
            "last_frame_url": last_frame_url,
            "prompt": prompt,
        })

    @tool
    def talk2video(project_id: str, portrait_url: str, audio_url: str) -> dict:
        """数字人生成：图片+音频（PRD §4.1 Pipeline 5）"""
        return _submit(project_id, "talk2video", {
            "portrait_url": portrait_url, "audio_url": audio_url,
        })

    @tool
    def concat(project_id: str, video_urls: list[str], transition_type: str = "fade") -> dict:
        """视频拼接 + 转场（PRD §4.1 Pipeline 7）"""
        return _submit(project_id, "concat", {
            "video_urls": video_urls, "transition_type": transition_type,
        })

    @tool
    def tts_align(project_id: str, full_script_text: str, timeline: list[dict]) -> dict:
        """整体音频生成 + 时间轴对齐（PRD §4.1 Pipeline 8）"""
        return _submit(project_id, "tts_align", {
            "full_script_text": full_script_text, "timeline": timeline,
        })

    @tool
    def inpainting(project_id: str, image_url: str, mask_url: str, prompt: str) -> dict:
        """图像局部重绘（PRD §4.2 Pipeline 5）"""
        return _submit(project_id, "inpainting", {
            "image_url": image_url, "mask_url": mask_url, "prompt": prompt,
        })

    @tool
    def upscale(project_id: str, video_url: str, scale: int = 2) -> dict:
        """视频超分，后台静默（PRD §4.2 Pipeline 6）"""
        return _submit(project_id, "upscale", {
            "video_url": video_url, "scale": scale,
        }, priority="background")

    return [text2image, character2image, image2video, keyframe2video, talk2video,
            concat, tts_align, inpainting, upscale]
