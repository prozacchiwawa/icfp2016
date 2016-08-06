import pstats

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 1:
        print 'usage process_prof prof.txt'
        sys.exit(1)

    p = pstats.Stats(sys.argv[1])
    p.strip_dirs().sort_stats('time').print_stats()
