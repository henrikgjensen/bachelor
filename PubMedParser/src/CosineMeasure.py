import math
import scipy
import cPickle
import TextCleaner
import os
import SearchTermDoc 
from numpy import linalg
import IOmodule
import time

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Hashtable directory
_hashTablePath = _path+"/"+"term_doc/hashTables"

# Load the precomputed norm of each row-vector in the term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,'VLHash')

def cosineMeasure2(queryString, M_lil, M_csr, numberOfResults=20):

    """
    This method is for making the standard cosine measure between two
    vector or between a term doc matrix. Using the standard calculation

    vectormath.dot(q, d) / ||q|| ||d||

    Where q, d are vector.

    And ||v|| denotes the length of vector v.

    Returns a list of tuples containing:
    [(pmidHash, angle in degrees), ... ]

    THIS IS COMPUTATIONALLY TOO HEAVY TO DEAL WITH IT TAKES ABOUT 2
    MINUTES TO TRAVERSE THROUGH 50000 RECORDS.
    """

    # Makes the query vector a column vector with size
    # M_csc.shape[1]-1 x 1 where M size is approximately 456.xxx x 1
    queryVector = blowUpVector(queryString, M_csr.shape[1])

    # Calculate the length of query vector |qv|
    lengthOfqv = math.sqrt(len(queryString.split(' ')))

    # Extracts the row indices based on the query string
    searchIndices = SearchTermDoc.extractRowIndices(M_csc, queryString)
    
    # Combine the search indices into one large set of pmidHashes
    searchIndices=reduce(set.union,map(set,searchIndices))

    #   Vector length calculation made smart! Hopefully
    #   sqrt(sum(map((lambda x: math.pow(x,2)),row)))

    angleResults = []

    for index in searchIndices:
        # Should not matter whether you use '0' or ':' here. As getrow
        # returns a 1 x 456.xxx matrix
        row = M_csr.getrow(index)
        pmidHash = row[0,0]
        row[0,0]=0
        # Remember the right order of the dot product.
        # n x m DOT m x n = n x n. So what we want to
        # do is 1 x 456.543 DOT 456.453 x 1 = 1 x 1
        # Returns a list of tuple with
        # (pmidHash, angle in degrees)
# Live version
        angleResults.append(tuple(pmidHash,math.degree(math.arccos((queryVector * row)/(lengthOfqv*_vectorLength[pmidHash])))))
# Test version
        
        # Returns arccos in radians of the degree between the two
        # vectors.
#        angleResults.append(tuple((M_csc.getrow(index)[0,0]),math.acos((queryVector * row)/(lengthOfqv*math.sqrt(sum(map((lambda x: math.pow(x,2)),row)))))))

    return angleResults[:numberOfResults]    

def cosineMeasure(M_lil, M_csc, queryString):

    t1 = time.time()

    # Extract the relevant indices of the row-vectors (pmid-hashes)
    searchIndices,hashedSearchTerms = SearchTermDoc.extractRowIndices(M_csc, queryString)
    # Union the arrays to avoid searching each row more than once
    print map(len,searchIndices)
    searchIndices = reduce(set.union,map(set,searchIndices))
    print len(searchIndices)
    #print searchIndices
    #searchIndices = set(searchIndices)

    queryString = SearchTermDoc.modifySearchString(queryString)

    print hashedSearchTerms

    results=[]
    for pmidHash in searchIndices:
        Sum=0
        for termHash in hashedSearchTerms:
            Sum+=M_lil[pmidHash,termHash]
        results.append(((pmidHash,(1.0/len(hashedSearchTerms))*(1.0/_vectorLength[pmidHash])*Sum)))
    
    t2 = time.time()

    print "Time for cosine scoring:", (t2-t1)

    return results

def blowUpVector(queryString, size):

    """
    Helper function that makes a query vector be the same size as a
    vector from the term doc matrix and with its entries in the
    correct places.

    Returns a 456.xxx x 1 "vector", in reality it is a column matrix
    """

    queryVector = SearchTermDoc.modifySearchString(queryString)

    # Init empty query vector
    qVector = scipy.sparse.lil_matrix((size,1))

    # Look up all terms in queryVector and make a set count on that
    # positions to one.
    for term in queryVector:
        try:
            qVector[SearchTermDoc.termHashTable[term],0] = 1
        except:
            print "Did not locate term", term
            continue

    return qVector

def createVLHash(M_lil):

    if not os.path.isdir(_hashTablePath):
        os.mkdir(_hashTablePath)

    VLHash={}
    for pmidHash in range(M_lil.shape[0]):
        VLHash[pmidHash]=linalg.norm((M_lil.getrow(i).data[0])[1:])

    IOmodule.pickleOut(_hashTablePath, "VLHash", VLHash)
