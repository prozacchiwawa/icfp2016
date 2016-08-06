
'''
Give a starting square, with all the fold-lines, and the target end state,
Output the solution in valid, normalized form.
'''


class Solution(object):
    def __init__(assumed, problem_end_position):
        assumed.shared_edges
        source_positions = []
        facets = []
        dest_positions = []    

def is_solution_valid(s):
    # All the source positions of the vertices are within the initial square 
    # spanned by the four vertices (0,0), (1,0), (1,1), (0,1).
    for p in s.source_positions:
        if p[0] < 0 or p[0] > 1 or p[1] < 0 or p[1] > 1:
            return False

    return True

# Return dict of edge: [list of polygon indicies] that share that edge.
def find_shared_edges(polygons):
    return None

def is_congruent(p1, p2):
    return False

def is_solution_normal(s):
    # At source position, if two different facets share an edge for a length greater than 0, then the intersection set of those two facets at destination positions must have an area greater than 0. In other words, if an edge separates two facets, you should always fold the origami at that edge.
    return is_solution_valid(s) and False

def output_solution(s):
    '''
    A transformed Point in dest_positions, index n represents the 
    same Point as the one in source_positions, index n
    '''
    print len(s.source_positions)
    for p in s.source_positions:
        print p

    print len(s.facets)
    for f in s.facets:
        sys.stdout.write(len(f))
        sys.stdout.write(" ")
        print " ".join(f)

    print len(source_positions)
    for p in source_positions:
        print p
    
