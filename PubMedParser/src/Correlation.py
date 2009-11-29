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

def calculateCorrelation(M,searchVector):

    t1=time.time()

    termHashTable=_termHashTable
    pmidHashTable=_pmidHashTable

    # Make sure hashes are loaded:
    if len(termHashTable)==0 or len(pmidHashTable)==0:
        print "Make sure to loaded hashes first!"
        raise Exception()

    # Convert the sparse matrix to a compressed-sparse-column matrix
    M=M.tocsc()

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

    # Locate columns containing the given terms
    colVectors={}
    for termHash in hashedSearchTerms:
        colVectors[termHash]=M.getcol(termHash).nonzero()[0]

    print "Found",len(colVectors),"column(s)"

    # Convert the matrix to a compressed-sparse-row matrix
    M=M.tocsr()

    # Get the rows expressed by the columns above
    rowVectors={}
    for item in colVectors.items():
        colHash=item[0]
        print "colhash: "+str(colHash)
        for pmidHash in item[1]:
            print "pmidHash: "+str(pmidHash)
            rowVectors[pmidHash]=M.getrow(pmidHash).nonzero()[0]

    t2=time.time()
        
    print "Time elapsed: "+str(t2-t1)

    print "Number of vectors: "+str(len(rowVectors))

    # revers=dict(zip(pmidHashTable.values(),pmidHashTable.keys()))
