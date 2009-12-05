
###################

import IOmodule
import math
import SearchTermDoc
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
    allHashedTerms = sorted(SearchTermDoc.termHashTable.values())


    #print "Transposing coo matrix"
    #t1=time.time()
    #MT_coo=M_coo.transpose()
    #t2=time.time()
    #print "Matrix transposed in",(t2-t1)

    print "Converting from coo to lil..."
    t1=time.time()
    tfidfMatrix=M_coo.tolil()
    t2=time.time()
    print "Matrix converted to lil in",(t2-t1)

#    print "Making a csc_matrix format..."
#    t1=time.time()
#    M_csc=M_coo.tocsc()
#    t2=time.time()
#    print "Made format in",(t2-t1)

#    del M_coo

    for row in range(numberOfDocs):
        row+=1
        subMatrix=tfidfMatrix[row,1:].tocoo()
        for i,j,v in zip(subMatrix.row, subMatrix.col, subMatrix.data):
            #m = tfidfMatrix[i,0]
            #n = tfidfMatrix[0,j]

            idf = math.log(numberOfDocs / _vectorLength[j])
            tf = math.log(1 + v)

            tfidfMatrix[i,j] = idf*tf

        print "Row "+str(row)+" done."

    """
    for termVectorIndex in range(M_coo.shape[1]):
        termVectorIndex += 1
        print "Progress: " + str(len(allHashedTerms)-termVectorIndex)
        #termVectorData = (M_csc.getcol(termVector).data)[1:]
        docIndexVector = (T_tfidfMatrix.getrow(termVectorIndex).nonzero()[1])[1:]
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf = math.log(numberOfDocs / len(docIndexVector))

        #row=T_tfidfMatrix[termVectorIndex,1:]
        #T_tfidfMatrix[termVectorIndex,1:]=map(lambda x: math.log(1+x)*idf,row)

        for docIndex in docIndexVector:
            # Calculate the term frequency
            tf = T_tfidfMatrix[termVectorIndex,docIndex]
            if tf == 0:
                print "Looked up zero-value at: ("+str(termVectorIndex)+" "+str(docIndex)+")"
                raise Exception
            tf = math.log(1 + tf)
            # Update the new matrix values
            T_tfidfMatrix[termVectorIndex,docIndex] = tf * idf
    """
    """
    for termVectorIndex in range(M_coo.shape[1]):
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
    """

    tfidfMatrix=T_tfidfMatrix.transpose()

    IOmodule.writeOutTDM("/root/The_Hive/term_doc/tfidf_termDoc", "TFIDF_termdoc", tfidfMatrix)

###################