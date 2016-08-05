import json
from httpreq import do_http_get

url="http://2016sv.icfpcontest.org/api/snapshot/list"
def do_query():
    return json.load(do_http_get(url))

if __name__ == '__main__':
    print do_query()
