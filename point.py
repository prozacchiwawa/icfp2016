from fractions import Fraction
from fract import float_of_fract

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
