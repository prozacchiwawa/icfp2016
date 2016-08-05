import json
from httpreq import do_http_get, do_http_post

url='http://2016sv.icfpcontest.org/api/solution/submit'
def do_submit_solution(prob_id,sol):
    return do_http_post(url,{'problem_id': str(prob_id), 'solution_spec': sol})

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'solve.py prob_id sol.txt'
        sys.exit(1)
    res = do_submit_solution(int(sys.argv[1]), open(sys.argv[2]).read())
    print res.read()

