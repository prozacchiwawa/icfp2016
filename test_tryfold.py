import tryfold
from tryfold import Folder
import unittest
from segment import Segment, IndexSegment
from point import Point
from fractions import Fraction
import matrix
import problem
import solution
from svgvis import SVGGallery

class TestIntersect(unittest.TestCase):
    def test_bowtie(self):
        y = [0,1,2,3]
        pts = [Point(Fraction(0),Fraction(0)),Point(Fraction(1),Fraction(1)),Point(Fraction(1),Fraction(0)),Point(Fraction(0),Fraction(1))]
        self.assertFalse(tryfold.planar_poly(pts,y))

    def test_poly_from_boundary(self):
        p1 = Point(Fraction(2),Fraction(2))
        p2 = Point(Fraction(3),Fraction(4))
        p3 = Point(Fraction(4),Fraction(2))
        sp1 = Point(Fraction(1),Fraction(3))
        sp2 = Point(Fraction(2),Fraction(1))
        points = [p1,p2,p3,sp1,sp2]
        isotri = [IndexSegment(0,1),IndexSegment(1,2),IndexSegment(2,0)]
        spi1 = Point(Fraction(5),Fraction(5))
        spi2 = Point(Fraction(6),Fraction(3))
        pt = tryfold.transform_from_boundary(points, isotri, 1)
        assert points[3].transform(pt) == spi1
        assert points[4].transform(pt) == spi2

    def test_unfold(self):
        p = problem.read(open('./prob/prob12.prob'))
        f = Folder(p)
        rootfold = f.getRootUnfolds()[0]
        unfolds = [rootfold.withUnfold(x[0],x[1],0) for x in rootfold.getEdgesInPlay()]
        best = filter(lambda x: x.area() == 1, unfolds)[0]
        segs = best.getSegments()
        g = SVGGallery()
        g.addFigure('#621',[s.segment() for s in segs])
        f = open('test.svg','w')
        f.write(g.draw())
        f.close()

    def test_unfold11(self):
        p = problem.read(open('./prob/prob11.prob'))
        f = Folder(p)
        rootfold = f.getRootUnfolds()[0]
        vlist = filter(lambda x: x[1].original_indices == IndexSegment(4,5), [x for x in rootfold.getEdgesInPlay()])
        g = SVGGallery()
        for v in vlist:
            unfold = rootfold.withUnfold(v[0],v[1],0)
            print 'area %s %s' % (unfold.area(), v)
            print [x.segment() for x in unfold.getSegments()]
            g.addFigure('#c54',[s.segment() for s in unfold.getSegments()])
        f = open('test2.svg','w')
        f.write(g.draw())
        f.close()

    def test_overlap_cull11(self):
        p = problem.read(open('./prob/prob11.prob'))
        f = Folder(p)
        rootfold = f.getRootUnfolds()[0]
        vlist = filter(lambda x: x[1].original_indices == IndexSegment(4,5), [x for x in rootfold.getEdgesInPlay()])
        g = SVGGallery()
        for v in vlist:
            unfold = rootfold.withUnfold(v[0],v[1],0)
            overlap = unfold.hasOverlap()
            if overlap:
                color = '#F00'
            else:
                color = '#0c0'
            print 'area %s %s' % (unfold.area(), v)
            print [x.segment() for x in unfold.getSegments()]
            g.addFigure(color,[s.segment() for s in unfold.getSegments()])
        f = open('overlap.svg','w')
        f.write(g.draw())
        f.close()

    def test_makeUnitSquare(self):
        points = [
            Point(Fraction(0),Fraction(3)),
            Point(Fraction(3),Fraction(7)),
            Point(Fraction(7),Fraction(4)),
            Point(Fraction(4),Fraction(0)),
            Point(Fraction(1),Fraction(9,4)),
            Point(Fraction(1),Fraction(13,3))
        ]
        segs = [
            Segment(points[0],points[4]),
            Segment(points[4],points[5]),
            Segment(points[5],points[0]),
            Segment(points[5],points[1]),
            Segment(points[1],points[2]),
            Segment(points[2],points[3]),
            Segment(points[3],points[4]),
            Segment(points[4],points[5])
        ]
        g = SVGGallery()
        g.addFigure("#333", segs)

        segs = solution.makeUnitSquare(segs)
        g.addFigure("#090", segs)

        segs = [Segment(Point(s[0][0],s[0][1]),Point(s[1][0],s[1][1])) for s in 
                ((Fraction(4, 3), Fraction(1, 3)), (Fraction(4, 3), Fraction(4, 3))), ((Fraction(4, 3), Fraction(4, 3)), (Fraction(1, 3), Fraction(4, 3))), ((Fraction(1, 3), Fraction(4, 3)), (Fraction(1, 3), Fraction(1, 1))), ((Fraction(1, 3), Fraction(1, 1)), (Fraction(1, 1), Fraction(1, 3))), ((Fraction(1, 1), Fraction(1, 3)), (Fraction(4, 3), Fraction(1, 3))), ((Fraction(1, 3), Fraction(1, 3)), (Fraction(1, 3), Fraction(1, 1))), ((Fraction(1, 3), Fraction(1, 1)), (Fraction(1, 1), Fraction(1, 3))), ((Fraction(1, 1), Fraction(1, 3)), (Fraction(1, 3), Fraction(1, 3)))]

        g.addFigure('#e32', segs)
        segs = solution.makeUnitSquare(segs)
        g.addFigure('#33e', segs)

        with open("test-sq.svg", 'w') as f:
            f.write(g.draw())

    def test_linejoin(self):
        points = [
            Point(Fraction(0),Fraction(0)),
            Point(Fraction(0),Fraction(1)),
            Point(Fraction(0),Fraction(2)),
            Point(Fraction(0),Fraction(3)),
            Point(Fraction(1),Fraction(1)),
            Point(Fraction(2),Fraction(2)),
            Point(Fraction(3),Fraction(3))
        ]
        tests = [
            (None, [
                Segment(points[0],points[1]),
                Segment(points[2],points[3])
            ]),
            (Segment(points[0],points[2]), [
                Segment(points[0],points[1]),
                Segment(points[1],points[2])
            ]),
            (Segment(points[0],points[5]), [
                Segment(points[0],points[4]),
                Segment(points[4],points[5])
            ]),
            (None, [
                Segment(points[0],points[4]),
                Segment(points[5],points[6])
            ])
        ]
        for (t_outcome,t_segments) in tests:
            got = solution.createLargerSegment(t_segments[0],t_segments[1])
            print 'want',t_outcome,'got',got,'from',t_segments
            assert t_outcome == got

if __name__ == '__main__':
    unittest.main()
