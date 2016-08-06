from fractions import Fraction
import problem
from problem import Problem
from fract import float_of_fract, fract_dist
from math import sqrt, fabs, ceil, floor
from svgvis import SVGGallery
from point import Point, FloatPoint
from segment import Segment, FloatSegment, IndexSegment
import matrix
from matrix import matrixmult
from basic import epsilon
from polygon import *

def transform_from_boundary(points,polygon,e1):
    # Points is a list of Point
    # polygon and prototype are lists of Segment
    # e1 is an index in polygon of an edge that has a match in prototype
    
    # Find matching edge in prototype
    segment = Segment(points[polygon[e1][0]],points[polygon[e1][1]])
    transform = matrix.reflection(segment)
    
    return transform

class FoldSpec:
    def __init__(self,folder,placed):
        self.folder = folder
        self.placed = placed

    def area(self):
        return sum([p.area() for p in self.placed])

    def getEdgesInPlay(self):
        for p in self.placed:
            for s in p.segments():
                adjacent = self.folder.getAdjacent(s.original_indices)
                for a in adjacent:
                    yield (a,s) # Polygon index, transformed segment

    def getSegments(self):
        segs = []
        for f in self.placed:
            segs.extend(f.segments())
        return segs

    def getPointsList(self,tseg):
        return [p.transform(tseg.transform) for p in self.folder.points]

    def withUnfold(self,poly_idx,tseg):
        pfin = self.folder.poly_finished[poly_idx]
        polygon = [IndexSegment(pfin[i],pfin[(i+1)%len(pfin)]) for i in range(len(pfin))]
        # Find tseg in polygon
        
        e1 = polygon.index(tseg.original_indices) if tseg.original_indices in polygon else polygon.index(tseg.original_indices.swap())
        points = self.getPointsList(tseg)
        transform = transform_from_boundary(points,polygon,e1)
        placed_plus = [TransformedPoly(transform,points,polygon,poly_idx)] + self.placed
        return FoldSpec(self.folder,placed_plus)

class Folder:
    def __init__(self,p):
        self.p = p
        # Come up with a set of plausible points
        self.points = []
        pointset = set([])
        for s in self.p.slist:
            print s
            assert type(s) == Segment
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
            print (line[0],line[1])
            a = self.points.index(line[0])
            b = self.points.index(line[1])
            self.lines.append(IndexSegment(a,b))
        # Break lines that contain points in the slist set
        lineset = set(self.lines)
        for s in [sa for sa in lineset]:
            for pp in pointset:
                p = self.points.index(pp)
                if s[0] == p or s[1] == p:
                    continue
                ss = Segment(self.points[s[0]],self.points[s[1]])
                a = fract_dist(ss[0],ss[1])
                b = fract_dist(ss[1],pp)
                c = fract_dist(pp,ss[0])
                ta = triangle_area(a,b,c)
                print 'area of %s,%s,%s -> %s' % (a,b,c,ta)
                if ta < epsilon:
                    if s in lineset:
                        lineset.remove(s)
                    lineset.add(Segment(s[0],p))
                    lineset.add(Segment(p,s[1]))
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
        self.poly_connections = dict([(l,set([])) for l in self.lines])
        for pi, p in enumerate(self.poly_finished):
            for i in range(len(p)):
                line = IndexSegment(p[i], p[(i+1)%len(p)])
                if line in self.poly_connections:
                    self.poly_connections[line].add(pi)
                else:
                    self.poly_connections[IndexSegment(line[1],line[0])].add(pi)
        print self.poly_connections

    def getAdjacent(self,iseg):
        if iseg in self.poly_connections:
            return self.poly_connections[iseg]
        else:
            return self.poly_connections[IndexSegment(iseg[1],iseg[0])]

    def getRootUnfold(self):
        pfin = self.poly_finished[0]
        polygon = [IndexSegment(pfin[i],pfin[(i+1)%len(pfin)]) for i in range(len(pfin))]
        return FoldSpec(self,[TransformedPoly(matrix.identity, self.points, polygon, 0)])

    def bruteAdjacentMethod(self):
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
                    side = IndexSegment(poly[i],poly[(i+1)%len(poly)])
                    if not side in self.poly_connections:
                        side = IndexSegment(side[1],side[0])
                    connected = self.poly_connections[side]
                    for c in connected:
                        newp = [c]+p
                        area = sum([poly_area(self.points, self.poly_finished[poly_]) for poly_ in newp])
                        if area < (1 + epsilon) and not newp in newpolies:
                            if area > (1 - epsilon):
                                finished.append(newp)
                            newpolies.append(newp)
            polies = newpolies
        return finished
        # Candidate solutions is a list of lists of polygon indices in self.poly_finished
        # poly_connections is a dict of IndexSegment to set(polygon index) specifying connectivity

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage: tryfold.py [prob] [svg?]'
        sys.exit(1)
    p = problem.read(open(sys.argv[1]))
    f = Folder(p)
    g = SVGGallery()
    candidates = f.bruteAdjacentMethod()
    for sol in candidates:
        square = ceil(sqrt(len(sol)))
        segs = []
        square_tenth = square / 10.0
        SL = -square_tenth
        SH = square + square_tenth
        segs.append(FloatSegment(FloatPoint(SL,SL),FloatPoint(SH,SL)))
        segs.append(FloatSegment(FloatPoint(SL,SL),FloatPoint(SL,SH)))
        segs.append(FloatSegment(FloatPoint(SH,SH),FloatPoint(SH,SL)))
        segs.append(FloatSegment(FloatPoint(SH,SH),FloatPoint(SL,SH)))
        for i,ss in enumerate(sol):
            s = f.poly_finished[ss]
            y = floor(i / square) * 1.1
            x = (i % square) * 1.1
            for i,v in enumerate(s):
                p1 = f.points[v]
                p2 = f.points[s[(i+1)%len(s)]]
                p1 = FloatPoint(p1[0] + x, p1[1] + y)
                p2 = FloatPoint(p2[0] + x, p2[1] + y)
                segs.append(FloatSegment(p1, p2))
        g.addFigure('#459', segs)
    
    if len(sys.argv) > 2:
        with open(sys.argv[2],'w') as outf:
            outf.write(g.draw())
