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
#_vectorLength = IOmodule.pickleIn(_hashTablePath,'CLHash')

# Load the precomputed norm of each row-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'RLHash')

print "Hashes loaded."

def generateLogTFIDF(M_coo):

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

            print tfidf ### line to be deleted later ###


def test(M_lil,M_csr,M_coo):

    t1=time.time()

    for row in range(1,1000):

        norm=_vectorLength[row]

        t3=time.time()
        for col in (M_coo.getrow(row).nonzero()[1])[1:]:
            M_lil[row,col]=(M_lil[row,col])/norm

        #M_csr.getrow(row).data[1:] += norm

        t4=time.time()
        print "Row "+str(row)+" done in "+str(t4-t3)

    t2=time.time()
    print "Total:"+str(t2-t1)

    return M_lil,M_csr,M_coo