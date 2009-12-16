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


def search(M_lil, M_csc, queryString, top=20, AND=False):

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


    # Note: tror den her er unodvendig kompliceret.
    #top100=[result for result in results[:100]]

    # Retrieve the top 100 results as PMIDs
    #pmidList=SearchTermDoc.getPMIDList(top100)

    #print len(top100)

    resultDic={}
    for item in results[:top]:
        pmid=item[1] #SearchTermDoc.getPMID(item[1])
        labels=_labelHash[pmid]
        for label in labels:
            try:
                resultDic[label]+=item[0]
            except:
                resultDic[label]=item[0]

    resultList=sorted(resultDic.items(), key=lambda(k,v):(v,k), reverse=True)

    return resultList

def getScore(resultList,diseaseName):

    Found=False

    for result in resultList:
        if result[0]==diseaseName:
            print "<<<<<<<",diseaseName,">>>>>>>"
            print "Scored",resultList.index(result),"out of",len(resultList)
            print "Cosine score:",result[1]
            Found=True

    if not Found: print "Did not locate the disease"
        
            