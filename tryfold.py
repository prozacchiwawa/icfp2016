from fractions import Fraction
import problem
from problem import Problem
from fract import float_of_fract, fract_dist
from math import sqrt, fabs, ceil, floor, atan, atan2, pi, fmod
from svgvis import SVGGallery
from point import Point, FloatPoint
from segment import Segment, FloatSegment, IndexSegment
import matrix
from matrix import matrixmult
from basic import epsilon
from polygon import *
import scipy.spatial
from scipy.spatial import ConvexHull

def transform_from_boundary(points,polygon,e1):
    # Points is a list of Point
    # polygon and prototype are lists of Segment
    # e1 is an index in polygon of an edge that has a match in prototype
    
    # Find matching edge in prototype
    segment = Segment(points[polygon[e1][0]],points[polygon[e1][1]])
    transform = matrix.reflection(segment)
    
    return transform

# passing in both so we can recover the rational points via index
def isUnitSquare(rational_points):
    # xxx rpoints and points must correspond xxx    
    points = [ p.toFloat() for p in rational_points ]
    hull = ConvexHull(points)
    hull_points = [ rational_points[i] for i in hull.vertices ]
    line1 = Segment(Point(hull_points[0][0],hull_points[0][1]), Point(hull_points[1][0], hull_points[1][1]))
    line2 = Segment(Point(hull_points[1][0],hull_points[1][1]), Point(hull_points[2][0], hull_points[2][1]))

    # hull_points are guaranteed to be in counterclockwise order
    angle = None
    if line1.no_slope() and (not line2.no_slope() and line2.slope() == 0):
        angle = pi / 2
    elif line2.no_slope() and (not line1.no_slope() and line1.slope() == 0):
        angle = pi / 2
    else:
        l1f = line1.toFloat()
        l2f = line2.toFloat()
        print "lines %s %s" % (l1f, l2f)
        l1d = FloatPoint(l1f[1][0]-l1f[0][0],l1f[1][1]-l1f[0][1])
        l2d = FloatPoint(l2f[1][0]-l2f[0][0],l2f[1][1]-l2f[0][1])
        angle = atan2(l2d[1], l2d[0]) - atan2(l1d[1], l1d[0])
        
    area = poly_area(rational_points, hull.vertices)
    num_points = len(hull_points)
    angle_delta = fmod(angle - (pi/2), 2*pi)
    print "IsSquare: area:", area, "Num Points: ", num_points, "Angle Delta from 90 degrees, in radians: ", angle_delta
    return area == 1 and num_points == 4 and abs(angle_delta) < epsilon

class FoldSpec:
    def __init__(self,folder,points,placed):
        self.folder = folder
        self.points = points
        self.placed = placed
        self.points_ = {}
        self.area_ = None
        self.segments_ = None

    def area(self):
        if not self.area_:
            self.area_ = sum([p.area() for p in self.placed])
        return self.area_

    def getEdgesInPlay(self):
        for p in self.placed:
            for s in p.segments():
                adjacent = self.folder.getAdjacent(s.original_indices)
                for a in adjacent:
                    yield (a,s) # Polygon index, transformed segment

    def getSegments(self):
        if self.segments_:
            return self.segments_
        self.segments_ = []
        for f in self.placed:
            self.segments_.extend(f.segments())
        return self.segments_

    def getPointsList(self,tseg):
        if tseg in self.points_:
            return self.points_[tseg]
        else:
            self.points_[tseg] = res = [p.transform(tseg.transform) for p in self.points]
            return res

    def withUnfold(self,poly_idx,tseg):
        pfin = self.folder.poly_finished[poly_idx]
        polygon = [IndexSegment(pfin[i],pfin[(i+1)%len(pfin)]) for i in range(len(pfin))]
        # Find tseg in polygon
        
        e1 = polygon.index(tseg.original_indices) if tseg.original_indices in polygon else polygon.index(tseg.original_indices.swap())
        points = self.getPointsList(tseg)
        transform = transform_from_boundary(points,polygon,e1)
        placed_plus = [TransformedPoly(transform,points,polygon,poly_idx)] + self.placed
        return FoldSpec(self.folder,points,placed_plus)

class Folder:
    def __init__(self,p):
        self.p = p
        # Come up with a set of plausible points
        self.points = []
        pointset = set([])
        floatPointSet = set([])
        for s in self.p.slist:
            print s
            assert type(s) == Segment
            if not s[0] in pointset:
                self.points.append(s[0])
            if not s[1] in pointset:
                self.points.append(s[1])
            pointset.add(s[0])
            pointset.add(s[1])
            floatPointSet.add( (float_of_fract(s[0][0]), float_of_fract(s[0][1])) )
            floatPointSet.add( (float_of_fract(s[1][0]), float_of_fract(s[1][1])) )
        print 'pointset %s' % pointset
        print 'Is square: ', isUnitSquare(list(pointset))

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
                    print s, ss
                    if s in lineset:
                        lineset.remove(s)
                    lineset.add(IndexSegment(s[0],p))
                    lineset.add(IndexSegment(p,s[1]))
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

    def getRootUnfolds(self):
        result = []
        for pfin in self.poly_finished:
            polygon = [IndexSegment(pfin[i],pfin[(i+1)%len(pfin)]) for i in range(len(pfin))]
            result.append(FoldSpec(self,self.points,[TransformedPoly(matrix.identity, self.points, polygon, 0)]))
        return result

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

    def unfoldsWithArea1(self):
        unfold_queue = self.getRootUnfolds()
        while len(unfold_queue):
            print len(unfold_queue)
            u = unfold_queue[0]
            unfolds = u.getEdgesInPlay()
            unfold_queue = unfold_queue[1:]
            for (polygon,segment) in unfolds:
                unfolded = u.withUnfold(polygon,segment)
                area = unfolded.area()
                if abs(area - 1.0) < epsilon:
                    points = []
                    segs = [s.segment() for s in unfolded.getSegments()]
                    for s in segs:
                        points.append(s[0])
                        points.append(s[1])
                    usq = isUnitSquare(points)
                    if usq:
                        print 'unit square %s' % points
                        yield unfolded
                        return
                elif area < 1:
                    unfold_queue.append(unfolded)
            unfold_queue = sorted(unfold_queue, key=lambda u: -u.area())

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage: tryfold.py [prob] [svg?]'
        sys.exit(1)
    p = problem.read(open(sys.argv[1]))
    f = Folder(p)
    g = SVGGallery()
    candidates = f.unfoldsWithArea1()
    for sol in candidates:
        segs = [s.segment() for s in sol.getSegments()]
        g.addFigure('#459', segs)

    if len(sys.argv) > 2:
        with open(sys.argv[2],'w') as outf:
            outf.write(g.draw())
