from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "mog"
    postgres_password: str = "mog"
    postgres_db: str = "mog"

    comfyui_host: str = "comfyui"
    comfyui_port: int = 8188

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = WorkerSettings()
