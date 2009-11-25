from scipy import sparse, ones
import IOmodule
import os
import time

def createLargeMatrix():

    m=40000
    n=1000000

    M=sparse.lil_matrix((m,n))

    # populate some of the matrix
    M.setdiag(ones(m))
    M[(m/2),:]=ones(n)
    M[:,(n/2)]=1

    return M


def createSubMatrix():

    m=500
    n=20000

    M=sparse.lil_matrix((m,n))

    # Populate some of the matrix
    M[0,:]=ones(n)
    M[:,0]=1
    M[(m/2),:]=ones(n)
    M[:,(n/2)]=1
    M[(m-1),:]=ones(n)
    M[:,(n-1)]=1
    M[0,20]=17
    M[23,0]=11
    M[23,20]=200

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
    M[:,0]=1
    M[(m/2),:]=ones(n)
    M[:,(n/2)]=1
    M[(m-1),:]=ones(n)
    M[:,(n-1)]=1

    t2 = time.time()
    print 'Time used: ',(t2-t1)

    return M

def saveMatrix(filename,matrix):

    t1 = time.time()

    IOmodule.writeOutTDM('testFolder',filename, matrix)

    t2 = time.time()
    print 'Time used: ',(t2-t1)


def addSubToLargeMatrix(MSmall,MLarge):

    t1 = time.time()

#    MSmall = sparse.dok_matrix(MSmall)

    MSmall2 = sparse.coo_matrix(MSmall)

#    MLarge = sparse.dok_matrix(MLarge)

    for i,j,v in zip(MSmall2.row, MSmall2.col, MSmall2.data):
        m = MSmall[i,0]
        n = MSmall[0,j]
        
        MLarge[m,n] += v

    t2 = time.time()
    print 'Time used: ',(t2-t1)
