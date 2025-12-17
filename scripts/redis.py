# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



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