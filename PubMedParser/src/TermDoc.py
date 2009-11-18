import RecordHandler
from pysparse import spmatrix


def populateMatrix(m,n,doc,term):

    M = spmatrix.ll_mat(m,n)

    # row : m
    # col : n

    for m in range(len(M[1,:])):
        for n in range(len(M[:,1])):

            #M[n,m]=float(str(n)+str(m))
            if m==0:
                M[n,m]=1

    return M




