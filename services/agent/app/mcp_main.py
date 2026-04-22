"""MCP SSE server 入口 — 单独进程，端口 8101.

docker-compose 中以独立命令启动：
    uvicorn app.mcp_main:app --host 0.0.0.0 --port 8101

Claude Desktop 本地配置示例：
    {
      "mcpServers": {
        "mog-templates": {
          "transport": "sse",
          "url": "http://localhost:8101/sse"
        }
      }
    }
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.mcp_server import asgi_app, _register_template_tools


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _register_template_tools()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/", asgi_app)
