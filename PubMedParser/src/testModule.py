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


# Main folder
#_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
#_hashTablePath = _path+"/"+"term_doc/hashTables"

# Load the precomputed length of each column-vector in the term-doc matrix.
#_vectorLength = IOmodule.pickleIn(_hashTablePath,'CLHash')


def go(MT_coo,MT_csr,M_lil,M_csc,M_coo):


    numberOfDocs = MT_coo.shape[1]
    print "Number of docs: "+str(numberOfDocs)


    
    for col in range(250000,MT_coo.shape[0]+1):

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
    for termVectorIndex in range(250000,M_coo.shape[1]+1):

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

    """
    for termVectorIndex in range(1,M_coo.shape[1]+1):

        t3=time.time()

        print "Progress: " + str(M_coo.shape[0]-termVectorIndex)
        #termVectorData = (M_csc.getcol(termVector).data)[1:]
        docIndexVector = (MT_csr.getrow(termVectorIndex).nonzero()[1])[1:]
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf = math.log(numberOfDocs / len(docIndexVector))

        #row=T_tfidfMatrix[termVectorIndex,1:]
        #T_tfidfMatrix[termVectorIndex,1:]=map(lambda x: math.log(1+x)*idf,row)

        for docIndex in docIndexVector:
            # Calculate the term frequency
            tf = M_lil[docIndex,termVectorIndex]
            if tf == 0:
                print "Looked up zero-value at: ("+str(termVectorIndex)+" "+str(docIndex)+")"
                raise Exception
            tf = math.log(1 + tf)
            # Update the new matrix values
            M_lil[docIndex,termVectorIndex] = tf * idf

        t4=time.time()
        print str(t4-t3)
    
    """

def makehist():

    from pylab import *
    import math

    # TEST 1 : Found on our own from orpha.net#

    #diseases=['Appar','Rubin','Aagen','Aase','Achon','Acalv','Acrod','Acrom','Bilia','Bronc','Chole']

    # Not stemmed
    #x1 = [4,725,75,37,38,85,68,1651,1,23,80]
    # Stemmed
    #x2 = [3,149,33,71,10,63,27,597,6,31,56]
    # Stemmed and tfidf-preprocessed
    #x3 = [2,102,33,28,14,54,46,306,2,13,203]

    # TEST 2 : From BMJ #

    diseases=['Infec','Cushi','Eosin','Ehrli','Neuro','Pheoc','Creut','Churg','Derma','Cat S','TEN','MELAS','Bruga']

    # Not stemmed
    x1 = [19,3,22,1268,115,105,108,5,54,0,2,41,7]
    # Stemmed
    x2 = [29,1,71,623,402,119,154,10,64,0,3,43,6]
    # Stemmed and tfidf-preprocessed
    x3 = [14,7,1152,1011,277,49,42,3,16,0,1,13,4]

    x1_log=map(lambda x: math.log(x+1),x1)
    x2_log=map(lambda x: math.log(x+1),x2)
    x3_log=map(lambda x: math.log(x+1),x3)


    xlen=len(x1)*6
    step=6

    bar(arange(0,xlen,step), x1_log, color='green', width=1, label='Not stemmed')
    bar(arange(1,xlen,step), x2_log, color='red', width=1, label='Stemmed')
    bar(arange(2,xlen,step), x3_log, color='blue', width=1, label='TFIDF-preprocessed and stemmed')

    #x=linspace(1,xlen)
    y1=mean(x1_log)
    print y1
    y2=mean(x2_log)
    print y2
    y3=mean(x3_log)
    print y3
    plot([0,xlen],[y1,y1],'g-',linewidth=2)
    plot([0,xlen],[y2,y2],'r-',linewidth=2)
    plot([0,xlen],[y3,y3],'b-',linewidth=2)

    xticks(range(1,len(x3)*6,6),diseases)

    legend()
    grid('.')
    title('Score test (BMJ)')
    xlabel('Disease')
    ylabel('Log_score')

    show()
    savefig("/home/henne/Documents/Projektet/bachelor/Grafer_og_tegninger/bmj_hist.png")


from scipy import linalg, mat, sparse, array
def svd(M_coo):

    t1=time.time()

    X = M_coo.todense()

    termHashTable=IOmodule.pickleIn("/root/The_Hive/term_doc/hashTables", "termHash_stemmed")
    revTermHashTable=dict(zip(termHashTable.values(),termHashTable.keys()))
    hashes=[]
    termHashes=array(X[0,1:])
    for termHash in termHashes[0]:
        hashes.append(revTermHashTable[termHash])

    X = X[1:,1:]

    U, S, Vt = linalg.svd(X)

    M, N = X.shape

    Sig = mat(linalg.diagsvd(S, M, N))
    U, Vt = mat(U), mat(Vt)

    t2=time.time()
    print str(t2-t1)

    return U,Sig,Vt,hashes


def semanticSpace(U,Sig,Vt,reduce=5):

    Sig_csc=sparse.csc_matrix(Sig)
    eigSum = Sig_csc.sum()
    diagLen = Sig_csc.getnnz()

    percentReduce=(float(eigSum)/100)*reduce
    print percentReduce

    counter=0
    n=0
    for i in range(1,diagLen):

        bottomUp=diagLen-i

        counter+=Sig[bottomUp,bottomUp]
        
        if counter >= percentReduce:
            n=i
            break

    print n
    U=U[:,:-n]
    print str(U.shape)
    Sig=Sig[:-n,:-n]# Make magic...
    print str(Sig.shape)
    Vt=Vt[:-n,:]
    print str(Vt.shape)

    U=sparse.csc_matrix(U)
    Sig=sparse.csc_matrix(Sig)
    Vt=sparse.csc_matrix(Vt)

    return U*Sig*Vt


def topSemanticTerms(M_csc,hashes):

    # Make magic...

    l=[]

    for col in range(M_csc.shape[1]):
        l.append((sum(M_csc.getcol(col).data),hashes[col]))

    l.sort()
    l.reverse()

    return l