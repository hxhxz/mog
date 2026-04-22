from fastapi import APIRouter
from . import projects, segments, characters, assets, pipelines, jobs, agent, health, templates

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(segments.router, prefix="/segments", tags=["segments"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
