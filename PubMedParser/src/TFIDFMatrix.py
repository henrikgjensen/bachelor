import IOmodule
import math
import time
import os

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Hashtable directory
_hashTablePath = _subFolder+"/"+"hashTables"
# Term-doc directory
_termDocDir = _subFolder+"/"+"termDoc"

# Load the precomputed length of each column-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'CLHash')

def generateLogTFIDF(M_coo):

    numberOfDocs = M_coo.shape[0]

    print "Converting from coo to lil..."
    t1=time.time()
    tfidfMatrix=M_coo.tolil()
    t2=time.time()
    print "Matrix converted to lil in",(t2-t1)

    for termVectorIndex in range(1,M_coo.shape[1]+1):

        print "Progress: " + str(termVectorIndex)
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

    IOmodule.writeOutTDM(_termDocDir, "TFIDF_termdoc", tfidfMatrix)
