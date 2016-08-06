from fractions import Fraction

# http://stackoverflow.com/questions/10508021/matrix-multiplication-in-python
def matrixmult (A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    rows_B = len(B)
    cols_B = len(B[0])

    if cols_A != rows_B:
      print "Cannot multiply the two matrices. Incorrect dimensions."
      return

    # Create the result matrix
    # Dimensions would be rows_A x cols_B
    C = [[0 for row in range(cols_B)] for col in range(rows_A)]

    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                C[i][j] += A[i][k] * B[k][j]
    return C

def translation(x,y):
    return [[1, 0, x],
            [0, 1, y],
            [0, 0, 1]]

def reflection(segment):
    to_origin = translation(-segment[0][0],-segment[0][1])
    from_origin = translation(segment[0][0],segment[0][1])
    if segment.no_slope():
        reflect = [[ -1, 0, 0 ],
                   [ 0,  1, 0 ],
                   [ 0,  0, 1 ]]
    else:
        m = segment.slope()
        factor = Fraction(1, 1 + (m * m))
        reflect = [[ factor * (1 - (m * m)), factor * 2 * m , 0 ],
                   [ factor * 2 * m, factor * ((m * m) - 1), 0 ],
                   [ 0 , 0 , 1 ]]
    a1 = matrixmult(from_origin, reflect)
    return matrixmult(a1, to_origin)
        
