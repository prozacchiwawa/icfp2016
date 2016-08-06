from segment import FloatSegment, Segment, IndexSegment
from point import FloatPoint, Point
from math import sqrt, fabs
from basic import epsilon

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
            ci1 = i1.toFloat()
            ci2 = i2.toFloat()
            j1 = pts[poly[j][0]]
            j2 = pts[poly[j][1]]
            cj1 = j1.toFloat()
            cj2 = j2.toFloat()
            if crossed_lines(FloatSegment(ci1,ci2),FloatSegment(cj1,cj2)):
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

def poly_segments_to_indices(polygon):
    index_chain = []
    while len(index_chain) != len(polygon):
        last = polygon[0][0]
        for p in polygon:
            if p[0] == last:
                last = p[1]
                index_chain.append(p[0])
    return index_chain

class TransformedSegment:
    def __init__(self,transform,points,polygon,poly_idx,edge_idx):
        assert type(polygon[0]) == IndexSegment
        self.points = points
        self.original_edge_idx = edge_idx
        self.original_poly_idx = poly_idx
        self.original_indices = edge = polygon[edge_idx]
        assert type(edge) == IndexSegment
        self.transform = transform
        self.segment_ = Segment(self.points[self.original_indices[0]].transform(self.transform), self.points[self.original_indices[1]].transform(self.transform))

    def segment(self):
        return self.segment_

    def __repr__(self):
        return "TransformedSegment(%s,%s,original=%s)" % (self.original_poly_idx,self.original_edge_idx,self.original_indices)

class TransformedPoly:
    def __init__(self,transform,points,polygon,pidx):
        self.transform = transform
        self.points = points
        self.polygon = polygon
        self.pidx = pidx
        self.segments_ = [TransformedSegment(self.transform,self.points,self.polygon,self.pidx,s) for s in range(len(self.polygon))]

    def segments(self):
        return self.segments_

    def area(self):
        return poly_area(self.points, poly_segments_to_indices(self.polygon))
