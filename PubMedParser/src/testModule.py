from turtle import color
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

    IOmodule.pickleOut("/root/The_Hive/term_doc/hashTables", "VLHash","btd", VLHash)


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
from pylab import *
import math
def makehist():


    ##########################################################################
                                    #TermDoc#
    ##########################################################################

    # TEST 1 : Found on our own from orpha.net#

    #diseases=['Ap','Ru','Aa','Aa','Ac','Ac','Ac','Ac','Bi','Br','Ch','Ch','Co','Om','Da','Ic','Em','Co','Fi','Ac','Os','Pr','He','Hy','Ja','Ja','Je','Ja','Mu','Tr']
    #graphName="termDoc_orphan_hist_3000.png"
    #title='Score (3000) test (Orphan) - term-doc matrix'

    # Not stemmed
    ## Mean:
    #x1 = [4,725,75,37,38,85,68,1651,1,23,80,15,0,26,2,218,3,13,2,3000,1,9,14,78,84,48,3,84,1,62]
    ## Median:
    #x1 = [81, 261, 613, 222, 987, 4, 36, 446, 666, 263, 1388, 291, 41, 47, 30, 0, 71, 147, 35, 3000, 174, 237, 13, 382, 863, 12, 835, 863, 267, 44]
    ## Max:
    #x1 = [6, 504, 0, 5, 108, 6, 2, 1079, 4, 52, 45, 7, 0, 13, 2, 0, 11, 0, 3, 3000, 6, 42, 4, 96, 434, 1, 8, 434, 14, 1]

    # Stemmed
    ## Mean:
    #x2 = [4,289,81,34,19,111,78,1355,1,26,187,18,0,27,2,215,3,12,4,3000,1,11,20,73,68,50,3,68,3,54]
    ## Median:
    #x2 = [139, 400, 53, 264, 850, 1, 32, 2304, 391, 318, 865, 237, 24, 37, 94, 0, 75, 134, 22, 3000, 175, 263, 21, 309, 406, 15, 433, 406, 451, 55]
    ## Max:
    #x2 = [12, 145, 0, 0, 93, 6, 2, 1842, 6, 25, 44, 15, 0, 15, 1, 0, 10, 0, 3, 3000, 7, 46, 4, 128, 115, 1, 24, 115, 2, 1]

    # Stemmed and tfidf-preprocessed
    ## Mean:
    #x3 = [2,221,30,28,34,69,68,775,2,15,196,12,0,24,1,222,0,11,3,3000,0,9,13,56,75,44,5,75,17,40]
    ## Median:
    #x3 = [339,246,82,237,1298,16,47,1224,741,495,1206,256,73,386,96,0,115,172,41,3000,479,581,35,774,646,34,193,646,662,99]
    ## Max:
    #x3 = [11,206,0,4,129,0,0,1399,13,20,79,22,0,12,0,1,15,0,3,3000,5,143,2,112,130,0,49,130,115,0]

    ## Normed labels
    #x3 = [289,371,6,152,705,8,26,1653,515,317,541,267,52,269,37,0,74,107,28,3000,285,539,42,650,431,31,201,431,634,27]

    # TEST 2 : From BMJ #

    #diseases=['Infec','Cushi','Eosin','Ehrli','Neuro','Pheoc','Creut','Churg','Derma','Cat S','TEN','MELAS','Bruga']
    #graphName="termDoc_bmj_hist_3000.png"
    #title='Score (3000) test (BMJ) - term-doc matrix'

    # Not stemmed
    ## Mean:
    #x1 = [19,3,22,1268,115,105,108,5,54,0,2,41,7]
    ## Median:
    #x1 = [128, 153, 819, 560, 612, 457, 204, 786, 81, 30, 603, 292, 184]
    # Max:
    #x1 = [5, 4, 383, 1021, 44, 241, 107, 37, 8, 0, 24, 19, 27]

    # Stemmed
    ## Mean:
    #x2 = [19,3,55,840,171,83,101,5,35,0,4,29,7]
    ## Median:
    #x2 = [89, 151, 800, 1103, 400, 491, 315, 842, 825, 51, 494, 681, 185]
    ## Max:
    #x2 = [2, 10, 136, 1123, 68, 249, 130, 44, 8, 0, 47, 65, 25]

    # Stemmed and tfidf-preprocessed
    ## Mean:
    #x3 = [13, 8, 1394, 722, 196, 48, 87, 2, 7, 0, 2, 8, 2]
    ## Median:
    #x3 = [288, 558, 81, 1920, 474, 510, 329, 822, 90, 574, 1028, 990, 863]
    ## Max:
    #x3 = [10, 150, 286, 1954, 143, 423, 238, 84, 9, 0, 125, 62, 55]
    

    ## Normed labels:
    #x3 = [185,478,74,2033,350,614,459,558,96,200,931,779,810]

    ##########################################################################
                                    #TermLabel#
    ##########################################################################

    # TEST 1 : Found on our own from orpha.net#

    #diseases=['Ap','Ru','Aa','Aa','Ac','Ac','Ac','Ac','Bi','Br','Ch','Ch','Co','Om','Da','Ic','Em','Co','Fi','Ac','Os','Pr','He','Hy','Ja','Ja','Je','Ja','Mu','Tr']
    #graphName="diseaseMatrix_orphan_hist_NOTnorm_3000.png"
    #title='Score (3000) test (Orphan) - disease matrix'

     # Not stemmed
     ## Norm:
    #x1 = [76,257,0,20,122,41,9,1912,16,1,448,128,1,13,5,0,33,380,20,1687,39,47,26,4,33,1,83,33,46,0]
     ## Not norm:
    #x1 = [8,108,1,12,4,79,120,563,5,6,82,8,0,1,0,22,0,3,0,3000,0,5,14,328,30,2,4,30,0,45]
     # Stemmed
     ## Norm:
    #x2 = [74,263,0,19,106,44,12,635,19,1,446,133,4,13,4,0,80,391,122,2137,74,54,12,2,30,1,99,30,162,0]
     ## Not norm:
    #x2 = [8,84,16,11,4,86,93,82,4,5,80,13,0,1,0,22,0,4,0,3000,0,5,4,260,29,3,3,29,0,51]
     # Stemmed and tfidf-preprocessed
     ## Norm:
    #x3 = [38,144,0,4,50,5,0,480,127,0,272,78,0,169,1,0,19,118,20,3000,26,20,6,8,24,0,24,24,15,0]
     ## Not norm:
    #x3 = [4,75,1031,273,3,98,383,88,220,6,94,2,0,526,0,376,1,1,0,3000,2,0,4,1604,80,29,14,80,2,457]

    # TEST 2 : From BMJ #

    diseases=['Infec','Cushi','Eosin','Ehrli','Neuro','Pheoc','Creut','Churg','Derma','Cat S','TEN','MELAS','Bruga']
    graphName="diseaseMatrix_bmj_hist_norm_3000.png"
    title='Score (3000) test (BMJ) - disease matrix'

    # Not stemmed
     ## Norm:
    x1 = [16,37,375,2001,270,1037,25,6,0,1,97,45,25]
     ## No sqrt
    #x1 = [31,62,474,2220,377,1225,93,8,20,5,227,118,94]

     ## Not norm:
    #x1 = [13,2,389,1052,11,609,8,4,3,0,3,13,6]
     ## No sqrt
    #x1 = [6,1,323,691,30,427,8,2,4,0,3,19,6]



    # Stemmed
     ## Norm:
    x2 = [25,37,748,1970,384,1053,25,2,0,1,102,68,30]
    # No sqrt
    #x2= [37,63,872,1963,533,1198,93,4,18,9,230,221,91]
     ## Square root of sum of values
    #x


     ## Not norm:
    #x2 = [18,2,653,900,12,600,7,0,3,0,3,21,6]
    # No sqrt
    #x2=[5,1,597,511,29,413,6,1,3,0,3,26,6]

    # Stemmed and tfidf-preprocessed
     ## Norm:
    x3 = [8,19,1060,1831,136,698,11,1,0,9,18,42,15]
    # No sqrt
    #x3= [8,33,1175,1561,255,593,29,4,0,9,68,90,50]

     ## Not norm:
    #x3 = [9,3,826,785,19,370,2,0,3,3,2,13,1]
    # No sqrt
    #x3=[4,4,816,410,35,184,2,1,4,2,2,15,3]

    ##########################################################################


    fig=figure(figsize=(8,5))
    ax=fig.add_subplot(1,1,1)

    # Font size in legend
    rc('legend', fontsize='small')

    xlen=len(x1)*6
    xlen=len(x2)*6
    xlen=len(x3)*6
    step=6

    x1_log=map(lambda x: math.log(x+1),x1)
    x2_log=map(lambda x: math.log(x+1),x2)
    x3_log=map(lambda x: math.log(x+1),x3)

    y1=mean(x1_log)
    print y1
    y2=mean(x2_log)
    print y2
    y3=mean(x3_log)
    print y3
    ax.plot([0,xlen],[y1,y1],'g-',linewidth=2)
    ax.plot([0,xlen],[y2,y2],'r-',linewidth=2)
    ax.plot([0,xlen],[y3,y3],'b-',linewidth=2)

    ax.bar(arange(0,xlen,step), x1_log, color='green', width=1, label='Not stemmed, avg='+str(y1)[:4])
    ax.bar(arange(1,xlen,step), x2_log, color='red', width=1, label='Stemmed, avg='+str(y2)[:4])
    ax.bar(arange(2,xlen,step), x3_log, color='blue', width=1, label='TFIDF-preprocessed and stemmed, avg='+str(y3)[:4])

    ax.set_xticks(range(1,len(x3)*6,6))
    ax.set_xticklabels(diseases)
    # Set font size for the disease-labels
    for label in ax.get_xticklabels():
        label.set_fontsize(10)

    ax.legend()
    ax.grid('.')
    ax.set_title(title)
    ax.set_xlabel('Disease')
    ax.set_ylabel('Log_score')

    # Rotate the disease labels
    fig.autofmt_xdate()

    show()
    savefig("/home/henne/Documents/Projektet/bachelor/Grafer_og_tegninger/"+graphName)

"""
from nltk import *
from nltk.corpus import stopwords
from scipy import sparse
termHashTable=IOmodule.pickleIn("/root/The_Hive/term_doc/hashTables", "termHash")
#termHashTable=IOmodule.pickleIn("/root/The_Hive/term_doc/hashTables", "termHash_stemmed")
revTermHashTable=dict(zip(termHashTable.values(),termHashTable.keys()))
from numpy import delete
def sanitizeMatrices():

    oldMatrixDir="/root/The_Hive/term_doc/diseaseMatrices"
    #oldMatrixDir="/root/The_Hive/term_doc/diseaseMatrices_stemmed"
    newMatrixDir="/root/The_Hive/term_doc/new_diseaseMatrices"
    #newMatrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_stemmed"

    stopWordList=stopwords.words("english")

    files = sorted([f for f in os.listdir(oldMatrixDir+"/") if os.path.isfile(oldMatrixDir+"/" + f)])

    count=0
    for file in files:
        count+=1
        print "Matrix "+str(count)
        coo=IOmodule.readInTDM(oldMatrixDir,file)
        csr=coo.tocsr()
        csc=coo.tocsc()
        dense=coo.todense()
    
        termHash=csr.getrow(0).data
        pmidHash=csc.getcol(0).data

        m=len(pmidHash)
        n=len(termHash)

        print "Dim("+str(m)+","+str(n)+")"

        dense=dense[:m+1,:n+1]

        print dense.shape

        toBeDeleted=[]
        for i in range(1,n+1):
            term=revTermHashTable[dense[0,i]]
            if term in stopWordList:
                toBeDeleted.append(i)

        dense=delete(dense,toBeDeleted,1)

        coo=sparse.coo_matrix(dense)

        IOmodule.writeOutTDM(newMatrixDir,file[:-4],coo)

        print ""
"""
