import math
from math import sqrt, pow, acos
import numpy as np
from numpy import linalg
from numpy.linalg import norm
from numpy import dot

# These should work independently from the term doc, as long as one
# does not look for correlation between different sub term doc, as
# they might contain differing terms, so you could end up performing
# correlation between different terms while thinking they are really
# the same.
#
# E.g.
# subtermdoc_1
#       th_1 th_2 th_3 th_4
# pid_1  wc1    0    0  wc4
# pid_2    ....
#
# subtermdoc_2
#       th_1 th_2 th_6 th_14
# pid_7  wc1  wc2    0  wc14
# pid_8    ....
#
# Looking for correlation between subtermdoc_1 and 2, will result in a
# correlation between termhash 4 and termhash 14, which does not make
# sense, i.e. looking for correlation between different terms.
#

def sim_pearson(v1, v2, output=False):

    """
    Recieves two vectors coming from the same vector space, i.e. with
    the same axis. This is either from the same sub term doc or both
    coming from the complete term doc. And then returns the pearsons
    correlation coefficient or 0 if they have no similarity at all.
    """

#     print v1
#     print 'test'
    #print v2
    v1nz = v1.nonzero()[1]
    v2nz = v2.nonzero()[1]

#    v1 = v1[0,1:]
#    v2 = v2[0,1:]

    # We need to get the coordinates where both are non zero, we use
    # set, because they are fast.
#    print "v1nz pmidhash: ", v1nz[0], '\t', 
#    print "v2nz pmidhash: ", v2nz[0]
    # We need to get the right indices.

    if output:
        print v1nz
        print v2nz

    simIndex = list(set.intersection(set(v1nz), set(v2nz)))
    # Sort the index for good order. :)
    simIndex.sort()

    if output:
        print simIndex

    # Number of sim non zero
    n = len(simIndex)

    if output:
        print "n =", n

    # If n is 0, no need to work anymore
    if n == 0: return 0

    # Sum up similar
    sum1 = 0.0
    sum2 = 0.0
    # Sum of the squares
    sum1Sq = 0.0
    sum2Sq = 0.0
    # Product sum
    pSum = 0.0

    # Only need to make one pass over the vectors.
    #
    # Do not know wether its faster to temporarily to the vector entry
    # out into a variable.
    for index in simIndex:
        if output:
            print 'v1: (0, ' + str(index) + ') =', v1[0, index]
            print 'v2: (0, ' + str(index) + ') =', v2[0, index]
        sum1 += v1[0, index]
        sum2 += v2[0, index]
        sum1Sq += pow(v1[0, index], 2)
        sum2Sq += pow(v2[0, index], 2)
        pSum += v1[0, index] * v2[0, index]

    if output:
        print
        print 'sum1 =', sum1
        print 'sum2 =', sum2
        print 'sum1Sq =', sum1Sq
        print 'sum2Sq =', sum2Sq
        print 'pSum =', pSum

    num = pSum - ((sum1 * sum2) / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))

    if output:
        print 'num =', num
        print 'den =', den

    if den == 0: return 0

    r = num / den

    # Return pearsons correlations coefficient
    return r

def cosine_measure(v1,v2):

    """
    Takes two normalized vectors and returns the cosine score between
    them.
    """

    v1 = v1[0,1:]
    v2 = v2[0,1:].transpose()

    # As they have already been normalized, their norm is 1
    rad_angle = (v1*v2) / (norm(v1) * norm(v2))

    return math.acos(rad_angle[0,0])
