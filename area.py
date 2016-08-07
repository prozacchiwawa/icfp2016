from math import floor, ceil
from fractions import Fraction, gcd

class ACoef(list):
    def __init__(self,vals,target):
        super(ACoef,self).__init__(self)
        self.extend([0 for v in vals])
        self.caps = [ceil(target/v) for v in vals]
        
    def incr(self):
        carry = 1
        n = 0
        while carry:
            self[n%len(self)] += 1
            if self[n%len(self)] >= self.caps[n%len(self)]:
                self[n%len(self)] = 0
                carry = 1
                n += 1
            else:
                carry = 0

class AreaSolver:
    def evalValues(self,m,adv):
        return sum([m * a for (m,a) in zip(m,adv)])

    def isSolution(self,m,adv):
        mod = (self.evalValues(self.areas[1:],self.avect[1:]) - self.target) / self.areas[0]
        return Fraction(mod).denominator == 1

    def __init__(self,areas,target):
        self.areas = sorted(areas, key=lambda a: -a)
        self.target = target

        # Goal: find integer solutions to ax + by + cz + ... = A
        
        m = [floor(target / a) for a in self.areas]
        
        # As quickly as possible, find a set of products mi * ai that 
        # satisfies

        self.avect = ACoef(self.areas,target)

        while not self.isSolution(self.areas,self.avect):
            self.avect.incr()

        self.gcdmatrix = [[0]*len(self.areas) for _ in range(len(self.areas))]
        for i in range(len(self.areas)):
            for j in range(len(self.areas)):
                self.gcdmatrix[i][j] = gcd(self.areas[i],self.areas[j])
