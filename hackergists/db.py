import redis as redis
import json

#redis = redis.StrictRedis(db='test5')
redis = redis.StrictRedis()

def flush():
    redis.flushdb()

def store(id, gist):
    redis.set(id, json.dumps(gist))

def delete(id):
    redis.delete(id)

def get(id):
    return json.loads(redis.get(id))

def exists(id):
    return redis.exists(id)
