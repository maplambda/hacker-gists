import re
import urlparse

from hackergists import thriftdb
from hackergists import model
from hackergists import gist as gist_api

criteria = dict(limit = 100,
    sortby = 'create_ts desc',
    q = 'gist.github.com',
    filter = {'[fields][type]' : 'comment'})

thrift = thriftdb.ThriftDb('http://api.thriftdb.com', 'api.hnsearch.com', 'items')

def load_gists():
    notifications = []

    comments = thrift.search(**criteria)
    nondead = [item for item in comments['results'] if item['item']['discussion'] is not None]

    for comment in nondead:
        discussion_id = comment['item']['id']
        urls = re.findall(r'href="(https://gist.github.com/\S+)"', comment['item']['text'])
        for url in urls:
            gist = {}
            path = urlparse.urlsplit(url.rstrip('/)')).path
            document = path.split('/').pop()

            if model.exists(document):
                continue

            gist['gist_id'] = document
            gist['discussion_id'] = discussion_id
            meta = gist_api.get(document)
            if meta is None:
                notifications.append("Error getting gist data for: " + document)
                continue

            gist['description'] = unicode(meta.description) if unicode(meta.description) else 'Gist: ' + document
            gist['url'] = meta.html_url
            gist['content'] = '\n'.join(meta.files[meta.files.keys()[0]]\
                .content.split('\n')[0:5])   

            model.store(gist, document)
            model.index_add(id=document, score=discussion_id)

    print "notifications: " + ','.join(notifications)
    print "latest gist is: " + str(model.latest_gist())
    print "recent gists: " + str(model.recent_gists())

def kill_old():
    #cause 400 ought to be enough
    for key in model.index_clear_range(0, -401):
        model.delete(key)

def flush_db():
     model.flush()
     model.index_clear()
