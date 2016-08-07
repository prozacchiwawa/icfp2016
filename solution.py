import matrix
from segment import Segment
from fractions import Fraction

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
        segs = [s.transform(transform) for s in segs]
    else:
        # Rotate it
        slope = Segment(leftmost, topmost).slope()
        shearY = [[1,0,0],[Fraction(1,slope),1,0],[0,0,1]]
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
        segshear = [s.transform(shearY) for s in segshear]
        segs = segshear
    points = gather_points(segs)
    xsorted = sorted(points, key=lambda p: p[0])
    ysorted = sorted(points, key=lambda p: p[1])
    # We might have damaged the scale by undoing the rotation using shear
    xscale = xsorted[-1][0] - xsorted[0][0]
    yscale = ysorted[-1][1] - ysorted[0][1]
    print xscale, yscale
    transform = [[Fraction(1,xscale),0,0],[0,Fraction(1,yscale),0],[0,0,1]]
    squaresegs = [s.transform(transform) for s in segs]
    points = gather_points(squaresegs)
    # Translate it
    xsorted = sorted(points, key=lambda p: p[0])
    ysorted = sorted(points, key=lambda p: p[1])
    xmin = xsorted[0][0]
    ymin = ysorted[0][1]
    transform = matrix.translation(-xmin,-ymin)
    segs = [s.transform(transform) for s in squaresegs]
    return segs
