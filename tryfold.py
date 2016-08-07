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
import solution
import copy
import area
import scipy.spatial
from scipy.spatial import ConvexHull

def overlaps(points1, points2):
    print 'points1',points1
    print 'points2',points2
    from shapely.geometry import Polygon
    overlap_area = 0
    polygon1 = Polygon(points1)
    polygon2 = Polygon(points2)
    overlap_area = polygon1.intersection(polygon2).area
    print "overlap: ", overlap_area
    print 'epsilon ', epsilon
    return overlap_area > epsilon

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
        
    area = poly_area_indexed(rational_points, hull.vertices)
    num_points = len(hull_points)
    angle_delta = fmod(angle - (pi/2), 2*pi)
    print "IsSquare: area:", area, "Num Points: ", num_points, "Angle Delta from 90 degrees, in radians: ", angle_delta
    return area == 1 and num_points == 4 and abs(angle_delta) < epsilon

def edge_check_ok(unfolded):
    assert type(unfolded) == FoldSpec
    # Check that each poly shares at least 2 points with other polygons
    # print "unfolded.placed: ", type(unfolded.placed), "(",unfolded.placed,")"
    for i,p in enumerate(unfolded.placed):
        points_i = set(p.getPolyPointList())
        for j in range(i+1,len(unfolded.placed)):
            points_j = set(unfolded.placed[j].getPolyPointList())
            points_both = points_j.intersection(points_i)
            if len(points_j) < 2:
                return False
            
    return True

# https://stackoverflow.com/questions/10301000/python-connected-components
# Does this work on bidirectional graphs?
def connected_components(neighbors):
    seen = set()
    def component(node):
        nodes = set([node])
        while nodes:
            node = nodes.pop()
            seen.add(node)
            nodes |= neighbors[node] - seen
            yield node
    for node in neighbors:
        if node not in seen:
            yield component(node)
            
def connected_graph(fs):
    edges = [ s.segment() for s in fs.getSegments() ]
    # build graph
    from collections import defaultdict
    old_graph = defaultdict(list)
    for edge in edges:
        old_graph[edge[0]].append(edge)
        old_graph[edge[1]].append(edge)
        
    # check connectivity
    components = []
    new_graph = {node: set(each for edge in edges for each in edge)
             for node, edges in old_graph.items()}
    for component in connected_components(new_graph):
        c = set(component)
        components.append([edge for edges in old_graph.values()
                            for edge in edges
                            if c.intersection(edge)])
    if len(components) == 1:
        return True
    else:
        print components
        return False
    
class FoldSpec(object):
    def __init__(self,folder,points,placed,composition,prevarea,minpt,maxpt,outer_edges):
        self.folder = folder
        self.points = points
        self.placed = placed
        self.points_ = {}
        self.ownarea_ = self.placed[0].area()
        self.area_ = prevarea + self.ownarea_
        self.segments_ = None
        self.composition_ = copy.deepcopy(composition)
        self.minpt = minpt
        self.maxpt = maxpt
        self.outer_edges = copy.deepcopy(outer_edges)
        #print "FoldSpec: outer_edges", self.outer_edges
        
        if not self.ownarea_ in self.composition_:
            self.composition_[self.ownarea_] = 1
        else:
            self.composition_[self.ownarea_] += 1
            
    def hasOverlap(self):
        candidate_poly = self.placed[0]
        current_polys = self.placed[1:]
        for p in current_polys:
            if overlaps(p.getPolyPointList(), candidate_poly.getPolyPointList()):
                return True
        return False
                
    def area(self):
        return self.area_

    def getEdgesInPlay(self):
        for i, p in enumerate(self.placed):
            for s in p.segments():
                adjacent = self.folder.getAdjacent(s.original_indices)
                for a in adjacent:
                    yield (a,s,i) # Polygon index, transformed segment, placement idx

    def getSegments(self):
        if self.segments_:
            return self.segments_
        self.segments_ = []
        for f in self.placed:
            self.segments_.extend(f.segments())
        return self.segments_

    def getPointsList(self,points,tseg):
        return [p.transform(tseg.transform) for p in points]

    def withUnfold(self,poly_idx,tseg,placement_idx):
        pfin = self.folder.poly_finished[poly_idx]
        polygon = [IndexSegment(pfin[i],pfin[(i+1)%len(pfin)]) for i in range(len(pfin))]

        # Find tseg in polygon
        e1 = polygon.index(tseg.original_indices) if tseg.original_indices in polygon else polygon.index(tseg.original_indices.swap())
        points = self.getPointsList(self.placed[placement_idx].points,tseg)
        transform = transform_from_boundary(points,polygon,e1)
        placed_new = TransformedPoly(transform,points,polygon,poly_idx)

        # Important: this does not take into account new
        # outer edges created by folds from internal segments 
        # (those fully inside outer bounding polygon)
        if tseg in self.outer_edges:
            for edge in placed_new:
                self.outer_edges.append(edge)
            # Remove outer edge we just folded across 
            self.outer_edges.remove(e1/tseg)
        placed_plus = [placed_new] + self.placed
        minpt = self.minpt
        maxpt = self.maxpt
        for pt_ in polygon:
            for pt in [points[pt_[0]].transform(transform),points[pt_[1]].transform(transform)]:
                if pt[0] < minpt[0]:
                    minpt = Point(pt[0],minpt[1])
                if pt[0] > maxpt[0]:
                    maxpt = Point(pt[0],maxpt[1])
                if pt[1] < minpt[1]:
                    minpt = Point(minpt[0],pt[1])
                if pt[1] > maxpt[1]:
                    maxpt = Point(maxpt[0],pt[1])

        fs = FoldSpec(self.folder,points,placed_plus,self.composition_,self.area_,minpt,maxpt, self.outer_edges)

        #if not edge_check_ok(fs):
        if not connected_graph(fs):
            print 'writing fail'
            g = SVGGallery()
            with open('fail.svg','w') as f:
                old = []
                for p in self.placed:
                    old.extend(p.segments())
                g.addFigure('#f33', [s.segment() for s in placed_new.segments()], tseg, 10)
                g.appendFigure('#891', [s.segment() for s in old])
                reflectSeg = (points[polygon[e1][0]],points[polygon[e1][1]])
                g.appendFigure('#731', [reflectSeg])
                probsegs = self.folder.segmentsOfPoly(poly_idx)
                poly_verts = ["%s,%s" % (p[0],p[1]) for p in [self.folder.points[i] for i in self.folder.poly_finished[poly_idx]]]
                print "guilty poly %s" % poly_verts
                print "tseg original %s,%s" % (tseg.points[tseg.original_indices[0]], tseg.points[tseg.original_indices[1]])
                print "tseg figure %s,%s" % (points[tseg.original_indices[0]], tseg.points[tseg.original_indices[1]])
                print ("e1 ", e1, polygon, polygon[e1])
                print ("So reflect about edge", reflectSeg)
                g.addFigure('#33e', probsegs)
                f.write(g.draw())
                f.close()
            raise("Illegal fold!")

        return fs

class Folder:
    def __init__(self,p):
        self.p = p
        # Come up with a set of plausible points
        self.points = []
        pointset = set([])
        floatPointSet = set([])

        self.initial_outer_edges = []
        # This outer edge finding will only work on problems with one
        # "Problem Silhouette" polygon
        # assert len(self.p.plist) == 1
        if len(self.p.plist) == 1:
            for polygon in self.p.plist:
                for i,p in enumerate(polygon):
                    p2 = polygon[(i+1) % len(polygon)]
                    print type(p), p
                    #outer_edges.append(Segment(Point(p[0],p[1]),Point(p2[0],p2[1])))
                    self.initial_outer_edges.append(Segment(p,p2))
        
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

        self.areas = [Polygon([self.points[pt] for pt in p]).area for p in self.poly_finished]
        self.asolver = area.AreaSolver(self.areas,1.0)
        print 'asolver %s %s' % (self.asolver.good, self.asolver.avect)

    def segmentsOfPoly(self,poly_idx):
        result = []
        poly_len = len(self.poly_finished[poly_idx])
        poly = self.poly_finished[poly_idx]
        for i,p in enumerate(poly):
            result.append(Segment(self.points[poly[i]],self.points[poly[(i+1)%poly_len]]))
        return result

    def getAdjacent(self,iseg):
        if iseg in self.poly_connections:
            return self.poly_connections[iseg]
        else:
            return self.poly_connections[IndexSegment(iseg[1],iseg[0])]

    def getRootUnfolds(self):
        result = []
        for pfin in self.poly_finished:
            polygon = [IndexSegment(pfin[i],pfin[(i+1)%len(pfin)]) for i in range(len(pfin))]
            minpt = self.points[pfin[i]]
            maxpt = self.points[pfin[i]]
            result.append(FoldSpec(self,self.points,[TransformedPoly(matrix.identity, self.points, polygon, 0)],{},0,minpt,maxpt,self.initial_outer_edges))
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

    def unfoldsWithArea1(self, gen_filename, genji):
        from itertools import count
        cnt = count()
        unfold_queue = self.getRootUnfolds()
        s2 = sqrt(2)
        while len(unfold_queue):
            print len(unfold_queue)
            u = unfold_queue[0]
            unfold_queue = unfold_queue[1:]
            if genji:
                with open("%03d%s" % (next(cnt), gen_filename),'w') as gen_outfile:
                    #seg_i = [ s.original_indices for s in u.getSegments() ]
                    segs = [ s.segment() for s in u.getSegments() ]
                    total_polys = 0
                    print u.composition_
                    for c in u.composition_.values():
                        total_polys += c
                    print "placed: ", u.placed, "total_polys", total_polys
                    assert(len(u.placed) == total_polys)
                    genji.addFigure('#000', segs, "%d" % total_polys)
                    gen_outfile.write(genji.draw())
            area = u.area()
            if abs(area - 1.0) < epsilon:
                points = []
                segs = [s.segment() for s in u.getSegments()]
                for s in segs:
                    points.append(s[0])
                    points.append(s[1])
                usq = isUnitSquare(points)
                if usq:
                    print 'unit square %s' % points
                    yield u
                    return

            if u.maxpt[0] - u.minpt[0] > s2 and u.maxpt[1] - u.minpt[1] > s2:
                print 'exceeded %s,%s' % (u.maxpt[0] - u.minpt[0], u.maxpt[1] - u.minpt[1])
                continue
            
            composition = [pair for pair in u.composition_.iteritems()]
            if not self.asolver.satisfies(composition):
                print 'composition %s unsatisfiable' % (composition)
                continue

            unfolds = u.getEdgesInPlay()
            for (polygon,segment,pidx) in unfolds:
                unfolded = u.withUnfold(polygon,segment,pidx)
                if unfolded.area() <= 1 and not unfolded.hasOverlap():
                    unfold_queue = [unfolded] + unfold_queue
            unfold_queue = sorted(unfold_queue, key=lambda u: -u.area())

def applyTransforms(transforms,seg):
    for t in transforms:
        seg = seg.transform(t)
    return seg
    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage: tryfold.py [prob] [svg?] [gen_svgs?]'
        sys.exit(1)
    p = problem.read(open(sys.argv[1]))
    f = Folder(p)
    g = SVGGallery()
    genji = SVGGallery()
    
    candidates = []
    solcount = 0
    if len(sys.argv) > 3:
        candidates = f.unfoldsWithArea1(sys.argv[3], genji)
    else:
        candidates = f.unfoldsWithArea1(None, None)

    for i, sol in enumerate(candidates):
        unitsegs, transforms = solution.makeUnitSquare([s.segment() for s in sol.getSegments()])
        g.addFigure('#459', unitsegs)

        polygons = []
        for p in sol.placed:
            segments_with_indices = p.segments()
            segs = [s.segment() for s in segments_with_indices]
            print 'segs',segs
            idxs = [s.original_indices for s in segments_with_indices]
            print 'idxs',idxs
            transformed = [applyTransforms(transforms, s) for s in segs]
            print 'transformed',
            pres = solution.Polygon(idxs, transformed)
            polygons.append(pres)
        solution = solution.writeSolution(f.points, polygons)
        print solution
        with open('%s.%s' % (sys.argv[1],i),'w') as solf:
            solf.write(solution)

    if len(sys.argv) > 2:
        with open(sys.argv[2],'w') as outf:
            outf.write(g.draw())

