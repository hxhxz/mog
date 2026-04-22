"""Aliyun OSS client wrapper — PRD §5.1 资产层."""
from functools import lru_cache
from app.core.config import settings


class StorageClient:
    """Thin OSS wrapper. MVP 阶段若未配置 OSS，使用本地目录占位。"""

    def __init__(self) -> None:
        self._oss = None
        if settings.oss_bucket and settings.oss_access_key_id:
            import oss2
            auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
            self._oss = oss2.Bucket(auth, settings.oss_endpoint, settings.oss_bucket)

    def put_object(self, key: str, data: bytes) -> str:
        if self._oss is None:
            return f"local://{key}"  # stub
        self._oss.put_object(key, data)
        return f"oss://{settings.oss_bucket}/{key}"

    def sign_url(self, key: str, expires: int = 3600) -> str:
        if self._oss is None:
            return f"/static/{key}"
        return self._oss.sign_url("GET", key, expires)


@lru_cache
def get_storage() -> StorageClient:
    return StorageClient()
