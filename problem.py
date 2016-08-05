import re
from fractions import Fraction
from fract import float_of_fract
from svgvis import SVGGallery

fraction_re_str = '(?P<xn>[-0-9]+)[ \t]*(/[ \t]*(?P<xd>[-0-9]+))?'
vertex_re_str = '%s,%s' % (fraction_re_str, fraction_re_str.replace('x','y'))
vertex_re = re.compile(vertex_re_str)
segment_re_str = '%s %s' % (vertex_re_str.replace('x','ax').replace('y','ay'), vertex_re_str.replace('x','bx').replace('y','by'))
segment_re = re.compile(segment_re_str)

class Problem:
    def __init__(self,plist,slist):
        self.plist = plist
        self.slist = slist
        self.svg = SVGGallery()
        polygonSegs = []
        for poly in self.plist:
            for i,p in enumerate(poly):
                polygonSegs.append((p,poly[(i+1)%len(poly)]))
                
        self.polygonGlyph = self.svg.addFigure('#974', polygonSegs)
        self.skeletonGlyph = self.svg.addFigure('#a31', self.slist)

    def toSVG(self):
        return self.svg.draw()

    def __repr__(self):
        return "Problem(%s,%s)" % (self.plist,self.slist)

def intn(s):
    if s is None:
        return 1
    else:
        return int(s)

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
            if not m:
                print 'problem parsing %s' % (lines[l])
            cx = Fraction(int(m.group('xn')),intn(m.group('xd')))
            cy = Fraction(int(m.group('yn')),intn(m.group('yd')))
            vlist.append((cx,cy))
        plist.append(vlist)
    skelsegs = int(lines[l])
    slist = []
    l += 1
    for i in range(skelsegs):
        m = segment_re.match(lines[l])
        l += 1
        ax = Fraction(int(m.group('axn')),intn(m.group('axd')))
        ay = Fraction(int(m.group('ayn')),intn(m.group('ayd')))
        bx = Fraction(int(m.group('bxn')),intn(m.group('bxd')))
        by = Fraction(int(m.group('byn')),intn(m.group('byd')))
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

