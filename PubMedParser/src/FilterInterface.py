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

        
    for termVector in range(M_csc.shape[1]):
        counter = 0
        termVector += 1
        print "Progress: " + str(len(allHashedTerms)-termVector)
        termVectorData = (M_csc.getcol(termVector).data)[1:]
        termVectorDoc = (M_csc.getcol(termVector).nonzero()[0])[1:]
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf = math.log(numberOfDocs / len(termVectorData))

        print "Length of term vector before:", len(termVectorData)

        for term in termVectorData:
            counter += 1

            if tfidfMatrix[termVectorDoc[counter], termVector] == 0:
                print "Looked up zero-value at: "+str(counter)+" "+str(term)
                raise Exception

            # Calculate the term frequency
            tf = tfidfMatrix[termVectorDoc[counter], termVector]
            tf = math.log(1 + tf)
            # Update the new matrix values
            tfidfMatrix[termVectorDoc[counter], termVector] = tf * idf

        print "Length of term vector after (for the tfidf matrix):", counter

    IOmodule.writeOutTDM("/root/The_Hive/term_doc/tfidf_termDoc", "TFIDF_termdoc", tfidfMatrix)

###################