import json
import os
from typing import Any, Optional

import redis

# Redis connection
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL") or "",
    decode_responses=True,
)


class CacheService:
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    @staticmethod
    def set(key: str, value: Any, expire: int = 300) -> bool:
        """Set value in cache with expiration (default 5 minutes)"""
        try:
            redis_client.setex(key, expire, json.dumps(value))
            return True
        except Exception:
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """Delete value from cache"""
        try:
            redis_client.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    def invalidate_pattern(pattern: str) -> bool:
        """Invalidate all keys matching a pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception:
            return False


def get_cache_key_user_chatrooms(user_id: int) -> str:
    """Generate cache key for user chatrooms"""
    return f"user_chatrooms:{user_id}"
