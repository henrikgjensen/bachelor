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
# TFIDF-matrix file name
_tfidfName = "TFIDFMatrix"

# Load the precomputed norm of each row-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'RLHash')

print "Hash loaded."

def _generateLogTFIDF(M_coo):

    totalTime1=time.time()

    numberOfDocs = M_coo.shape[0]

    print "Converting from coo to csc..."
    t1=time.time()
    M_csc=M_coo.tocsc()
    t2=time.time()
    print "Matrix converted to csc in",(t2-t1)

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
        idf = math.log(float(numberOfDocs) / len(docIndexVector))

        for docIndex in docIndexVector:
            # Retrieve the term frequency
            tf = tfidfMatrix[docIndex, termVectorIndex]
            if tf == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception
            # Calculate the log-transformation of the term-frequency
            tf = math.log(1 + tf)
            # Update the new matrix values
            tfidf=tf * idf
            tfidfMatrix[docIndex, termVectorIndex] = tfidf

    # Save the progress
    IOmodule.writeOutTDM(_termDocDir, _tfidfName, tfidfMatrix)

    totalTime2=time.time()
    print "Total time: "+str(totalTime2-totalTime1)

    return tfidfMatrix

def _normalizeVectorLengths(M_lil):

    t1=time.time()

    for row in range(1,1000):

        norm=_vectorLength[row]
        for col in (M_lil.getrow(row).nonzero()[1])[1:]:
            M_lil[row,col]=(M_lil[row,col])/norm

    t2=time.time()
    print "Total:"+str(t2-t1)

    # Save and overwrite the log_tfidf generate above
    IOmodule.writeOutTDM(_tfidfDir, _tfidfName, tfidfMatrix)


def runTFIDF(M_coo):

    print "Generating log_TFIDF..."
    TFIDFMatrix=_generateLogTFIDF(M_coo)
    print "Normalizing vector lengths..."
    _normalizeVectorLengths(TFIDFMatrix)
    print "Done."

