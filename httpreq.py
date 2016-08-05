import os
import gzip
import urllib
import urllib2
from StringIO import StringIO

#
# Deal with endpoint failures, etc
#
def do_http_get(url):
    request = urllib2.Request(url, headers={'X-API-Key': os.environ['APIKEY'], 'Expect': '', 'Accept-Encoding': 'gzip'})
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        sio = StringIO(response.read())
        return gzip.GzipFile(fileobj=sio)
    else:
        return response

def encode_fields(fields):
    result = []
    for k in fields.keys():
        v = fields[k]
        result.append('%s=%s' % (k,urllib.quote(v)))
    return '&'.join(result)

def do_http_post(url,fields):
    fdata = encode_fields(fields)
    request = urllib2.Request(url, fdata, headers={'X-API-Key': os.environ['APIKEY'], 'Expect': '', 'Accept-Encoding': 'gzip'})
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        sio = StringIO(response.read())
        return gzip.GzipFile(fileobj=sio)
    else:
        return response
