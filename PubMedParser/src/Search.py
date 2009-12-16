#! /usr/bin/python

import SearchInterface
import SearchTermDoc
import FilterInterface
import IOmodule
import os

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Hashtable directory
_hashTablePath = _subFolder+"/"+"hashTables"
# Set True for Porter-stemming
_stemmer=False

# Disease label hash
_labelHash = IOmodule.pickleIn(_hashTablePath,"labelHash")
print "Label hash loaded"


def search20(M_lil, M_csc, queryString, AND=False):

    """
    This function is still a work in progress..
    """

    # OPTIONAL:
    # Stem the information
    if _stemmer: queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasureOR(M_lil, M_csc, queryString)

    if AND: results=SearchInterface.cosineMeasureAND(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    results.sort()
    results.reverse()

    top20=[result[1] for result in results[:20]]

    # Retrieve the top 20 results as PMIDs
    pmidList=SearchTermDoc.getPMIDList(top20)

    pmidList=' '.join(pmid for pmid in pmidList)

    return pmidList


def search100(M_lil, M_csc, queryString, AND=False):

    """
    This function is still a work in progress..
    """

    # OPTIONAL:
    # Stem the information
    if _stemmer: queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasureOR(M_lil, M_csc, queryString)

    if AND: results=SearchInterface.cosineMeasureAND(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    results.sort()
    results.reverse()

    top100=[result for result in results[:100]]

    # Retrieve the top 100 results as PMIDs
    #pmidList=SearchTermDoc.getPMIDList(top100)

    print top100

    resultList={}
    for item in top100:
        pmid=SearchTermDoc.getPMID(item[1])
        try:
            resultList[pmid]+=item[0]
        except:
            resultList[pmid]=[]
            resultList[pmid].append(item[0])

    print resultList

    #pmidList=' '.join(pmid for pmid in pmidList)

#    return pmidList