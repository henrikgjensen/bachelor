from scipy import sparse, ones
import IOmodule
import os
import time

def createLargeMatrix():

    m=40000
    n=1000000

    M=sparse.lil_matrix((m,n))

    # populate some of the matrix
    M.setdiag(ones(m-1))
    M[(m/2),:]=ones(n-1)
    M[:,(n/2)]=ones(m-1)

    return M


def createSubMatrix():

    m=500
    n=20000

    M=sparse.lil_matrix((m,n))

    # Populate some of the matrix
    M[0,:]=ones(n)
    M[:,0]=ones(m)
    M[(m/2),:]=ones(n)
    M[:,(n/2)]=ones(m)
    M[m-1,:]=ones(n)
    M[:,n-1]=ones(m)

    return M

def createLargeSubMatrix():

    # Create a large matrix, but with same amount of 'ones' as the small submatrix

    t1 = time.time()

    m=40000
    n=1000000

    M=sparse.lil_matrix((m,n))

    m=500
    n=20000

    # Populate some of the matrix
    M[0,:]=ones(n)
    M[:,0]=ones(m)
    M[(m/2),:]=ones(n)
    M[:,(n/2)]=ones(m)
    M[m-1,:]=ones(n)
    M[:,n-1]=ones(m)

    t2 = time.time()
    print 'Time used: ',(t2-t1)

    return M

def saveMatrix(filename,matrix):

    t1 = time.time()

    IOmodule.writeOutTDM('testFolder',filename, matrix)

    t2 = time.time()
    print 'Time used: ',(t2-t1)


#def addSubToLargeMatrix(MSmall,MLarge):
#
#    for m in MSmall:
#        for n in MSmall:
