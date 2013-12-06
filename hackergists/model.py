import json
import time
import os
import redis
import friendly_age

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

"""
Model
"""
def exists(gist_id):
    gist_key = "gist:#"+str(gist_id)

    last_status = redis.hmget(gist_key, 'status')[0]
    retry_count = redis.hmget(gist_key, 'retry_count')[0]

    return last_status == 'OK'

def retry(gist_id, error=None):
    gist_key = "gist:#"+str(gist_id)

    last_status = redis.hmget(gist_key, 'status')[0]
    retry_count = redis.hmget(gist_key, 'retry_count')[0]

    if retry_count is None or int(retry_count) < 10:
        redis.hmset(gist_key, dict(status='ERR', message=error))
        redis.hincrby(gist_key, 'retry_count')
        return 'ERR'
    else:
        redis.hmset(gist_key, dict(status='DEAD'))
        return 'DEAD'

def add(gist):
    gist_key = "gist:#"+str(gist['gist_id'])
    redis.hmset(gist_key, dict(payload=json.dumps(gist), status='OK'))
    index_add(gist['gist_id'], gist['hn_id'])
    redis.set('global.lastupdate', int(friendly_age.get_universal_time())) 
    return 'OK'
