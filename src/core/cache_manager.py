from cacheout import CacheManager, Cache

__CACHE_MANAGER = CacheManager()


def get_cache(cache_name):
    if cache_name not in __CACHE_MANAGER:
        __CACHE_MANAGER.register(cache_name, Cache(maxsize=512, ttl=60*60*24))
    return __CACHE_MANAGER[cache_name]
