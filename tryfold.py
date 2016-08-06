from fractions import Fraction
import problem
from problem import Problem
from fract import float_of_fract, fract_dist
from math import sqrt, fabs, ceil, floor
from svgvis import SVGGallery

epsilon = 0.0000001

def triangle_area(a,b,c):
    p = (a+b+c) / 2
    return sqrt(p * (p - a) * (p - b) * (p - c))

# 
# Thanks http://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
# p1 & p2 are part of the first segment and p3 & p4 are part of the second segment.
# I0 and I1 are the pointers which get set when intersection point(s) are found.
#
# Returns: 0 - No intersection
#          1 - Unique intersection set in  I0
#          2 - Segment intersection set in [I0, I1]
#
# Test if two line segments [p1, p2] & [p3, p4] intersect
# To find orientation of ordered triplet (a, b, c).
# The function returns following values
# 0 --> a, b and c are collinear
# 1 --> Clockwise        (Right of line formed by the segment)
# 2 --> Counterclockwise (Left of line formed by the segment)
def orientation(a,b,c):
    val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
    if fabs(val) < epsilon:
        return 0 # collinear
    elif val > 0: # clock or counterclock wise
        return 1
    else:
        return 2

# Tests whether or not a point c is on the segment [a, b]
def pointOnLine(a,b,c):
    is_collinear = orientation(a,b,c)

    if (is_collinear == 0):
        if ( min(a[0], b[0]) <= c[0] and c[0] <= max(a[0], b[0])):
            if ( min(a[1], b[1]) <= c[1] and c[1] <= max(a[1], b[1]) ):
                return True

    return False

def doIntersect(p1,p2,p3,p4):
    o1 = orientation(p1, p2, p3)
    o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1)
    o4 = orientation(p3, p4, p2)

    # General case
    if (o1 != o2 and o3 != o4):
        return True

    # Collinear special cases
    if (o1 == 0 and pointOnLine(p1, p2, p3)):
        return True
    if (o2 == 0 and pointOnLine(p1, p2, p4)):
        return True
    if (o3 == 0 and pointOnLine(p3, p4, p1)):
        return True
    if (o4 == 0 and pointOnLine(p3, p4, p2)):
        return True

    return False

def segment_segment_intersection (la,lb):
    p1 = la[0]
    p2 = la[1]
    p3 = lb[0]
    p4 = lb[1]
    if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4:
        return False
    return doIntersect(p1, p2, p3, p4)

def crossed_lines(a,b):
    return segment_segment_intersection(a,b)

def planar_poly(pts,polyline):
    poly = []
    point_used = dict([(p,0) for p in range(len(pts))])
    for i in range(0,len(polyline)):
        coord = (polyline[i],polyline[(i+1)%len(polyline)])
        if coord[0] != coord[1]:
            point_used[coord[0]] += 1
            point_used[coord[1]] += 1
        poly.append(coord)
    for k in point_used.keys():
        if not point_used[k] in [2,0]:
            return False
    for i in range(0,len(poly)):
        for j in range(0,i):
            i1 = pts[poly[i][0]]
            i2 = pts[poly[i][1]]
            ci1 = (float_of_fract(i1[0]),float_of_fract(i1[1]))
            ci2 = (float_of_fract(i2[0]),float_of_fract(i2[1]))
            j1 = pts[poly[j][0]]
            j2 = pts[poly[j][1]]
            cj1 = (float_of_fract(j1[0]),float_of_fract(j1[1]))
            cj2 = (float_of_fract(j2[0]),float_of_fract(j2[1]))
            if crossed_lines((ci1,ci2),(cj1,cj2)):
                return False
    return True

# http://code.activestate.com/recipes/578275-2d-polygon-area/
def poly_area(pts, poly_):
    poly = [pts[p] for p in poly_]
    total = 0.0
    N = len(poly)
    for i in range(N):
        v1 = poly[i]
        v2 = poly[(i+1) % N]
        total += v1[0]*v2[1] - v1[1]*v2[0]
    return abs(total/2)

class Folder:
    def __init__(self,p):
        self.p = p
        # Come up with a set of plausible points
        self.points = []
        pointset = set([])
        for s in self.p.slist:
            if not s[0] in pointset:
                self.points.append(s[0])
            if not s[1] in pointset:
                self.points.append(s[1])
            pointset.add(s[0])
            pointset.add(s[1])
        print 'pointset %s' % pointset
        # Make a list of lines by vertex
        self.lines = []
        for line in self.p.slist:
            a = self.points.index(line[0])
            b = self.points.index(line[1])
            self.lines.append((a,b))
        # Break lines that contain points in the slist set
        lineset = set(self.lines)
        for s in [sa for sa in lineset]:
            for pp in pointset:
                p = self.points.index(pp)
                if s[0] == p or s[1] == p:
                    continue
                ss = (self.points[s[0]],self.points[s[1]])
                a = fract_dist(ss[0],ss[1])
                b = fract_dist(ss[1],pp)
                c = fract_dist(pp,ss[0])
                ta = triangle_area(a,b,c)
                print 'area of %s,%s,%s -> %s' % (a,b,c,ta)
                if ta < epsilon:
                    if s in lineset:
                        lineset.remove(s)
                    lineset.add((s[0],p))
                    lineset.add((p,s[1]))
        self.lines = [l for l in lineset]
        print 'lines %s' % (self.lines)
        # Make a list of polygons as lists of vertices
        # self.connections[n] will contain a set 
        self.connections = dict([(x,set()) for x in range(len(self.points))])
        for l in self.lines:
            self.connections[l[0]].add(l[1])
            self.connections[l[1]].add(l[0])
        print self.connections
        poly_candidates = [[k] for k in self.connections.keys()]
        poly_finished = []
        # As long as we can add a new point to each polygon candidate
        # Without crossing an existing line, add it.  If we reach
        # a point already in the candidate, then emit a finished
        # polygon and retire it.
        while len(poly_candidates):
            cand = poly_candidates[0]
            poly_candidates = poly_candidates[1:]
            for conn in self.connections[cand[0]]:
                if cand[-1] == conn and len(cand) > 2:
                    poly_finished.append(cand)
                elif not conn in cand:
                    proposed = [conn]+cand
                    if planar_poly(self.points,proposed):
                        poly_candidates.append(proposed)
        self.poly_finished = []
        poly_finished_sets = [set(p) for p in poly_finished]
        for i, pi in enumerate(poly_finished):
            for j in range(i+1, len(poly_finished)):
                if poly_finished_sets[i] == poly_finished_sets[j]:
                    break
            else:
                self.poly_finished.append(pi)
        print self.poly_finished
        poly_connections = dict([(l,set([])) for l in self.lines])
        print poly_connections
        for pi, p in enumerate(self.poly_finished):
            for i in range(len(p)):
                line = (p[i], p[(i+1)%len(p)])
                if line in poly_connections:
                    poly_connections[line].add(pi)
                else:
                    poly_connections[(line[1],line[0])].add(pi)
        print poly_connections
        # A square is made up of polygons built from the shapes in the skeleton.
        # We will generate a list of polygon combinations whose area sum is
        # exactly 1 as close as we can tell.
        polies = [[n] for n in range(len(self.poly_finished))]
        finished = []
        while any([sum([poly_area(self.points, self.poly_finished[p]) for p in poly]) < (1 - epsilon) for poly in polies]):
            newpolies = []
            for p in polies:
                poly = self.poly_finished[p[0]]
                for i in range(len(poly)):
                    side = (poly[i],poly[(i+1)%len(poly)])
                    if not side in poly_connections:
                        side = (side[1],side[0])
                    connected = poly_connections[side]
                    for c in connected:
                        newp = [c]+p
                        area = sum([poly_area(self.points, self.poly_finished[poly_]) for poly_ in newp])
                        if area < (1 + epsilon) and not newp in newpolies:
                            if area > (1 - epsilon):
                                finished.append(newp)
                            newpolies.append(newp)
            polies = newpolies
        self.candidate_solutions = finished

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage: tryfold.py [prob] [svg?]'
        sys.exit(1)
    p = problem.read(open(sys.argv[1]))
    f = Folder(p)
    g = SVGGallery()
    for sol in f.candidate_solutions:
        square = ceil(sqrt(len(sol)))
        segs = []
        square_tenth = square / 10.0
        SL = -square_tenth
        SH = square + square_tenth
        segs.append(((SL,SL),(SH,SL)))
        segs.append(((SL,SL),(SL,SH)))
        segs.append(((SH,SH),(SH,SL)))
        segs.append(((SH,SH),(SL,SH)))
        for i,ss in enumerate(sol):
            s = f.poly_finished[ss]
            y = floor(i / square) * 1.1
            x = (i % square) * 1.1
            for i,v in enumerate(s):
                p1 = f.points[v]
                p2 = f.points[s[(i+1)%len(s)]]
                p1 = (p1[0] + x, p1[1] + y)
                p2 = (p2[0] + x, p2[1] + y)
                segs.append((p1, p2))
        g.addFigure('#459', segs)
    
    if len(sys.argv) > 2:
        with open(sys.argv[2],'w') as outf:
            outf.write(g.draw())
