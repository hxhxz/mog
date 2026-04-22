from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_base_url: str = "http://api:8000"
    model_name: str = "anthropic/claude-sonnet-4-5"  # 通过 LiteLLM 挂任意后端
    model_api_key: str = ""

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 1  # 独立 DB，和 API 的 pub/sub 隔离

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = AgentSettings()
