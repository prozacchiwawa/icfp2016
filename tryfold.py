from fractions import Fraction
import problem
from problem import Problem
from fract import float_of_fract, fract_dist
from math import sqrt

def triangle_area(a,b,c):
    p = (a+b+c) / 2
    return sqrt(p * (p - a) * (p - b) * (p - c))

epsilon = 0.0000001

class Folder:
    def __init__(self,p):
        self.p = p
        # Come up with a set of plausible points
        self.points = []
        pointset = set([])
        for s in self.p.slist:
            if not s[0] in pointset:
                self.points.append(s[0])
            if not s[1] in pointset:
                self.points.append(s[1])
            pointset.add(s[0])
            pointset.add(s[1])
        # Make a list of lines by vertex
        self.lines = []
        for line in self.p.slist:
            a = self.points.index(line[0])
            b = self.points.index(line[1])
            self.lines.append((a,b))
        # Break lines that contain points in the slist set
        lineset = set(self.lines)
        allbroken = False
        while not allbroken:
            for s in [sa for sa in lineset]:
                for pp in pointset:
                    p = self.points.index(pp)
                    if s[0] == p or s[1] == p:
                        continue
                    ss = (self.points[s[0]],self.points[s[1]])
                    a = fract_dist(ss[0],ss[1])
                    b = fract_dist(ss[1],pp)
                    c = fract_dist(pp,ss[0])
                    ta = triangle_area(a,b,c)
                    if ta < epsilon and b < a:
                        lineset.remove(s)
                        lineset.add((s[0],p))
                        lineset.add((p,s[1]))
                        allbroken = True
        self.lines = [l for l in lineset]
        # Make a list of polygons as lists of vertices
        # self.connections[n] will contain a set 
        self.connections = dict([(x,set()) for x in range(len(self.points))])
        for l in self.lines:
            self.connections[l[0]].add(l[1])
            self.connections[l[1]].add(l[0])
        print self.connections
        # A square is made up of polygons built from the shapes in the skeleton

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'usage: tryfold.py [prob]'
        sys.exit(1)
    p = problem.read(open(sys.argv[1]))
    f = Folder(p)

