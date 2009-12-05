
###################

import IOmodule
import math
#import SearchTermDoc
import time
import os

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
_hashTablePath = _path+"/"+"term_doc/hashTables"

# Load the precomputed length of each column-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'CLHash')

def generateLogTFIDF(M_coo):

    numberOfDocs = M_coo.shape[0]
    #allHashedTerms = sorted(SearchTermDoc.termHashTable.values())

    print "Converting from coo to lil..."
    t1=time.time()
    tfidfMatrix=M_coo.tolil()
    t2=time.time()
    print "Matrix converted in",(t2-t1)

#    print "Making a csc_matrix format..."
#    t1=time.time()
#    M_csc=M_coo.tocsc()
#    t2=time.time()
#    print "Made format in",(t2-t1)

#    del M_coo

#    print "Making a dok_matrix format..."
#    t1=time.time()
#    M_dok=M_coo.todok()
#    t2=time.time()
#    print "Made format in",(t2-t1)


    for i,j,v in zip(M_coo.row, M_coo.col, M_coo.data):
        m = tfidfMatrix[i,0] # row number = doc index
        n = tfidfMatrix[0,j] # column number = term index
        
        idf = math.log(numberOfDocs / _vectorLength[n])
        tf = math.log(1+v)

        tfidfMatrix[m,n] = tf*idf

        print "Coordinates: ("+str(m)+","+str(n)+")"


    """
    for termVectorIndex in range(tfidfMatrix.shape[1]):
        termVectorIndex += 1
        print "Progress: " + str(len(allHashedTerms)-termVectorIndex)
        #termVectorData = (M_csc.getcol(termVector).data)[1:]
        docIndexVector = (M_csc.getcol(termVectorIndex).nonzero()[0])[1:]
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf = math.log(numberOfDocs / len(docIndexVector))

        for docIndex in docIndexVector:
            # Calculate the term frequency
            tf = tfidfMatrix[docIndex, termVectorIndex]
            if tf == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception
            tf = math.log(1 + tf)
            # Update the new matrix values
            tfidfMatrix[docIndex, termVectorIndex] = tf * idf

    IOmodule.writeOutTDM("/root/The_Hive/term_doc/tfidf_termDoc", "TFIDF_termdoc", tfidfMatrix)
    """
###################