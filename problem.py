import re
from fractions import Fraction

fraction_re_str = '(?P<xn>[-0-9]+)[ \t]*/[ \t]*(?P<xd>[-0-9]+)'
vertex_re_str = '%s,%s' % (fraction_re_str, fraction_re_str.replace('x','y'))
vertex_re = re.compile(vertex_re_str)
segment_re_str = '%s %s' % (vertex_re_str.replace('x','ax').replace('y','ay'), vertex_re_str.replace('x','bx').replace('y','by'))
segment_re = re.compile(segment_re_str)

def float_of_fract(p,off=0,scale=1):
    return (((p.numerator / p.denominator) * scale) + off)

class Problem:
    def __init__(self,plist,slist):
        self.plist = plist
        self.slist = slist
        xmin = 0
        ymin = 0
        xmax = 1
        ymax = 1
        for vlist in plist:
            for p in vlist:
                xmin = min(float_of_fract(p[0]), xmin)
                xmax = max(float_of_fract(p[0]), xmax)
                ymin = min(float_of_fract(p[1]), ymin)
                ymax = max(float_of_fract(p[1]), ymax)
        self.scale = 500 / max(xmax - xmin, ymax - ymin)
        self.xoff = 70 - (self.scale * xmin)
        self.yoff = 70 - (self.scale * ymin)

    def svgPolygon(self,vlist):
        points = ['%s,%s' % (float_of_fract(p[0],self.xoff,self.scale),float_of_fract(p[1],self.yoff,self.scale)) for p in vlist]
        return '<polygon fill="none" stroke="#ff8a65" stroke-width="2" points="%s"/>' % (' '.join(points))
    def toSVG(self):
        polygons = '\n'.join([self.svgPolygon(p) for p in self.plist])
        res = [
            '<?xml version="1.0" encoding="iso-8859-1"?>'
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="640" width="640" viewBox="0 0 640 640">',
            polygons,
            '</svg>'
        ]
        return '\n'.join(res)

    def __repr__(self):
        return "Problem(%s,%s)" % (self.plist,self.slist)

def read(flo):
    lines = filter(lambda x: len(x), [l.strip() for l in flo.readlines()])
    polygons = int(lines[0])
    l = 1
    plist = []
    for i in range(polygons):
        vlist = []
        vertices = int(lines[l])
        l += 1
        for j in range(vertices):
            m = vertex_re.match(lines[l])
            l += 1
            cx = Fraction(int(m.group('xn')),int(m.group('xd')))
            cy = Fraction(int(m.group('yn')),int(m.group('yd')))
            vlist.append((cx,cy))
        plist.append(vlist)
    skelsegs = int(lines[l])
    slist = []
    l += 1
    for i in range(skelsegs):
        m = segment_re.match(lines[l])
        l += 1
        ax = Fraction(int(m.group('axn')),int(m.group('axd')))
        ay = Fraction(int(m.group('ayn')),int(m.group('ayd')))
        bx = Fraction(int(m.group('bxn')),int(m.group('bxd')))
        by = Fraction(int(m.group('byn')),int(m.group('byd')))
        a = (ax,ay)
        b = (bx,by)
        slist.append((a,b))
    return Problem(plist, slist)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage problem.py prob.txt'
        sys.exit(1)
    p = read(open(sys.argv[1]))
    print p.toSVG()

