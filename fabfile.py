import re
import urlparse
import json

from hackergists import thriftdb
from hackergists import model
from hackergists import metrics
from hackergists import gist as gist_api
from hackergists import friendly_age

thrift = thriftdb.ThriftDb('http://api.thriftdb.com', 'api.hnsearch.com', 'items')

"""
Search Hacker News for recent Gists
"""
def _fetch_gist_ids():
    criteria = dict(limit = 100, 
                    sortby = 'create_ts desc',
                    q = 'gist.github.com',
                    filter = {'[fields][type]' : 'comment'})

    comments = thrift.search(**criteria)

    nondead = [item for item in comments['results'] if item['item']['discussion'] is not None]

    for comment in nondead:
        discussion_id = comment['item']['id']
        urls = re.findall(r'href="(https://gist.github.com/\S+)"', comment['item']['text'])

        for url in urls:
            path = urlparse.urlsplit(url.rstrip('/)')).path
            document = path.split('/').pop()
            yield (document, discussion_id)

"""
Add a new entry to submission queue
"""
def submit(document, discussion_id):
    meta, error = gist_api.get(document)
    if meta is None:
        print error
        return False, error

    gist= dict(gist_id = document,
               discussion_id = discussion_id,
               description = unicode(meta.description) if unicode(meta.description) else 'Gist: ' + document,
               url = meta.html_url,
               content = unicode('\n'.join(meta.files[meta.files.keys()[0]].content.split('\n')[0:5])))

    model.redis.hmset("gist:#"+str(document), dict(payload=json.dumps(gist), status='OK'))
    model.index_add(document, discussion_id)

    return True, None

"""
Cron jobs
"""
def load_gists():
    model.redis.set('global.lastupdate', int(friendly_age.get_universal_time()))

    recent_gists = _fetch_gist_ids()
    for document, discussion_id in recent_gists:
        gist_key = "gist:#"+str(document)

        last_status = model.redis.hmget(gist_key, 'status')[0]
        retry_count = model.redis.hmget(gist_key, 'retry_count')[0]

        if (last_status != 'OK') and (retry_count is None or int(retry_count) < 10):
            print "checking #", retry_count
            result, error = submit(document, discussion_id)
            if(not result):
                model.redis.hmset(gist_key, dict(status='ERR',message=error))
                model.redis.hincrby(gist_key, 'retry_count')                
        else:
            if last_status == 'OK':
                print "skipping OK"
            else:
                model.redis.hmset(gist_key, dict(status='DEAD'))
                print "skipping DEAD", retry_count, model.redis.hmget(gist_key, 'message')[0]

"""
Db
"""
def kill_old():
    for key in model.index_clear_range(0, -501):
        model.redis.delete(key)

def flush_db():
    model.redis.flushdb()

    model.index_clear()

"""
Stats
"""
def info():
    stat = {}
    stat['updated_time'] = model.redis.get('global.lastupdate')
    stat['redis_info'] = model.redis.info()

    print json.dumps(stat)
    print "keys ", stat['redis_info']['db0']['keys']
    print "last update", friendly_age.friendly_age(int(model.redis.get('global.lastupdate')))
