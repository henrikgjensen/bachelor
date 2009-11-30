import TextCleaner
import os
import cPickle
import time

# Path to main folder
_path=os.getenv("HOME")+'/'
# Term-doc directory
_termDocDir="TermDoc"
# Term- and PMID-hash directory
_hashTablesDir="hashTables"
# Term-hash table file
_termHashTable="termHash.btd"
# PMID-hash table file
_pmidHashTable="pmidHash.btd"

_termHash=_path+_hashTablesDir+"/"+_termHashTable
_pmidHash=_path+_hashTablesDir+"/"+_pmidHashTable
_termHashData=open(_termHash)
_pmidHashData=open(_pmidHash)
_termHashTable=cPickle.load(_termHashData)
_pmidHashTable=cPickle.load(_pmidHashData)

print "Hashes loaded"

def loadHashes():

    termHash=_path+_hashTablesDir+"/"+_termHashTable
    pmidHash=_path+_hashTablesDir+"/"+_pmidHashTable
    termHashData=open(termHash)
    pmidHashData=open(pmidHash)
    termHashTable=cPickle.load(termHashData)
    pmidHashTable=cPickle.load(pmidHashData)

    print "Hashes loaded"

def calculateCorrelation(M_lil,M_csc,searchVector):

    totalTime1=time.time()

    termHashTable=_termHashTable
    #pmidHashTable=_pmidHashTable

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
    # Husk at vi stadig har problemet med det 0'te element i cols'ne!
    colList=[]
    for termHash in hashedSearchTerms:
        colList.append(M_csc.getcol(termHash)[1:].nonzero()[0])

    intersectedColSet=reduce(set.intersection,map(set,colList))
    t2=time.time()
    print "Compared",len(hashedSearchTerms),"vectors in "+str(t2-t1)

    rowVectors={}
    for pmidHash in intersectedColSet:
        rowVectors[pmidHash]=M_lil.getrow(pmidHash)[:,1:].nonzero()[0]

    totalTime2=time.time()
    print "Total time elapsed: "+str(totalTime2-totalTime1)

    print "Number of vectors: "+str(len(rowVectors))

    # revers=dict(zip(pmidHashTable.values(),pmidHashTable.keys()))
