from point import Point, FloatPoint

class FloatSegment(tuple):
    def __new__(self,a,b):
        assert type(a) == FloatPoint
        assert type(b) == FloatPoint
        return super(FloatSegment,self).__new__(self,tuple((a,b)))

class Segment(tuple):
    def __new__(self,a,b):
        assert type(a) == Point
        assert type(b) == Point
        return super(Segment,self).__new__(self,tuple((a,b)))

class IndexSegment(tuple):
    def __new__(self,a,b):
        assert type(a) == type(0)
        assert type(b) == type(0)
        return super(IndexSegment,self).__new__(self,tuple((a,b)))
