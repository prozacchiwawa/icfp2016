import json
import sys

if len(sys.argv) == 1:
    print 'getprobs.py foo.snap'
    sys.exit(1)

x = json.loads(open(sys.argv[1]).read())
problems = x['problems']
for p in problems:
    pid = p['problem_id']
    h = p['problem_spec_hash']
    print '(sleep 1 && sh runapi.sh python blob.py %s > prob%s.prob)' % (h, pid)
