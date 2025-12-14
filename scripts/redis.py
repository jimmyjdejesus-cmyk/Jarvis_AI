"""Minimal redis shim for CI testing."""

class RedisError(Exception):
    pass

class Redis:
    def __init__(self, host=None, port=None, db=None, decode_responses=None):
        pass

    def rpush(self, name, value):
        pass

    def lpop(self, name):
        return None

    def llen(self, name):
        return 0