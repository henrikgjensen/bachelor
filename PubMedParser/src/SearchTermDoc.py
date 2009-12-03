import TextCleaner
import os
import cPickle
import time
import IOmodule

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

# Hashes to be instantiated:
termHashTable=IOmodule.pickleIn(_hashTablesDir, "termHash")
pmidHashTable=IOmodule.pickleIn(_hashTablesDir, "pmidHash")
revPmidHashTable=dict(zip(pmidHashTable.values(),pmidHashTable.keys()))
print "Hashes loaded"


def modifySearchString(searchString):

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

    searchVector=modifySearchString(searchString)
    
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
    print "Found and returned column"+str(len(colList))+"vectors in: "+str(t2-t1)

    return colList, hashedSearchTerms


def vector2QueryScore():

    return None



def getPMID(hashedPMID):

    """
    This function simply returns the true PMID from the hashtable. It uses a
    reverse of the pmidHashTable dictionary for a O(1) time lookup.
    """

    return revPmidHashTable[hashedPMID]
