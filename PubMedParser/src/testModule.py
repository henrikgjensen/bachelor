from scipy import sparse, ones
import pysparse
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


def addSubToLargeMatrix():

    # create sub matrix

    # [0, 3, 7]
    # [5,11,12]
    # [9,21,22]

    msub=sparse.lil_matrix((3,3))
    msub[0,0]=0
    msub[0,1]=3
    msub[0,2]=7
    msub[1,0]=5
    msub[2,0]=9
    msub[1,1]=11
    msub[1,2]=12
    msub[2,1]=21
    msub[2,2]=22
    msub=msub.tocoo()
    msub2=msub.tolil()
    print 'Made submatrix'

    # create large matrix
    mlar=sparse.lil_matrix((30,30))
    print 'Allocated large matrix: ',mlar


    #for row in range(msub.shape[0]):
    #    for col in range(msub.shape[1]):

    for i,j,v in zip(msub.row, msub.col, msub.data):
        m = msub2[i,0]
        n = msub2[0,j]

        # Make sure not to add index's
        if m==0 or n==0:
            continue

        print "row:",i,"col:",j
        print "Adding "+str(v)+" to ("+str(m)+","+str(n)+")"
        mlar[m,n] += v
        print 'Successfully added'

    return mlar

def loadMatrix(dirPath,filename):

    t1=time.time()

    M = IOmodule.readInTDM(dirPath, filename)

    t2=time.time()

    print str(t2-t1)

    return M


from numpy import linalg
import IOmodule
def createVLHash(M_lil):

    VLHash={}
    for pmidHash in range(M_lil.shape[0]):
        VLHash[pmidHash]=linalg.norm((M_lil.getrow(pmidHash).data[0])[1:])

    IOmodule.pickleOut("/root/The_Hive/term_doc/hashTables", "VLHash", VLHash)


#really fast elementwise stuff:
import math
import os
import SearchTermDoc

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
_hashTablePath = _path+"/"+"term_doc/hashTables"

# Load the precomputed length of each column-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'CLHash')


def go(MT_coo,MT_csr,M_lil,M_csc,M_coo):


    numberOfDocs = MT_coo.shape[1]
    print "Number of docs: "+str(numberOfDocs)


    
    for col in range(1,MT_coo.shape[0]+1):

        t3=time.time()

        slice=MT_csr.getrow(col).tocoo() # 'column' slice

        for row,data in zip(slice.col,slice.data):
            idf = math.log(numberOfDocs / _vectorLength[col])
            tf = math.log(1 + data)
            if data==0:
                raise Exception
            M_lil[row,col]=tf*idf
            #data=(j,i,v) # (row,col,data)
        print "column number: "+str(col)

        t4=time.time()
        print str(t4-t3)

    return M_lil
    
    """
    for termVectorIndex in range(1,M_coo.shape[1]+1):

        t3=time.time()
        
        print "Progress: " + str(M_coo.shape[1]-termVectorIndex)
        #termVectorData = (M_csc.getcol(termVector).data)[1:]
        docIndexVector = (M_csc.getcol(termVectorIndex).nonzero()[0])[1:]
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf = math.log(numberOfDocs / len(docIndexVector))

        for docIndex in docIndexVector:
            # Calculate the term frequency
            tf = M_lil[docIndex, termVectorIndex]
            if tf == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception
            tf = math.log(1 + tf)
            # Update the new matrix values
            M_lil[docIndex, termVectorIndex] = tf * idf

        t4=time.time()
        
        print str(t4-t3)
    """
    
