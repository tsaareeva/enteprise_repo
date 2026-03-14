from cachetools import TTLCache, cached
from typing import Any

customer_cache = TTLCache(maxsize=1000, ttl=600)
all_customers_cache = TTLCache(maxsize=100, ttl=600)

def clear_customer_cache():
    customer_cache.clear()
    all_customers_cache.clear()

def get_customer_cache():
    return customer_cache

def get_all_customers_cache():
    return all_customers_cache