import json
import time
import os

import redis

"""
redis
"""
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

""" 
helpers for front page
"""
def index_add(id, score):
    redis.zadd('index', id, score)

def index_clear():
    redis.zremrangebyrank('index', 0, -1)

def index_clear_range(start=None, end=None):
    zrange = redis.zrange('index', start, end) 
    redis.zremrangebyrank('index', start, end)
    return zrange

def recent_gists(start=None):
    start = 0 if start == None else start
    end = start + 30 if start is not None else -1
    
    pipe = redis.pipeline()
    for id in redis.zrevrange('index', start, end):
        pipe.hmget("gist:#"+str(id), 'payload')

    return map(lambda x: json.loads(x[0]),
           filter(lambda x:x is not None, pipe.execute()))
