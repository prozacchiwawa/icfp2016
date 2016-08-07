import matrix
from segment import Segment
from fractions import Fraction
from polygon import poly_segments_to_indices, IndexSegment

def gather_points(segs):
    points = []
    for s in segs:
        points.append(s[0])
        points.append(s[1])
    return points

#
# Given a figure with shapes and overlapping lines formed into a square,
# discover a translation to the unit square, translate it, and output a
# proper contest solution.
#
def makeUnitSquare(segs):
    print 'insegs %s' % segs

    transforms = []

    # the topmost point and leftmost point must be on the hull
    points = gather_points(segs)

    xsorted = sorted(points, key=lambda p: p[0])
    ysorted = sorted(points, key=lambda p: p[1])

    leftset = set(filter(lambda x: x[0] == xsorted[0][0], xsorted))
    leftmost = xsorted[0]
    topmost = ysorted[0]

    nextleftmost = filter(lambda x: x[0] != leftmost[0], xsorted)[0]

    print "left %s next %s" % (leftmost, nextleftmost)
    print "leftset %s" % leftset

    if len(leftset) > 1:
        # It is upright
        left = leftmost[0]
        bottom = topmost[1] - 1
        transform = matrix.translation(-left, -bottom)
        transforms.append(transform)
        segs = [s.transform(transform) for s in segs]
    else:
        # Rotate it
        slope = Segment(leftmost, topmost).slope()
        shearY = [[1,0,0],[Fraction(1,slope),1,0],[0,0,1]]
        transforms.append(shearY)
        segshear = [s.transform(shearY) for s in segs]
        segs = segshear
        points = gather_points(segshear)
        ysorted = sorted(points, key=lambda p: p[0])
        ymin = ysorted[0][1]
        ymax = ysorted[-1][1]
        yminline = sorted(filter(lambda x: x[1] == ymin, ysorted), key=lambda p: p[0])
        ymaxline = sorted(filter(lambda x: x[1] == ymax, ysorted), key=lambda p: p[0])
        xmin = yminline[0]
        xmax = ymaxline[0]
        if xmin == xmax:
            raise("What to do here?")
        slope = Segment(xmin,xmax).slope()
        shearY = [[1,Fraction(-1,slope),0],[0,1,0],[0,0,1]]
        transforms.append(shearY)
        segshear = [s.transform(shearY) for s in segshear]
        segs = segshear
    points = gather_points(segs)
    xsorted = sorted(points, key=lambda p: p[0])
    ysorted = sorted(points, key=lambda p: p[1])
    # We might have damaged the scale by undoing the rotation using shear
    print 'xsorted', xsorted
    xscale = xsorted[-1][0] - xsorted[0][0]
    yscale = ysorted[-1][1] - ysorted[0][1]
    print xscale, yscale
    transform = [[Fraction(1,xscale),0,0],[0,Fraction(1,yscale),0],[0,0,1]]
    transforms.append(transform)
    squaresegs = [s.transform(transform) for s in segs]
    points = gather_points(squaresegs)
    # Translate it
    xsorted = sorted(points, key=lambda p: p[0])
    ysorted = sorted(points, key=lambda p: p[1])
    xmin = xsorted[0][0]
    ymin = ysorted[0][1]
    transform = matrix.translation(-xmin,-ymin)
    transforms.append(transform)
    segs = [s.transform(transform) for s in squaresegs]
    return segs, transforms

# Returns a segment if seg1 and seg2 join or None
def createLargerSegment(s1,s2):
    if s1.no_slope() and s2.no_slope():
        coords = set([s1[0],s1[1],s2[0],s2[1]])
        if len(coords) == 4:
            return None
        
        points = sorted(coords, key=lambda v: v[1])
        return Segment(points[0],points[2])
    elif s1.no_slope() or s2.no_slope():
        return None
    elif s1.slope() != s2.slope():
        return None
        
    coords = set([s1[0],s1[1],s2[0],s2[1]])
    if len(coords) == 4:
        return None

    points = sorted(coords, key=lambda v: v[0])
    return Segment(points[0],points[2])

def strizeFract(ft):
    if ft.denominator == 1:
        return str(ft.numerator)
    else:
        return '%s/%s' % (str(ft.numerator), str(ft.denominator))

def strizePoint(pt):
    print pt
    return '%s,%s' % (strizeFract(pt[0]),strizeFract(pt[1]))

def strizeFacet(f):
    return " ".join([str(len(f))] + [str(fe) for fe in f])

class Polygon:
    def __init__(self,index_list,pos_list):
        self.indices = index_list
        self.positions = pos_list

# Inputs sil_points_in, the points list from Folder
def writeSolution(sil_points_in,polygons):
    paper_points = []
    sil_points = []
    facets = []

    # Create aligned arrays with sil_points and paper_points corresponding
    # to paper_indices, which are index segments.
    for p in polygons:
        facet = []
        for i, s in enumerate(p.indices):
            pos = p.positions[i]
            if pos[0] in paper_points:
                pidx0 = paper_points.index(pos[0])
            else:
                pidx0 = len(paper_points)
                paper_points.append(pos[0])
                sil_points.append(sil_points_in[s[0]])
            if pos[1] in paper_points:
                pidx1 = paper_points.index(pos[1])
            else:
                pidx1 = len(paper_points)
                paper_points.append(pos[1])
                sil_points.append(sil_points_in[s[1]])
            iseg = IndexSegment(pidx0, pidx1)
            print 'pos',pos,'to index',iseg,'paper',paper_points
            facet.append(iseg)
        print 'got facet',facet
        facet = poly_segments_to_indices(facet)
        print 'got facet',facet
        facets.append(facet)

    print 'PAPER POINTS',paper_points
    print 'SIL   POINTS',sil_points

    return '\n'.join([
        str(len(paper_points)),
        '\n'.join([strizePoint(p) for p in paper_points]),
        str(len(facets)),
        '\n'.join(strizeFacet(f) for f in facets),
        '\n'.join(strizePoint(p) for p in sil_points)
    ])
