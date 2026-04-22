"""Agent Tool 调用 & REST 触发的唯一入口.

新增 Pipeline 只需：
  1. 在 app/pipelines/ 下加一个文件继承 BasePipeline
  2. 在此 registry 注册即可
"""
from app.pipelines.base import BasePipeline
from app.pipelines.text2image import Text2Image
from app.pipelines.character2image import Character2Image
from app.pipelines.image2video import Image2Video
from app.pipelines.keyframe2video import Keyframe2Video
from app.pipelines.talk2video import Talk2Video
from app.pipelines.concat import Concat
from app.pipelines.tts_align import TtsAlign
from app.pipelines.inpainting import Inpainting
from app.pipelines.upscale import Upscale


PIPELINE_REGISTRY: dict[str, type[BasePipeline]] = {
    # P0 — PRD §4.1
    "text2image": Text2Image,
    "character2image": Character2Image,
    "image2video": Image2Video,
    "keyframe2video": Keyframe2Video,
    "talk2video": Talk2Video,
    "concat": Concat,
    "tts_align": TtsAlign,
    # P1 — PRD §4.2
    "inpainting": Inpainting,
    "upscale": Upscale,
}
