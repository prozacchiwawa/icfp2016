import tryfold
import unittest
from segment import Segment
from point import Point
from fractions import Fraction
import matrix

class TestIntersect(unittest.TestCase):
    def test_bowtie(self):
        y = [0,1,2,3]
        pts = [Point(Fraction(0),Fraction(0)),Point(Fraction(1),Fraction(1)),Point(Fraction(1),Fraction(0)),Point(Fraction(0),Fraction(1))]
        self.assertFalse(tryfold.planar_poly(pts,y))
    def test_prob16(self):
        # y = 
        # pts = [(-0.2, 2.2), (0.0, 0.625), (2.2, 2.2), (0.0, 1.1), (-0.2, -0.2), (0.3, 0.7000000000000001), (1.1, 0.0), (1.1, 0.625), (2.1, 0.0), (0.0, 0.0), (1.0, 1.225), (-0.3, 0.4), (2.1, 0.125), (1.0, 1.1), (1.0, 0.0), (2.2, -0.2), (1.0, 0.125)]
        pass

    def test_poly_from_boundary(self):
        p1 = Point(Fraction(2),Fraction(2))
        p2 = Point(Fraction(3),Fraction(4))
        p3 = Point(Fraction(4),Fraction(2))
        sp1 = Point(Fraction(1),Fraction(3))
        sp2 = Point(Fraction(2),Fraction(1))
        isotri = [
            Segment(p1,p2),
            Segment(p2,p3),
            Segment(p3,p1)
        ]
        isosquare = [
            Segment(p2,p3),
            Segment(p3,sp2),
            Segment(sp2,sp1),
            Segment(sp1,p2)
        ]
        spi1 = Point(Fraction(5),Fraction(5))
        spi2 = Point(Fraction(6),Fraction(3))
        (pm, pt) = tryfold.poly_from_boundary(isotri, 1, isosquare)
        assert pt[0] == Segment(p2,p3)
        assert pt[1] == Segment(p3,spi2)
        assert pt[2] == Segment(spi2,spi1)
        assert pt[3] == Segment(spi1,p2)

if __name__ == '__main__':
    unittest.main()
