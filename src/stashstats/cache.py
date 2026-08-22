import json
import logging
import os
from functools import wraps
import redis
from stashstats.models import YarnSearchResponse, YarnDetailResponse

logger = logging.getLogger("stashstats.cache")

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=3)

def cached_yarn_search(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        query = kwargs.get("query", args[0] if args else "")
        page = kwargs.get("page", 1)
        page_size = kwargs.get("page_size", 50)
        sort = kwargs.get("sort", "best")
        
        key = f"yarn_search:{query}:{page}:{page_size}:{sort}"
        client = None
        try:
            client = get_redis_client()
            cached = client.get(key)
            if cached:
                logger.debug(f"[REDIS HIT] key={key}")
                data = json.loads(cached)
                return YarnSearchResponse.model_validate(data)
            logger.debug(f"[REDIS MISS] key={key}")
        except Exception as e:
            logger.debug(f"[REDIS ERROR] lookup failed for {key}: {e}")
            
        result = func(self, *args, **kwargs)
        
        if client:
            try:
                client.setex(key, 7200, result.model_dump_json())
                logger.debug(f"[REDIS SET] key={key} ttl=7200s")
            except Exception as e:
                logger.debug(f"[REDIS ERROR] store failed for {key}: {e}")
                
        return result
    return wrapper

def cached_yarn_details(func):
    @wraps(func)
    def wrapper(self, yarn_id, *args, **kwargs):
        key = f"yarn_details:{yarn_id}"
        client = None
        try:
            client = get_redis_client()
            cached = client.get(key)
            if cached:
                logger.debug(f"[REDIS HIT] key={key}")
                data = json.loads(cached)
                return YarnDetailResponse.model_validate(data)
            logger.debug(f"[REDIS MISS] key={key}")
        except Exception as e:
            logger.debug(f"[REDIS ERROR] lookup failed for {key}: {e}")
            
        result = func(self, yarn_id, *args, **kwargs)
        
        if client:
            try:
                client.setex(key, 86400, result.model_dump_json())
                logger.debug(f"[REDIS SET] key={key} ttl=86400s")
            except Exception as e:
                logger.debug(f"[REDIS ERROR] store failed for {key}: {e}")
                
        return result
    return wrapper
