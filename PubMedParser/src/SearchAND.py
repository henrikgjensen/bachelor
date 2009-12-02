import SearchTermDoc


def searchAND(M_lil,M_csc,searchVector)

    """
    Returns only rows that contain all the searched terms. In other words,
    there exists an implicit AND between each term in the query.

    Returned format:
    {PMIDhash1: array([termcount1,termcount2,...]), PMID2hash: ...}
    """

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