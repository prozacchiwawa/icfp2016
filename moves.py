import problem
from problem import Problem
import fractions
from fractions import Fraction

import misc
from misc import intn

#import copy
#from copy import deepcopy

def fraction_from_string(str):
    num = 1
    denom = 1
    
    try:
        num,denom = str.split("/")
    except ValueError as e:
        num = str
        
    return Fraction(int(num), intn(denom))

# args is a list of strings
def create_move(cmd, args):
    # This is kinda crap.
    if cmd == "translate":
        x_str = args[0]
        y_str = args[1]

        x = fraction_from_string(x_str)
        y = fraction_from_string(y_str)
        
        return Move(cmd, [x,y])
    else:
        raise("Unknown move command: [", cmd, "]")

def translate(problem, arglist):
    x = arglist[0]
    y = arglist[1]

    print "translate: ", type(problem)
    assert( type(problem) == Problem )
    assert( type(x) == Fraction )
    assert( type(y) == Fraction )

    #new_polys = deepcopy(problem.plist)
    #new_lines = deepcopy(problem.slist)

    new_polys = []
    new_lines = []
    
    for polygon in problem.plist:
        vlist = []
        for vertex in polygon:
            vlist.append((vertex[0] + x, vertex[1] + y))
        new_polys.append(vlist)
            
    for line in problem.slist:
        #for line in s:
        a = line[0]
        b = line[1]
        print (a,b)
        new_lines.append( ((a[0]+x,a[1]+y), (b[0]+x,b[1]+y)) )

    # Note that Problem construtor wants tuples, not Fractions
    return Problem(new_polys, new_lines)
    
def rotate(problem, r):
    pass

def fold(problem):
    pass

class Move(object):
    moves = {
        "translate": translate
    }
    move = None
    arglist = []
    def __init__(self, name, arglist):
        self.move = self.moves[name]
        self.arglist = arglist

    def do_move(self, p):
        return self.move(p, self.arglist)
    
