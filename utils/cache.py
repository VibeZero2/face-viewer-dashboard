"""
Caching utilities for Face Viewer Dashboard
Provides caching functionality for expensive operations
"""

import functools
import time
from datetime import datetime, timedelta

# Simple in-memory cache
_cache = {}

def cached(timeout=60, key_prefix=None):
    """
    Cache decorator for expensive functions
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Optional prefix for cache key
        
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_prefix:
                cache_key = f"{key_prefix}:{func.__name__}"
            else:
                cache_key = func.__name__
                
            # Check if result is in cache and not expired
            if cache_key in _cache:
                result, timestamp = _cache[cache_key]
                if timestamp + timeout > time.time():
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

def clear_cache(key_prefix=None):
    """
    Clear cache entries
    
    Args:
        key_prefix: Optional prefix to clear only specific entries
    """
    global _cache
    if key_prefix:
        # Clear only entries with matching prefix
        keys_to_remove = [k for k in _cache.keys() if k.startswith(f"{key_prefix}:")]
        for key in keys_to_remove:
            del _cache[key]
    else:
        # Clear all cache
        _cache = {}
