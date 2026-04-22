from app.pipelines.registry import PIPELINE_REGISTRY


def test_all_prd_pipelines_registered() -> None:
    """PRD §4.1 (7 P0) + §4.2 (2 P1) = 9."""
    expected = {
        "text2image", "character2image", "image2video", "keyframe2video",
        "talk2video", "concat", "tts_align",       # P0
        "inpainting", "upscale",                   # P1
    }
    assert set(PIPELINE_REGISTRY.keys()) == expected
    assert len(PIPELINE_REGISTRY) == 9


def test_upscale_is_background_priority() -> None:
    """PRD §4.3 规律总结：Pipeline 6 (upscale) 后台静默。"""
    assert PIPELINE_REGISTRY["upscale"].default_priority == "background"
