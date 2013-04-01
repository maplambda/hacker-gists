import redis
import os

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

def set_label(name, value):
    redis.hset('stat.label', name, value)

def clear_label(name):
    redis.hdel('stat.label', name)

def get_label(name):
    return redis.hget('stat.label', name)

def get_labels():
    return redis.hgetall('stat.label')

def clear_all():
    redis.hdel('stat.label', *redis.hkeys('stat.label'))
