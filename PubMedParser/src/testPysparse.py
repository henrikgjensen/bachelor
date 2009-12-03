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


def testMatrixPS(fullpath):

    totalTime1=time.time()

    termHashTable=_termHashTable
    pmidHashTable=_pmidHashTable

    print "Loading matrix.."
    t1=time.time()
    spmatrix.ll_mat_from_mtx(fullpath)
    t2=time.time()
    print "Loaded matrix in "+str(t2-t1)

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
    t1=time.time()
    for termHash in hashedSearchTerms:
        colVectors[termHash]=M.col(termHash)
    t2=time.time()
    print "Found",len(colVectors),"column(s)"
    print "Located columns matrix in "+str(t2-t1)

    # Convert the matrix to a compressed-sparse-row matrix
    M=M.tocsr()

    # Get the rows expressed by the columns above
    rowVectors={}
    for item in colVectors.items():
        colHash=item[0]
        print "colhash: "+str(colHash)
        for pmidHash in item[1]:
            rowVectors[pmidHash]=M.getrow(pmidHash).nonzero()[0]

    totalTime2=time.time()

    print "Time elapsed in total: "+str(totalTime2-totalTime1)

    print "Number of vectors: "+str(len(rowVectors))
