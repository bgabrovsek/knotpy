"""
test_cache.py

Unit tests for the Cache class from cache.py.
"""

import pytest
from knotpy.utils.cache import Cache


def test_cache_insertion_and_length_limits():
    cache = Cache(max_cache_size=2, max_key_length=3)
    cache['a'] = 1
    cache['bb'] = 2
    # Cache should contain both items.
    assert len(cache) == 2
    assert cache['a'] == 1
    assert cache['bb'] == 2

def test_key_too_long_is_ignored():
    cache = Cache(max_cache_size=2, max_key_length=3)
    cache['abcd'] = 11  # Too long, should be ignored
    assert 'abcd' not in cache
    cache['abc'] = 22   # Ok
    assert 'abc' in cache

def test_cache_eviction_on_full():
    cache = Cache(max_cache_size=2, max_key_length=5)
    cache['ab'] = 1
    cache['abc'] = 2
    cache['d'] = 3  # 'abc' (len=3) evicted, since 'ab' (len=2) is shorter
    assert 'd' in cache
    assert 'ab' in cache or 'abc' in cache
    # Only two items
    assert len(cache) == 2
    # The evicted one should be 'abc' since d is shorter than abc

def test_eviction_prefers_longest_key():
    cache = Cache(max_cache_size=2, max_key_length=5)
    cache['short'] = 1  # len=5
    cache['mid'] = 2    # len=3
    cache['a'] = 100    # len=1, should evict 'short' (longest key)
    assert 'short' not in cache
    assert 'mid' in cache
    assert 'a' in cache

def test_refuse_replace_when_key_not_shorter():
    cache = Cache(max_cache_size=2, max_key_length=4)
    cache['abc'] = 1
    cache['de'] = 2
    # Now cache is full; try to insert 'xyz', length=3 (not shorter than any existing)
    cache['xyz'] = 99  # Should not get in, as no existing key is longer.
    assert 'xyz' not in cache
    # Try to insert an even shorter key
    cache['q'] = 7  # Should evict 'abc' (len=3)
    assert 'q' in cache
    assert len(cache) == 2

if __name__ == "__main__":
    pytest.main([__file__])