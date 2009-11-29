import TextCleaner

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


def calculateCorrelation(M,searchVector):

    # Load hash-lists
    termHash=_path+_hashTablesDir+"/"+_termHashTable
    pmidHash=_path+_hashTablesDir+"/"+_pmidHashTable
    termHashData=open(termHash)
    pmidHashData=open(pmidHash)
    termHashTable=cPickle.load(termHashData)
    pmidHashTable=cPickle.load(pmidHashData)

    # Convert the sparse amtrix to a compressed-sparse-column matrix
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

    # Locate pmids containing the given terms
    colIndices=[]
    for term in hashedSearchTerms:

        colIndices.append(M[0,term])

        print term
