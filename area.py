from math import floor, ceil
from fractions import Fraction, gcd

class ACoef(list):
    def __init__(self,vals,target):
        super(ACoef,self).__init__(self)
        self.extend([0 for v in vals])
        self.caps = [floor(target/v) for v in vals]
        print self.caps
        
    def incr(self):
        carry = 1
        n = 0
        l = len(self)
        while carry and n < l:
            self[n] += 1
            if self[n] > self.caps[n]:
                self[n] = 0
                carry = 1
                n += 1
            else:
                break
        return n < l

class AreaSolver:
    def evalValues(self,m,adv):
        return sum([m * a for (m,a) in zip(m,adv)])

    def isSolution(self,m,adv):
        return (self.evalValues(self.areas,self.avect) - self.target) == 0

    def __init__(self,areas,target):
        self.areas = sorted(areas, key=lambda a: -a)
        self.target = target

        # Goal: find integer solutions to ax + by + cz + ... = A
        
        m = [floor(target / a) for a in self.areas]
        
        # As quickly as possible, find a set of products mi * ai that 
        # satisfies

        self.avect = ACoef(self.areas,target)

        self.good = True
        while not self.isSolution(self.areas,self.avect) and self.good:
            self.good = self.avect.incr()

        self.gcdmatrix = [[0]*len(self.areas) for _ in range(len(self.areas))]
        for i in range(len(self.areas)):
            for j in range(len(self.areas)):
                self.gcdmatrix[i][j] = gcd(self.areas[i],self.areas[j])

    def satisfies(self,copies):
        val = self.target - sum([c * a for (c,a) in copies])
        print val
        if val < 0:
            return False
        return AreaSolver(self.areas,val).good
