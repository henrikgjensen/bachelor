#import os
import SearchTermDoc 
#import IOmodule
import time

# Main folder
#_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
#_hashTablePath = _path+"/"+"term_doc/hashTables"

######################################
#### Use stopword-removed TermDoc ####
######################################

 # Load the precomputed norm of each row-vector in the term-doc matrix.
#_vectorLength = IOmodule.pickleIn(_hashTablePath,'RLHash')

####################################################################
#### Use stopword-removed and Porter-stemmed (english) TermDoc: ####
####################################################################

 # Load the precomputed norm of each row-vector in the stemmed term-doc matrix.
#_vectorLength = IOmodule.pickleIn(_hashTablePath,'RLHash_stemmed')

import math
def cosineMeasureOR(M_lil, M_csc, queryString):

    """
    This function calculates the cosine score for each document containing one
    or more of the query-terms in the query string (thereby the implicit 'or'
    between each query-term).

    It returns a scored list of all the documents mentioned above.
    """

    t1 = time.time()

    # Extract the relevant indices of the row-vectors (pmid-hashes)
    searchIndices,hashedSearchTerms = SearchTermDoc.extractRowIndices(M_csc, queryString)

    # Union the arrays to avoid searching each row more than once
    searchIndices = reduce(set.union,map(set,searchIndices))

    results=[]
    for pmidHash in searchIndices:
        Sum=0
        for termHash in hashedSearchTerms:
            Sum+=math.sqrt(M_lil[pmidHash,termHash])
        results.append((Sum,pmidHash))

    t2 = time.time()

    #print "Time for cosine-scoring on",len(searchIndices),"rows:",(t2-t1)

    return results
