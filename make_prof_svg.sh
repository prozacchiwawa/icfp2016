#!/bin/sh

gprof2dot -f pstats $1 -o prof.dot
dot -Tsvg -oprof.svg prof.dot
