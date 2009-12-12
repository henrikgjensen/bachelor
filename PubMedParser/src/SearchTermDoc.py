import TextCleaner
import os
import time
import IOmodule
from numpy import linalg

mainFolder = 'The_Hive'
subFolder = 'search_engine'

# Path to main folder
_path=os.getenv("HOME")+'/'+mainFolder
# Term-doc directory
_termDocDir=_path+'/'+'term_doc'+'/'+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_path+'/'+'term_doc'+'/'+"hashTables"

# If subFolder do not exists
if not os.path.isdir(_path+'/'+subFolder):
    os.mkdir(_path+'/'+subFolder)

####################################################################
#### Use stopword-removed TermDoc ##################################
####################################################################

 # Hashes
termHashTable=IOmodule.pickleIn(_hashTablesDir, "termHash")
pmidHashTable=IOmodule.pickleIn(_hashTablesDir, "pmidHash")
revPmidHashTable=dict(zip(pmidHashTable.values(),pmidHashTable.keys()))

####################################################################
#### Use stopword-removed and Porter-stemmed (english) TermDoc: ####
####################################################################

 # Stemmed hashes
#termHashTable=IOmodule.pickleIn(_hashTablesDir, "termHash_stemmed")
#pmidHashTable=IOmodule.pickleIn(_hashTablesDir, "pmidHash_stemmed")
#revPmidHashTable=dict(zip(pmidHashTable.values(),pmidHashTable.keys()))

####################################################################


print "Hashes loaded"


def _modifySearchString(searchString):

    """
    Takes a search string and returns a list of sanitized search terms.
    """

    # Sanitize the search vector and convert it to a list of terms.
    sanitizer=TextCleaner.sanitizeString()
    searchVector=[term.lower() for term in sanitizer.sub(' ', searchString).split(' ') if term!='']

    return searchVector


def extractRowIndices(M_csc,searchString):

    """
    Given a csc_matrix and a search string, this function extracts the relevant
    rows in the term-doc matrix. It looks up the search terms in the hash list
    (if they exist) and returns a list of all the PMID-indices that contain the
    given term(s).

    Return format: [array([rowindex1 of term1, rowindex2 of term1 ,...]),array...]
    """

    t1=time.time()

    searchVector=_modifySearchString(searchString)
    
    # Look up hashes for terms.
    hashedSearchTerms=[]
    for term in searchVector:
        try:
            termHash=termHashTable[term]
        except:
            print "Did not locate",term
            continue
        hashedSearchTerms.append(termHash)
    print "Search vector:",str(searchVector),". Corresponding hash:",str(hashedSearchTerms)

    # Extract all the indices of the non-zero elements in the columns.
    colList=[]
    for termHash in hashedSearchTerms:
        colList.append((M_csc.getcol(termHash).nonzero()[0])[1:])

    t2=time.time()
    print "Found and returned",len(colList),"column vector(s) in: "+str(t2-t1)

    return colList, hashedSearchTerms


def extractColVectors(M_csc, termHashes):

    """
    Does the same as 'extractRowIndices' but takes a hashlist instead of a
    querystring and returns a list of values instead of a list of row indices

    Format: [array1,array2,...]
    """

    termHashes=sorted(termHashes)

    colList=[]
    for termHash in termHashes:
        print str(len(termHashes)-termHash)
        colList.append((M_csc.getcol(termHash))[1:].data)

    return colList


def createRLHash(M_lil,filename):

    """
    Precompute and save the norm of each row vector in the term-doc matrix.
    """

    t1=time.time()

    if not os.path.isdir(_hashTablesDir):
        os.mkdir(_hashTablesDir)

    RLHash={}
    count=0
    for pmidHash in range(1,M_lil.shape[0]+1):
        RLHash[pmidHash]=linalg.norm((M_lil.getrow(pmidHash).data[0])[1:])
        count+=1
        print "Hashes created: "+str(count)

    IOmodule.pickleOut(_hashTablesDir, filename, RLHash)

    t2=time.time()
    print "Created and saved RowLength-hash in: "+str(t2-t1)


def createCLHash(M_coo,filename):

    """
    Precompute and save the length of each column vector in the term-doc matrix.
    Here the length refers to the number of elements.
    """

    t1=time.time()

    if not os.path.isdir(_hashTablesDir):
        os.mkdir(_hashTablesDir)

    M_lil=(M_coo.transpose()).tolil()

    CLHash={}
    count=0
    for termHash in range(1,M_coo.shape[1]+1):
        termVectorLength=len((M_lil.getrow(termHash).nonzero()[0])[1:])
        CLHash[termHash]=termVectorLength
        count+=1
        print "Hashes created: "+str(count)+". Length:"+str(termVectorLength)

    IOmodule.pickleOut(_hashTablesDir, filename, CLHash)

    t2=time.time()
    print "Created and saved ColumnLength-hash in: "+str(t2-t1)


def getPMIDList(hashedPMIDList):

    """
    This function simply returns a list of the 'true' PMIDs from the hashtable.
    It uses a reverse of the pmidHashTable dictionary for a O(1) time lookup.
    """

    pmidList=[]
    for hashedPMID in hashedPMIDList:
        pmidList.append(revPmidHashTable[hashedPMID])

    return pmidList
