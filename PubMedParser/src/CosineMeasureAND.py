import os
import SearchTermDoc
import IOmodule
import time

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
_hashTablePath = _path+"/"+"term_doc/hashTables"

# Load the precomputed norm of each row-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'VLHash')


def cosineMeasureAND(M_lil,M_csc,queryString)

    t1 = time.time()

    # Extract the relevant indices of the row-vectors (pmid-hashes)
    searchIndices,hashedSearchTerms = SearchTermDoc.extractRowIndices(M_csc, queryString)
    # Union the arrays to avoid searching each row more than once
    searchIndices = reduce(set.intersection,map(set,searchIndices))

    results=[]
    for pmidHash in searchIndices:
        Sum=0
        for termHash in hashedSearchTerms:
            Sum+=M_lil[pmidHash,termHash]
        results.append(((pmidHash,(1.0/len(hashedSearchTerms))*(1.0/_vectorLength[pmidHash])*Sum)))

    t2 = time.time()

    print "Time for cosine scoring on",len(searchIndices),"rows:",(t2-t1)

    return results

    """
    def searchAND(M_lil,M_csc,searchVector)

    
    #Returns only rows that contain all the searched terms. In other words,
    #there exists an implicit AND between each term in the query.

    #Returned format:
    #{PMIDhash1: array([termcount1,termcount2,...]), PMID2hash: ...}


    colList = SearchTermDoc.extractRowIndices(M_csc, searchVector)

    t1=time.time()
    intersectedColSet=reduce(set.intersection,map(set,colList))
    t2=time.time()
    print "Compared",len(hashedSearchTerms),"vectors in "+str(t2-t1)

    t1=time.time()

    rowVectors={}
    for pmidHash in intersectedColSet:
        rowVectors[pmidHash]=(M_lil.getrow(pmidHash).nonzero()[0])[1:]

    print "Number of vectors: "+str(len(rowVectors))
    t2=time.time()
    print "Returned vectors in: "+str(t2-t1)

    return rowVectors

    """