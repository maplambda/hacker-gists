import redis as redis
import json

redis = redis.StrictRedis()

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

def index_add(id=None, score=None):
    redis.zadd('index', score, id)

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
    return map(lambda x: get(x), 
               redis.zrevrange('index', start, end))

def info():
    return redis.info()
