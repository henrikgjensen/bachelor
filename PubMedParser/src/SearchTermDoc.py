import TextCleaner
import os
import cPickle
import time

mainFolder = 'The_Hive'
subFolder = 'search_engine'

# Path to main folder
_path=os.getenv("HOME")+'/'+mainFolder
# Term-doc directory
_termDocDir=_path+'/'+'term_doc'+'/'+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_path+'/'+'term_doc'+'/'+"hashTables"
# Term-hash table file
_termHashTable="termHash.btd"
# PMID-hash table file
_pmidHashTable="pmidHash.btd"

_path+=_path+'/'+subFolder

# If subFolder do not exists
if not os.path.isdir(_path):
    os.mkdir(_path)

# Hashes to be instansiated:
_termHash=_hashTablesDir+"/"+_termHashTable
_pmidHash=_hashTablesDir+"/"+_pmidHashTable
_termHashData=open(_termHash)
_pmidHashData=open(_pmidHash)
_termHashTable=cPickle.load(_termHashData)
_pmidHashTable=cPickle.load(_pmidHashData)
_revPmidHashTable=revers=dict(zip(pmidHashTable.values(),pmidHashTable.keys()))
print "Hashes loaded"

def extractRelevantVectors(M_lil,M_csc,searchVector):

    totalTime1=time.time()

    termHashTable=_termHashTable

    # Sanitize the search vector and convert it to a list of terms
    sanitizer=TextCleaner.sanitizeString()
    searchVector=[term.lower() for term in sanitizer.sub(' ', searchVector).split(' ') if term!='']

    # Look up hashes for terms
    hashedSearchTerms=[]
    for term in searchVector:
        try:
            termHash=termHashTable[term]
        except:
            print "Did not locate",term
            continue
        hashedSearchTerms.append(termHash)

    print "Search vector:",str(searchVector),". Corresponding hash:",str(hashedSearchTerms)

    t1=time.time()
    colList=[]
    for termHash in hashedSearchTerms:
        colList.append((M_csc.getcol(termHash).nonzero()[0])[1:])

    intersectedColSet=reduce(set.intersection,map(set,colList))
    t2=time.time()
    print "Compared",len(hashedSearchTerms),"vectors in "+str(t2-t1)

    rowVectors={}
    for pmidHash in intersectedColSet:
        rowVectors[pmidHash]=(M_lil.getrow(pmidHash).nonzero()[0])[1:]


    totalTime2=time.time()
    print "Total time elapsed: "+str(totalTime2-totalTime1)
    print "Number of vectors: "+str(len(rowVectors))

    return rowVectors

def getPMID(hashedPMID):

    """
    This function simply returns the true PMID from the hashtable. It uses a
    reverse of the pmidHashTable dictionary for a O(1) time lookup.
    """

    return _revPmidHashTable[hashedPMID]
