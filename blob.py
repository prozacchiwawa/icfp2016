import json
from httpreq import do_http_get

url="http://2016sv.icfpcontest.org/api/blob"
def do_blob(h):
    return do_http_get("%s/%s" % (url, h))

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage blob.py hash'
        sys.exit(1)
    print do_blob(sys.argv[1]).read()

