"""种子数据：预置风格 LoRA + 演示项目 (PRD §4.4)。

用法：
    docker compose run --rm api python -m scripts.seed
    # 或本地开发环境
    cd services/api && python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# 允许直接在仓库根执行
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "services" / "api"))

from app.core.config import get_settings  # noqa: E402
from app.models.asset import Asset, AssetKind  # noqa: E402
from app.models.project import Project  # noqa: E402


# PRD §4.4 —— 风格 LoRA 预置清单
P0_STYLES = [
    {"name": "古装国风", "slug": "guzhuang_guofeng", "lora_path": "loras/style/guzhuang_guofeng.safetensors"},
    {"name": "都市现代写实", "slug": "dushi_xianshi", "lora_path": "loras/style/dushi_xianshi.safetensors"},
    {"name": "甜宠日系", "slug": "tianchong_rixi", "lora_path": "loras/style/tianchong_rixi.safetensors"},
    {"name": "悬疑暗黑", "slug": "xuanyi_anhei", "lora_path": "loras/style/xuanyi_anhei.safetensors"},
]
P1_STYLES = [
    {"name": "ins 小清新", "slug": "ins_qingxin", "lora_path": "loras/style/ins_qingxin.safetensors"},
    {"name": "高端质感写实", "slug": "gaoduan_zhigan", "lora_path": "loras/style/gaoduan_zhigan.safetensors"},
    {"name": "轻商务简约", "slug": "qing_shangwu", "lora_path": "loras/style/qing_shangwu.safetensors"},
]


async def seed() -> None:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        # 1. 预置风格 LoRA
        for spec in P0_STYLES + P1_STYLES:
            existing = await session.scalar(select(Asset).where(Asset.slug == spec["slug"]))
            if existing:
                print(f"  · skip  style_lora: {spec['name']}")
                continue
            session.add(Asset(
                kind=AssetKind.STYLE_LORA,
                name=spec["name"],
                slug=spec["slug"],
                uri=spec["lora_path"],
                meta={"preset": True},
            ))
            print(f"  + seed  style_lora: {spec['name']}")

        # 2. 演示项目
        demo_slug = "demo-project"
        existing = await session.scalar(select(Project).where(Project.slug == demo_slug))
        if not existing:
            session.add(Project(
                slug=demo_slug,
                name="示例项目",
                description="用于最小 Demo 链路验证，可随意删除。",
            ))
            print(f"  + seed  project: {demo_slug}")
        else:
            print(f"  · skip  project: {demo_slug}")

        await session.commit()

    await engine.dispose()
    print("✔ seed 完成")


if __name__ == "__main__":
    asyncio.run(seed())
