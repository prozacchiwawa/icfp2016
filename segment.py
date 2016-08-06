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

    def offset(self,p):
        return Segment(self[0].offset(p),self[1].offset(p))

    def no_slope(self):
        return self[0][0] == self[1][0]

    def slope(self):
        assert not self.no_slope()
        diffy = self[1][1] - self[0][1]
        diffx = self[1][0] - self[0][0]
        return diffy / diffx

    def transform(self,mat):
        return Segment(self[0].transform(mat), self[1].transform(mat))

class IndexSegment(tuple):
    def __new__(self,a,b):
        assert type(a) == type(0)
        assert type(b) == type(0)
        return super(IndexSegment,self).__new__(self,tuple((a,b)))

    def offset(self,n):
        return IndexSegment(self[0]+n,self[1]+n)
