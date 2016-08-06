import problem
from problem import Problem
import moves
from moves import Move,create_move


'''
do_moves.py:
  * Read the finished problem, and a file containing moves.
  * Apply the moves to the starting square, and check if the ending state 
    is the same as the given problem.
  * Output the Formatted Solution

let Problem be Position

All points in the previous step must be in the new step (possibly at new positions)

There may be new points

mountain. valley. right_up, left_down.

Operations: break a line segment.

Position([ (0,0), (1,0), (1,1), (0,1) ])
Fold( (0,1), (1,0) )
Position([ (0,0), (1,0), (0,0), (0,1) ])
Fold( (0,0.5), (0.5,0.5) )
Position([ (0,0), (1,0), (1,1), (0,1) ])


How many lines overlap?
Propogate points backward: unfold(points, lines)
Which types of unflod generate points?

All facets in the start appear in the end.

Fold: if both points are new (split a line), then:
  two new points are created for each outer?) new point, -- edge of square
  one new point for each point ... lays on prev outer fold? - inner of sq
  
'''

def read_move(line):
    cmd_and_args = line.split(":")
    cmd = cmd_and_args[0].strip()
    args = cmd_and_args[1].split(",")
    return create_move(cmd, args)


def read_moves(filename):
    moves = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            moves.append(read_move(line))
    return moves
    
#def do_move(move, problem):
#    pass

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print 'usage: a.py [start_prob] [moves_file] [end_prob]'
        sys.exit(1)

    # e.g. p = Problem("prob/start_square.prob")
    p = problem.read(open(sys.argv[1]))
    moves = read_moves(sys.argv[2])
    end_problem = problem.read(open(sys.argv[3]))
    states = []
    
    for m in moves:
        states.append(p)
        p = m.do_move(p)

    # XXX need a way to compare states - equality operator on Problem 
    if p != end_problem:
        print "BAD"
        print "\nWANTED: ", end_problem
        print "\nGOT: ", p
        print "\nVIA STATES: ", states
        print
        sys.exit(2)

    print "OK"
