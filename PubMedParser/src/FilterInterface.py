import IOmodule

###################

import math
import SearchTermDoc
import time

def generateLogTFIDF(M_coo):

    numberOfDocs = len(SearchTermDoc.pmidHashTable)
    allHashedTerms = sorted(SearchTermDoc.termHashTable.values())

    print "Duplicating matrix..."
    t1=time.time()
    tfidfMatrix=M_coo.copy()
    t2=time.time()
    print "Matrix duplicated in",(t2-t1)

    print "Converting from coo to lil..."
    t1=time.time()
    tfidfMatrix=tfidfMatrix.tolil()
    t2=time.time()
    print "Matrix converted in",(t2-t1)

    del M_coo

    print "Making a csc_matrix format..."
    t1=time.time()
    M_csc=tfidfMatrix.tocsc()
    t2=time.time()
    print "Made format in",(t2-t1)

    #print "Extracting term vectors"
    #t1=time.time()
    #colList = SearchTermDoc.extractColVectors(M_csc, allHashedTerms)
    #t2=time.time()
    #print "Term vectors extracted in",(t2-t1)

    #del M_csc

        
    for termVectorIndex in range(M_csc.shape[1]):
        counter = 0
        termVectorIndex += 1
        print "Progress: " + str(len(allHashedTerms)-termVectorIndex)
        #termVectorData = (M_csc.getcol(termVector).data)[1:]
        docIndexVector = (M_csc.getcol(termVectorIndex).nonzero()[0])[1:]
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf = math.log(numberOfDocs / len(docIndexVector))

        print "Length of term vector before:", len(docIndexVector)

        for docIndex in docIndexVector:
            counter += 1

            if tfidfMatrix[docIndex, termVectorIndex] == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception

            # Calculate the term frequency
            tf = tfidfMatrix[docIndex, termVectorIndex]
            tf = math.log(1 + tf)
            # Update the new matrix values
            tfidfMatrix[docIndex, termVectorIndex] = tf * idf

        print "Length of term vector after (for the tfidf matrix):", counter

    IOmodule.writeOutTDM("/root/The_Hive/term_doc/tfidf_termDoc", "TFIDF_termdoc", tfidfMatrix)

###################