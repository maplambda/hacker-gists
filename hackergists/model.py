import json
import time
import os

import redis

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

def flush():
    redis.flushdb()

def store(gist, id):
    redis.set(id, json.dumps(gist))

def get(id):
    return json.loads(redis.get(id))

def delete(id):
    redis.delete(id)

def exists(id):
    return redis.exists(id)

def latest_gist():
    return redis.zrevrange('index', 0, 0)

def index_add(score=None, id=None,):
    redis.zadd('index', id, score)

def index_clear():
    redis.zremrangebyrank('index', 0, -1)

def index_clear_range(start=None, end=None):
    zrange = redis.zrange('index', start, end) 
    redis.zremrangebyrank('index', start, end)
    return zrange

def index_rev_range(start=None, end=None):
    return redis.zrevrange('index', start, end)

def index_range(start=None, end=None):
    return redis.zrange('index', start, end)

def recent_gists(start=None):
    start = 0 if start == None else start
    end = start + 30 if start is not None else -1
    
    pipe = redis.pipeline()
    for id in redis.zrevrange('index', start, end):
        pipe.get(id)

    return map(lambda x: json.loads(x), pipe.execute())

def info():
    return redis.info()
