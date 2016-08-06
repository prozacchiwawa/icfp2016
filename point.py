from fractions import Fraction
from fract import float_of_fract

class FloatPoint(tuple):
    def __init__(self,x,y):
        return super(Point,self).__new__(self,tuple((x,y))) 

class Point(tuple):
    def __new__(self,x,y):
        return super(Point,self).__new__(self,tuple((x,y))) 

    def toFloat(self):
        return FloatPoint(float_of_fract(self[0]),float_fo_fract(self[1]))
