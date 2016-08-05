from math import sqrt

def float_of_fract(p,off=0,scale=1):
    if type(p) == type(0.0):
        return (p * scale) + off
    else:
        return (((float(p.numerator) / float(p.denominator)) * scale) + off)

def fract_dist(a,b):
    ax = float_of_fract(a[0])
    ay = float_of_fract(a[1])
    bx = float_of_fract(b[0])
    by = float_of_fract(b[1])
    xdiff = bx - ax
    ydiff = by - ay
    return sqrt((xdiff * xdiff) + (ydiff * ydiff))
