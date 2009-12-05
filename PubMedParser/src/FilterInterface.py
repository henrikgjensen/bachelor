
###################

import math
import SearchTermDoc
import time

def generateLogTFIDF(M_coo):

    numberOfDocs = len(SearchTermDoc.pmidHashTable)
    allHashedTerms = SearchTermDoc.pmidHashTable.keys()

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

    print "Making a lil_matrix format..."
    t1=time.time()
    M_lil=tfidfMatrix.tocsc()
    t2=time.time()
    print "Made format in",(t2-t1)

    print "Extracting term vectors"
    t1=time.time()
    colList = SearchTermDoc.extractColVectors(M_csc, allHashedTerms)
    t2=time.time()
    print "Term vectors extracted in",(t2-t1)

    for termVector in colList:
        counter=0
        # Calculate the inverse document frequency
        # (Note that the length of each term vector is always greater than 0)
        idf=math.log(numberOfDocs/len(termVector))

        print "Length of term vector before:",len(termVector)

        for term in termVector:
            counter+=1

            if M[counter,term]==0:
                print "Looked up zero-value"
                raise Exception

            # Calculate the term frequency
            tf=M[counter,term]
            tf=math.log(1+tf)
            # Update the new matrix values
            tfidfMatrix[counter,term]=tf*idf

        print "Length of term vector after (for the tfidf matrix):",counter

    # writeout...

    return tfidfMatrix

###################