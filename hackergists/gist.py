import urllib2
import json
import StringIO

endpoint = 'https://api.github.com/gists/'

class Gist(dict):
    def __init__(self, data):
        self.d = data

    def keys(self):
        return self.d.keys()

    def __getattr__(self, name):
        if self.d.has_key(name):
            
            item = self.d[name]
            if hasattr(item, 'keys'):
                g = Gist(self.d[name])
                for k,v in  self.d[name].iteritems():
                    g[k]=Gist(v)

                return g
            else:
                return self.d[name]
        else: raise AttributeError, name

def get(id):
    try:
        return Gist(json.load(urllib2.urlopen(endpoint+ id))), None
    #404 
    except urllib2.HTTPError as e:
        return None, "HTTP error on: %s (%s)" % (id, e)
    #gists may contain png see: 2206278
    except UnicodeDecodeError:
        return None, "UnicodeDecodeError on " + id
