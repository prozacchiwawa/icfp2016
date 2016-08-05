import urllib2
import json
from httpreq import do_http_get

url="http://2016sv.icfpcontest.org/api/hello"
def do_hello():
    return json.load(do_http_get(url))

if __name__ == '__main__':
    print do_hello()
