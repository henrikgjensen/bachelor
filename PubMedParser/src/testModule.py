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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # TEST 1 : Found on our own from orpha.net#
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    #diseases=['Ap','Ru','Aa','Aa','Ac','Ac','Ac','Ac','Bi','Br','Ch','Ch','Co','Om','Da','Ic','Em','Co','Fi','Ac','Os','Pr','He','Hy','Ja','Ja','Je','Ja','Mu','Tr']
    #graphName="termDoc_orphan_hist_3000.png"
    #title='Score test Orpha.net - term-doc matrix'

    # Not stemmed
    #=========================================================================
    ## Mean norm-sqrt (COSINE):
    #x2 = [4,725,75,37,38,85,68,1651,1,23,80,15,0,26,2,218,3,13,2,3000,1,9,14,78,84,48,3,84,1,62]
    ## Median norm-sqrt (COSINE):
    #x1 = [81, 261, 613, 222, 987, 4, 36, 446, 666, 263, 1388, 291, 41, 47, 30, 0, 71, 147, 35, 3000, 174, 237, 13, 382, 863, 12, 835, 863, 267, 44]
    ## Max norm-sqrt (COSINE):
    #x1 = [6, 504, 0, 5, 108, 6, 2, 1079, 4, 52, 45, 7, 0, 13, 2, 0, 11, 0, 3, 3000, 6, 42, 4, 96, 434, 1, 8, 434, 14, 1]

    ## Mean norm (COSINE - no sqrt):
    #x1 = [4, 664, 30, 47, 38, 85, 62, 1371, 1, 32, 83, 15, 0, 26, 2, 81, 3, 16, 2, 3000, 4, 10, 13, 24, 66, 35, 3, 66, 4, 34]
    ## Median norm (COSINE - no sqrt):
    #x1 = [163, 357, 76, 240, 948, 4, 76, 141, 384, 314, 505, 211, 44, 181, 42, 773, 87, 169, 189, 3000, 179, 265, 21, 491, 692, 37, 435, 692, 358, 233]
    ## Max norm (COSINE - no sqrt):
    #x1 = [4, 858, 0, 10, 44, 15, 2, 541, 4, 116, 99, 18, 0, 6, 2, 0, 22, 0, 3, 3000, 9, 67, 5, 63, 201, 1, 8, 201, 9, 0]


    ## Mean not-norm (SUM)
    #1= [6, 910, 917, 32, 122, 460, 145, 3119, 1, 21, 342, 50, 0, 45, 2, 137, 3, 44, 14, 2458, 0, 9, 36, 37, 132, 47, 26, 132, 37, 127]
    ## Median not-norm (SUM)
    #2 = [626, 2814, 495, 219, 1232, 963, 182, 3590, 872, 1207, 1056, 595, 526, 940, 179, 1292, 503, 408, 304, 845, 320, 204, 143, 1165, 1763, 19, 467, 1763, 1532, 100]
    ## Max not-norm (SUM)
    #3 = [119, 2081, 611, 113, 1031, 48, 203, 3833, 7, 127, 1139, 109, 9, 7, 2, 357, 7, 401, 3, 1957, 13, 0, 102, 169, 260, 4, 198, 260, 72, 55]

    #=========================================================================

    # Stemmed
    #=========================================================================
    ## Mean norm-sqrt (COSINE):
    #x2 = [4,289,81,34,19,111,78,1355,1,26,187,18,0,27,2,215,3,12,4,3000,1,11,20,73,68,50,3,68,3,54]
    ## Median norm-sqrt (COSINE):
    #x2 = [139, 400, 53, 264, 850, 1, 32, 2304, 391, 318, 865, 237, 24, 37, 94, 0, 75, 134, 22, 3000, 175, 263, 21, 309, 406, 15, 433, 406, 451, 55]
    ## Max norm-sqrt (COSINE):
    #x3 = [12, 145, 0, 0, 93, 6, 2, 1842, 6, 25, 44, 15, 0, 15, 1, 0, 10, 0, 3, 3000, 7, 46, 4, 128, 115, 1, 24, 115, 2, 1]
    
    ## Mean norm (COSINE - no sqrt):
    #x2 = [4, 248, 29, 48, 23, 106, 64, 1436, 1, 34, 85, 16, 0, 26, 2, 81, 3, 15, 3, 3000, 4, 11, 11, 24, 60, 46, 3, 60, 7, 36]
    ## Median norm (COSINE - no sqrt):
    #x2 = [146, 968, 15, 256, 503, 5, 53, 114, 403, 106, 440, 252, 39, 123, 59, 689, 94, 125, 132, 3000, 281, 256, 23, 511, 572, 38, 386, 572, 571, 15]
    ## Max norm (COSINE - no sqrt):
    #x3 = [1, 677, 0, 3, 40, 8, 2, 462, 4, 75, 87, 31, 0, 8, 1, 0, 17, 0, 3, 3000, 10, 58, 5, 86, 162, 1, 24, 162, 9, 0]

    ## Mean not-norm (SUM):
    #x4 = [6, 708, 644, 28, 97, 460, 170, 2522, 1, 30, 190, 58, 0, 43, 6, 136, 3, 39, 16, 2636, 0, 8, 50, 33, 115, 53, 31, 115, 121, 124]
    ## Median not-norm (SUM):
    #x2 = [691, 1905, 143, 209, 1763, 684, 152, 2492, 1008, 1046, 1126, 321, 334, 865, 557, 1253, 567, 425, 399, 1310, 392, 262, 186, 913, 1903, 15, 675, 1903, 1910, 89]
    ## Max not-norm (SUM):
    #x4 = [75, 2228, 638, 113, 993, 48, 171, 3281, 3, 131, 1194, 131, 7, 7, 3, 365, 7, 414, 3, 2242, 253, 0, 150, 188, 42, 4, 6, 42, 372, 55]
    #=========================================================================

    #~~~~~~~~~~~~~~~~~~~#
    # TEST 2 : From BMJ #
    #~~~~~~~~~~~~~~~~~~~#

    #diseases=['Infec','Cushi','Eosin','Ehrli','Neuro','Pheoc','Creut','Churg','Derma','Cat S','TEN','MELAS','Bruga']
    #graphName="termDoc_bmj_hist_3000.png"
    #title='Score test BMJ - term-doc matrix'

    # Not stemmed
    #=========================================================================
    ## Mean norm-sqrt (COSINE):
    #x2 = [19,3,22,1268,115,105,108,5,54,0,2,41,7]
    ## Median norm-sqrt (COSINE):
    #x1 = [128, 153, 819, 560, 612, 457, 204, 786, 81, 30, 603, 292, 184]
    ## Max norm-sqrt (COSINE):
    #x1 = [5, 4, 383, 1021, 44, 241, 107, 37, 8, 0, 24, 19, 27]
    
    ## Mean norm (COSINE - no sqrt):
    #x1 = [25, 2, 66, 692, 128, 139, 128, 3, 63, 0, 2, 52, 9]
    ## Median norm (COSINE - no sqrt):
    #x1 = [123, 179, 1210, 1004, 665, 502, 76, 343, 455, 59, 392, 430, 464]
    ## Max norm (COSINE - no sqrt):
    #x1 = [28, 7, 311, 1123, 166, 375, 109, 16, 21, 0, 39, 96, 47]

    ## Mean not-norm (SUM):
    #x1 = [23, 3, 362, 772, 35, 76, 144, 1, 45, 0, 25, 53, 5]
    ## Median not-norm (SUM):
    #x2 = [188, 459, 2150, 1878, 213, 852, 974, 83, 1353, 670, 2193, 689, 1210]
    ## Max not-norm (SUM):
    #x3 = [54, 10, 344, 2401, 235, 469, 495, 70, 6, 19, 441, 391, 26]
    #=========================================================================

    # Stemmed
    #=========================================================================
    ## Mean norm-sqrt (COSINE):
    #x2 = [19,3,55,840,171,83,101,5,35,0,4,29,7]
    ## Median norm-sqrt (COSINE):
    #x2 = [89, 151, 800, 1103, 400, 491, 315, 842, 825, 51, 494, 681, 185]
    ## Max norm-sqrt (COSINE):
    #x3 = [2, 10, 136, 1123, 68, 249, 130, 44, 8, 0, 47, 65, 25]
    
    ## Mean norm (COSINE - no sqrt):
    #x2 = [24, 2, 110, 710, 292, 113, 110, 3, 38, 0, 2, 51, 9]
    ## Median norm (COSINE - no sqrt):
    #x2 = [106, 252, 706, 1127, 532, 803, 179, 308, 751, 76, 472, 808, 473]
    ## Max norm (COSINE - no sqrt):
    #x3 = [20, 11, 427, 1232, 210, 370, 108, 28, 22, 0, 62, 192, 56]
    
    ## Mean not-norm (SUM):
    #x4 = [23, 3, 720, 746, 44, 60, 158, 1, 33, 0, 27, 88, 5]
    ## Median not-norm (SUM):
    #x2 = [161, 472, 1708, 1862, 405, 994, 789, 97, 1252, 907, 2135, 1079, 1095]
    ## Max not-norm (SUM):
    #x4 = [120, 6, 10, 2374, 228, 360, 566, 62, 8, 7, 394, 496, 26]
    #=========================================================================


    ##########################################################################
                                    #TermLabel#
    ##########################################################################

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # TEST 1 : Found on our own from orpha.net#
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    #diseases=['Ap','Ru','Aa','Aa','Ac','Ac','Ac','Ac','Bi','Br','Ch','Ch','Co','Om','Da','Ic','Em','Co','Fi','Ac','Os','Pr','He','Hy','Ja','Ja','Je','Ja','Mu','Tr']
    #graphName="diseaseMatrix_orphan_hist_NOTnorm_3000.png"
    #title='Score test Orphan.net - disease matrix'

    # Not stemmed
    #=========================================================================
    ## Norm (COSINE sqrt):
    #x1 = [76,257,0,20,122,41, 9,1912,16,1,448,128,1,13, 5,0,33,380, 20,1687,39,47,26,4,33,1,83,33, 46,0]

    ## Norm (COSINE - no sqrt):
    #x2 = [95,599,0,76,307,99,47,2989,28,3,430,165,7,37,11,7,97,717,150, 562,74,64,31,5,89,1,75,89,222,1]

    ## Not norm (SUM)
    #x3 = [9,123,4,10,4,81,109,601,3,7,68,9,0,2,1, 6,0,3,0,3000,0,8, 5,107,46,4,2,46,2,55]
    #=========================================================================

    # Stemmed
    #=========================================================================
    ## Norm (COSINE):
    #x1 = [74,263,0,19,106,44,12, 635,19,1,446,133, 4,13, 4,0, 80,391,122,2137, 74,54,12,2,30,1,99,30,162,0]

    ## Norm (COSINE - no sqrt)
    #x2 = [94,553,0,80,284,94,51,1454,32,1,433,181,10,33,18,7,169,710,334, 704,167,65,26,8,74,1,83,74,468,1]

    ## Not norm (SUM)
    #x1 = [9,90,17, 9,4,86,79,105,2,7,64,16,0,2,1, 6,0,2,0,3000,1,9,3, 84,39,3,1,39,2,59]
    #=========================================================================

    #~~~~~~~~~~~~~~~~~~~#
    # TEST 2 : From BMJ #
    #~~~~~~~~~~~~~~~~~~~#

    #diseases=['Infec','Cushi','Eosin','Ehrli','Neuro','Pheoc','Creut','Churg','Derma','Cat S','TEN','MELAS','Bruga']
    #graphName="diseaseMatrix_bmj_hist_norm_3000.png"
    #title='Score test BMJ - disease matrix'

    # Not stemmed
    #=========================================================================
    ## Norm (COSINE):
    #x1 = [16,37,375,2001,270,1037,25,6, 0,1, 97, 45,25]

    ## Norm (COSINE - no sqrt)
    #x2 = [31,62,474,2220,377,1225,93,8,20,5,227,118,94]

    ## Not norm (SUM)
    #x3 = [ 6,1,323, 691,30,427,8,2,4,0,3,19,6]
    #=========================================================================

    # Stemmed
    #=========================================================================
    ## Norm (COSINE):
    #1 = [25,37,748,1970,384,1053,25,2, 0,1,102, 68,30]

    ## Norm (COSINE - no sqrt)
    #2 = [37,63,872,1963,533,1198,93,4,18,9,230,221,91]

    # Not norm (SUM)
    #x1 = [5,1,597,511,29,413,6,1,3,0,3,26,6]
    #=========================================================================

    ##########################################################################
                            # TermLabel - Blind tests #
    ##########################################################################

    diseases=["Fibrodysplasia","Adrenoleukodystrophy","Papillon Lefevre","Kleine Levin","?"]
    graphName=""
    title=""

    x1 = [20,'Not found',6,2,'?']

    # "Adrenoleukodystrophy  autosomal  neonatal form" found at '1718'
    # "Childhood-onset cerebral X-linked adrenoleukodystrophy" not found

    ##########################################################################


    fig=figure(figsize=(8,5))
    ax=fig.add_subplot(1,1,1)

    # for 3 bars
#     cx1 = 'green'
#     cx2 = 'red'
#     cx3 = 'blue'

    # for four bars
    cx1 = '#29dbda'
    cx2 = '#2943db'
    cx3 = '#ec1008'
    cx4 = '#f66b5a'

    # for three bars
#     lx1 = 'Cosine, normalized, sqrt'
#     lx2 = 'Cosine, normalized, no sqrt'
#     lx3 = 'Sum, not normalized'

    # for four bars.
    lx1 = 'Sum - disease matrix'
    lx2 = 'Mean - cosine, sqrt, Term document matrix'
    lx3 = 'Max - cos, sqrt, Term document matrix'
    lx4 = 'Mean sum - Term document matrix'

    # Font size in legend
    rc('legend', fontsize='small')

    # For four bars
    xlen=len(x1)*8
    step = 8

    # For three bars
#     xlen=len(x1)*6
#     step = 6
    
    # For two bars
    #    xlen=len(x1)*4
    #    step=4

    x1_log=map(lambda x: math.log(x+1),x1)
    x2_log=map(lambda x: math.log(x+1),x2)
    x3_log=map(lambda x: math.log(x+1),x3)
    x4_log=map(lambda x: math.log(x+1),x4)

    y1=mean(x1_log)
    print y1
    y2=mean(x2_log)
    print y2
    y3=mean(x3_log)
    print y3
    y4=mean(x4_log)
    print y4
    ax.plot([0,xlen],[y1,y1],color=cx1,linewidth=2)
    ax.plot([0,xlen],[y2,y2],color=cx2,linewidth=2)
    ax.plot([0,xlen],[y3,y3],color=cx3,linewidth=2)
    ax.plot([0,xlen],[y4,y4],color=cx4,linewidth=2)

    
    ax.bar(arange(0,xlen,step), x1_log, color=cx1, width=1, label=lx1+' avg='+str(y1)[:4])
    ax.bar(arange(1,xlen,step), x2_log, color=cx2, width=1, label=lx2+' avg='+str(y2)[:4])
    ax.bar(arange(2,xlen,step), x3_log, color=cx3, width=1, label=lx3+' avg='+str(y3)[:4])
    ax.bar(arange(3,xlen,step), x4_log, color=cx4, width=1, label=lx4+' avg='+str(y4)[:4])


    ax.set_xticks(range(step/2,xlen,step))
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
    print "Writing to "+graphName
    savefig("/home/bp/brep/barcharts/"+graphName)
    #    savefig("/home/henne/Documents/Projektet/bachelor/Grafer_og_tegninger/"+graphName)

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
