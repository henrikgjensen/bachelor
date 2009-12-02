import math
import scipy
import cPickle
import TextCleaner
import os
import SearchTermDoc 

_path = os.getenv("HOME")
# Term- and PMID-hash directory
_hashTablesDir=_path+'/'+'The_Hive'+'/'+'term_doc'+'/'+"hashTables"
# Term-hash table file
_termHashTable="termHash.btd"

_termHashData=open(_termHash)
_termHashTable=cPickle.load(_termHashData)


def cosineMeasure(queryString, termDocMatrix, numberOfResults=20):

    """
    This method is for making the standard cosine measure between two
    vector or between a term doc matrix. Using the standard calculation

    vectormath.dot(q, d) / ||q|| ||d||

    Where q, d are vector.

    And ||v|| denotes the length of vector v.
    """
    queryVector = blowUpVector(queryString)

    lengthOfqv = sqrt(len(queryString.split(' ')))

    searchSpace = SearchTermDoc.extractRowIndices(termDocMatrix_csc, queryString):
    
    angleResults = []
    for in searchSpace:
        angleResults.append((queryVector * row)/(lengthOfqv*sqrt(sum(map((lambda x -> math.pow(x,2)),row[1:])))))

    return angleResults[:numberOfResults]    

def blowUpVector(queryString, size):

    """
    Helper function that makes a query vector be the same size as a
    vector from the term doc matrix and with its entries in the
    correct places.
    """

    queryVector = SearchTermDoc.modifySearchString(queryString):

    # Init empty query vector
    qVector = scipy.sparse.lil_matrix((1,size))

    # Look up all terms in queryVector and make a set count on that
    # positions to one.
    for term in queryVector:
        try:
            qVector[0,termHashTable[term]] = 1
        except:
            print "Did not locate term", term
            continue

    return qVector
