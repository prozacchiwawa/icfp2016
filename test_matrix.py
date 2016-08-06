from fractions import Fraction
from point import Point
from segment import Segment
import matrix

s_vert = Segment(Point(Fraction(10),Fraction(0)),Point(Fraction(10),Fraction(1)))
p_vert = Point(Fraction(11),Fraction(2))
m = matrix.reflection(s_vert)
print p_vert.transform(m)

s_m2 = Segment(Point(Fraction(3),Fraction(5)),Point(Fraction(4),Fraction(7)))
assert (not s_m2.no_slope())
assert s_m2.slope() == 2
p_slope = Point(Fraction(5),Fraction(4))
m = matrix.reflection(s_m2)
print p_slope.transform(m)

