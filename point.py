from fractions import Fraction
from fract import float_of_fract
from matrix import matrixmult

class FloatPoint(tuple):
    def __new__(self,x,y):
        assert type(x) == type(0.0)
        assert type(y) == type(0.0)
        return super(FloatPoint,self).__new__(self,tuple((x,y))) 

class Point(tuple):
    def __new__(self,x,y):
        assert type(x) == Fraction
        assert type(y) == Fraction
        return super(Point,self).__new__(self,tuple((x,y))) 

    def toFloat(self):
        return FloatPoint(float_of_fract(self[0]),float_of_fract(self[1]))

    def offset(self,p):
        return Point(p[0]+self[0],p[1]+self[1])

    def invert(self):
        return Point(-self[0],-self[1])

    def transform(self,mat):
        m = matrixmult(mat,[[self[0]],[self[1]],[1]])
        return Point(m[0][0],m[1][0])
