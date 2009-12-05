import os
import SearchTermDoc 
import IOmodule
import time

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
_hashTablePath = _path+"/"+"term_doc/hashTables"

# Load the precomputed norm of each row-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'RLHash')



def cosineMeasureOR(M_lil, M_csc, queryString):

    t1 = time.time()

    # Extract the relevant indices of the row-vectors (pmid-hashes)
    searchIndices,hashedSearchTerms = SearchTermDoc.extractRowIndices(M_csc, queryString)
    # Union the arrays to avoid searching each row more than once
    searchIndices = reduce(set.union,map(set,searchIndices))

    results=[]
    for pmidHash in searchIndices:
        Sum=0
        for termHash in hashedSearchTerms:
            Sum+=M_lil[pmidHash,termHash]
        results.append(((pmidHash,(1.0/len(hashedSearchTerms))*(1.0/_vectorLength[pmidHash])*Sum)))
    
    t2 = time.time()

    print "Time for cosine scoring on",len(searchIndices),"rows:",(t2-t1)

    return results
