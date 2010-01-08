import SearchTermDoc 
import math

def sumMeasure(M_lil, M_csc, queryString):

    """

    """

    ### TEMP ###
    # (Lav precomputed RL-hash for labelmatrices hvis noedvendigt)
    #vectorLength=SearchTermDoc.createRLHash(M_lil, None,False)
    ############

    # Extract the relevant indices of the row-vectors (pmid-hashes)
    searchIndices,hashedSearchTerms = SearchTermDoc.extractRowIndices(M_csc, queryString)

    # Union the arrays to avoid searching each row more than once
    searchIndices = reduce(set.union,map(set,searchIndices))

    results=[]
    for pmidHash in searchIndices:
        Sum=0
        for termHash in hashedSearchTerms:
            Sum+=M_lil[pmidHash,termHash] #/ vectorLength[pmidHash]
        results.append((Sum,pmidHash))

    return results
