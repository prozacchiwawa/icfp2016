import json
from httpreq import do_http_get
import sys

url="http://2016sv.icfpcontest.org/api/snapshot/list"
def do_query():
    return json.load(do_http_get(url))

if __name__ == '__main__':
    objs = do_query()
    if 'latest' in sys.argv[1:]:
       latest_time = 0
       latest_obj = None
       for obj in objs["snapshots"]:
           if obj["snapshot_time"] > latest_time:
               latest_time = obj["snapshot_time"]
               latest_obj = obj
       print latest_obj
    else:
        print objs
