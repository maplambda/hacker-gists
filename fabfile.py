import re
import urlparse
import json

from hackergists import thriftdb
from hackergists import model
from hackergists import friendly_age
from hackergists import gist as gist_api

"""
Helpers
"""
def counter():
    d = {}
    def make_counter(item=None):
        if item is not None:
            if d.has_key(item):
                d[item] += 1
            else:
                d[item] = 1
        return d
    return make_counter

"""
Application
"""
def iter_hn_gists():
    """Search Hacker News for recent Gists. Yield  gist_id, hn_id"""
    thrift = thriftdb.ThriftDb('http://api.thriftdb.com', 'api.hnsearch.com', 'items')
    criteria = {'limit' : 100,
                     'sortby' : 'create_ts desc',
                          'q' : 'gist.github.com'}

    items = thrift.search(**criteria)

    for item in items['results']:
        hn_id = item['item']['id']

        if 'submission' == item['item']['type'] and item['item']['url'] is not None:
            gist_id = item['item']['url'].split('/')[-1]
            yield gist_id, hn_id

        if  'comment' == item['item']['type']:
            urls = re.findall(r'href="(https://gist.github.com/\S+)"', item['item']['text'])
            for url in urls:
                path = urlparse.urlsplit(url.rstrip('/)')).path
                gist_id = path.split('/')[-1]
                yield gist_id, hn_id

"""
Cron jobs
"""
def load_gists():
    stats = counter()

    hn_gists = iter_hn_gists()
    for gist_id, hn_id in hn_gists:
        print "Checking gist_id: {0} hn_id: {1}".format(gist_id, hn_id)

        if not model.exists(gist_id):
            document, error = gist_api.get(gist_id)
            if document is not None:
                gist = {'gist_id' : gist_id,
                       'hn_id' : hn_id,
                       'description' : unicode(document.description) if unicode(document.description) else 'Gist: ' + gist_id,
                       'url' : document.html_url,
                       'content' : unicode('\n'.join(document.files[document.files.keys()[0]].content.split('\n')[0:5]))}

                stats("OK")
                print(model.add(gist))
            else:
                #mark retry
                retry = model.retry(gist_id, error)
                stats(retry)
                print(error, "hn id ", hn_id)
        else:
            stats("SKIPPED")
            print("SKIPPED")

    print(stats())

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
    stat = {'keys' : model.redis.info()['db0']['keys'],
            'used_memory' :  model.redis.info()['used_memory_human'],
            'last_save_time' :  model.redis.info()['last_save_time'],
            'last_save_time' :  friendly_age.friendly_age(int(model.redis.info()['last_save_time']))}

    print(model.redis.info())
    print stat

