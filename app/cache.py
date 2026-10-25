"""
Redis caching layer for DarkMirror.

Provides async caching for prediction results, reducing redundant
pipeline executions for previously-seen conversation fingerprints.
Falls back gracefully if Redis is unavailable.
"""
import json
import hashlib
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Lazy-initialised Redis connection
_redis_client = None


def _get_redis():
    """Lazily initialise and return the Redis client."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            _redis_client.ping()
            logger.info("Redis connection established at %s", settings.REDIS_URL)
        except Exception as exc:
            logger.warning("Redis unavailable (%s) – caching disabled", exc)
            _redis_client = False  # Sentinel: tried and failed
    return _redis_client if _redis_client else None


def _fingerprint(text: str) -> str:
    """Generate a SHA-256 fingerprint for conversation text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def get_cached_prediction(conversation_text: str) -> Optional[dict]:
    """
    Look up a cached prediction by conversation fingerprint.

    Returns the cached prediction dict, or None on miss / Redis unavailable.
    """
    client = _get_redis()
    if client is None:
        return None
    try:
        key = f"darkmirror:pred:{_fingerprint(conversation_text)}"
        raw = client.get(key)
        if raw:
            logger.debug("Cache HIT for %s", key)
            return json.loads(raw)
        logger.debug("Cache MISS for %s", key)
        return None
    except Exception as exc:
        logger.warning("Redis GET error: %s", exc)
        return None


async def set_cached_prediction(
    conversation_text: str,
    prediction: dict,
    ttl_seconds: int = 3600,
) -> None:
    """
    Store a prediction in Redis with a TTL.

    Args:
        conversation_text: Raw conversation used to derive the cache key.
        prediction: Serialisable prediction dict to cache.
        ttl_seconds: Time-to-live in seconds (default 1 hour).
    """
    client = _get_redis()
    if client is None:
        return
    try:
        key = f"darkmirror:pred:{_fingerprint(conversation_text)}"
        client.setex(key, ttl_seconds, json.dumps(prediction))
        logger.debug("Cached prediction at %s (TTL=%ds)", key, ttl_seconds)
    except Exception as exc:
        logger.warning("Redis SET error: %s", exc)


async def invalidate_cache(conversation_text: str) -> None:
    """Remove a cached prediction."""
    client = _get_redis()
    if client is None:
        return
    try:
        key = f"darkmirror:pred:{_fingerprint(conversation_text)}"
        client.delete(key)
    except Exception as exc:
        logger.warning("Redis DEL error: %s", exc)
