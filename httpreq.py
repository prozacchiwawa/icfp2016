import os
import gzip
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

    
