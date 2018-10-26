from functools import lru_cache

import requests


@lru_cache(maxsize=64)
def cached_get_request(url):
    return requests.get(url)
