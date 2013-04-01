import re
import urlparse
import json

from hackergists import thriftdb
from hackergists import model
from hackergists import metrics
from hackergists import gist as gist_api
from hackergists import friendly_age

criteria = dict(limit = 100, sortby = 'create_ts desc',q = 'gist.github.com',
                filter = {'[fields][type]' : 'comment'})

thrift = thriftdb.ThriftDb('http://api.thriftdb.com', 'api.hnsearch.com', 'items')

# returns gist id, hn discussion id
def fetch_gist_ids():
    ids = []
    comments = thrift.search(**criteria)
    nondead = [item for item in comments['results'] if item['item']['discussion'] is not None]

    for comment in nondead:
        discussion_id = comment['item']['id']
        urls = re.findall(r'href="(https://gist.github.com/\S+)"', comment['item']['text'])
        for url in urls:
            gist = {}
            path = urlparse.urlsplit(url.rstrip('/)')).path
            document = path.split('/').pop()
            ids.append([document, discussion_id])
    return ids

def load_gists():
    metrics.set_label('hackergists.lastupdate', int(friendly_age.get_universal_time()))
    recent_gists = fetch_gist_ids()
    
    pipe = model.redis.pipeline()
    for document, discussion_id in recent_gists:
        pipe.exists(document)

    key_exists = pipe.execute()
    to_update = map(lambda x: x[0], filter(lambda x: x[1] == False, 
                    zip(recent_gists, key_exists))) 

    for document, discussion_id in to_update:
        meta, error = gist_api.get(document)
        if meta is None:
            metrics.set_label(document, error)
        else:
            gist = {}
            gist['gist_id'] = document
            gist['discussion_id'] = discussion_id
            gist['description'] = unicode(meta.description) if unicode(meta.description) else 'Gist: ' + document
            gist['url'] = meta.html_url
            gist['content'] = unicode('\n'.join(meta.files[meta.files.keys()[0]].content.split('\n')[0:5]))

            model.store(gist, document)
            model.index_add(score=discussion_id, id=document)
            
            metrics.clear_label(document)

def kill_old():
    for key in model.index_clear_range(0, -501):
        model.delete(key)

def flush_db():
    model.flush()
    model.index_clear()

def info():
    stat = {}
    stat['updated_time'] = metrics.get_label('hackergists.lastupdate')
    stat['errors'] = metrics.get_labels()
    stat['redis_info'] = model.info()

    print json.dumps(stat)
    print "errors ", len(stat['errors'])
    print "keys ", stat['redis_info']['db0']['keys']
    print "last update", stat['updated_time']

def updated():
    print friendly_age.friendly_age(int(metrics.get_label('hackergists.lastupdate')))

