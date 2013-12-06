import requests
import urllib
import json

def get(url, params):
    print url+params
    return json.loads(requests.get(url, params=params).text)

def iter_flatten(data):
    for k, v in data.items():
        if hasattr(v, '__iter__'):
            for v2 in v:
                yield k,v2
        else:
            yield k,v    

class ThriftDb(object):
    def __init__(self, base, bucket, collection):
        self.base = base
        self.bucket = bucket
        self.collection = collection

    def search(self, **kwargs):
        filter = {}
        if 'filter' in kwargs:
            filter = kwargs['filter']
            del kwargs['filter']

        url = '/'.join([self.base, self.bucket, self.collection, '_search?'])
        params = urllib.urlencode(kwargs)
        if filter:
            filter_query =  ['filter' + '='.join(item) for item in iter_flatten(filter)]
            params = params + '&'.join(filter_query) 

        return get(url,params)

if __name__ == '__main__':
    t = ThriftDb('http://api.thriftdb.com', 'api.hnsearch.com', 'items')
    t.search(limit= '100',
        #pretty_print= 'true',
        sortby= 'create_ts desc',
        q= 'gist.github.com',
        filter= {'[fields][type]' : 'comment'})
