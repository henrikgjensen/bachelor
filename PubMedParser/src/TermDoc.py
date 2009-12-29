import RecordHandler
import IOmodule
import FilterInterface
from scipy import sparse
import os
import TextCleaner
import time
from nltk import *
from TextCleaner import sanitizeString

# Main folder
_mainFolder=os.getenv("HOME")+"/"+"The_Hive"
# Phase subfolder
_subFolder = _mainFolder+"/"+"term_doc"
# MedLine record directory
_medlineDir=_mainFolder+"/data_acquisition/"+"medline_records"
# Term-doc directory
_termDocDir=_subFolder+"/"+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_subFolder+"/"+"hashTables"
# Disease label hash
_labelHash="labelHash"

########################################################################
#### Use only stopword-removal as filter: ##############################
########################################################################

 # Sub-matrix directory
#_subMatrixDir=_subFolder+"/"+"diseaseMatrices"
 # Hashtable filenames:
#_termHash="termHash"
#_pmidHash="pmidHash"
#_termDoc="TermDoc"
#_stemmer=False

########################################################################
#### Use stopword-removal and Porter-stemming (english) as filters: ####
########################################################################

 # Stemmed sub-matrix directory
_subMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed"
 # Stemmed hashtable filenames:
_termHash="termHash_stemmed"
_pmidHash="pmidHash_stemmed"
_termDoc="TermDoc_stemmed"
_stemmer=True


# Create main folder if it doesn't already exist.
if not os.path.isdir(_mainFolder):
        os.mkdir(_mainFolder)

# Create sub folder if it doesn't already exist..
if not os.path.isdir(_subFolder):
        os.mkdir(_subFolder)


def _wordCounter(pmid, string):

    """
    This function counts the number of occurences for each term in a text-string.

    It takes a PMID and a text-string

    It returns a list on the form [PMID1,[(term1,count1),...],PMID2,[...],...]
    """

    ll=[pmid,[]]


    # Run FreqDist on the split string, removing empty strings in the process
    fdist = FreqDist([word.lower() for word in string.split(' ') if word != ''])

    ll[1].extend(fdist.items())

    return ll

def _gatherMatrixData(filename):

    """
    This function utilizes the RecordHandler module to create and structure the
    data to populate the term-doc matrices. It currently also removes stopwords
    from the abstract.

    It takes the records' file name to gather data from.

    It returns a doc-term list on the form: [[PMID,[(term1,count1),...],...]
    """

    medlineDir=_medlineDir

    # Get the regex pattern that sanitize strings.
    sanitizer = sanitizeString()

    l = []
    records = RecordHandler.loadMedlineRecords(medlineDir, filename)
    fields = RecordHandler.readMedlineFields(records, ['AB','TI','MH'])
    for entry in fields.items():
        information=''
	# Get the title if any
        try:
		information=' '+entry[1]['TI']
        except:
		print 'Unable to find title in', entry[0]
	# Get the abstract if any
        try:
		information+=' '+entry[1]['AB']
        except:
		print 'Unable to find abstract in', entry[0]
	# Get all the mesh terms if any
	if 'MH' in entry[1]:
		for meshterm in entry[1]['MH']:
			information+=' '+meshterm

        # Sanitize the abstract
        information=sanitizer.sub(' ', information)
        # Remove english stopwords from the information
        information=FilterInterface.stopwordRemover(information)

        # OPTIONAL:
        # Stem the information
        if _stemmer: information=FilterInterface.porterStemmer(information)

        l.append(_wordCounter(entry[0],information))

    return l

def _populateMatrix(m, n, termDoc,termHashTable,pmidHashTable):

    """
    This function creates and populates the term-doc matrices.

    It takes the matrix dimensions (row: m, col: n), the term-doc data,
    structered as returned by the 'gatherMatrixData' function and the two hash
    tables (on dictionary form).

    It returns a sparse matrix.

    Structure: If term A occurs x times in doc B, the coordinate of x in matrix M
    is given by the index: x = M[list-index of B, list-index of A].
    """

    M = sparse.lil_matrix((m, n))
    print M.shape
    termList = []
    pmidList = []

    for item in termDoc:
        pmidIndex = 0
        termIndex = 0
        pmid=item[0]
        termCountList=item[1]

        if pmid not in pmidList:
            pmidList.append(pmid)
            pmidIndex = len(pmidList)
            M[pmidIndex,0]=pmidHashTable[pmid]
        else:
            pmidIndex = pmidList.index(pmid)+1

        for tc in termCountList:
            term=tc[0]
            termCount=tc[1]
            
            if term not in termList:
                termList.append(term)
                termIndex = len(termList)
                M[pmidIndex, termIndex] = termCount
                M[0,termIndex]=termHashTable[term]
            else:
                termIndex = termList.index(term)+1
                M[pmidIndex, termIndex] += termCount

    return M

def medlineDir2MatrixDir():

    """
    This function converts a directory of MedLine records to a new directory of
    corresponding term-doc matrices.

    It takes the matrix dimensions (row: m, col: n).

    It creates a directory (in the home folder) named 'diseaseMatrices' and
    stores the matrices as 'MatrixMarket' .mtx files, named by the disease name.
    """

    termHashTable=IOmodule.pickleIn(_hashTablesDir, _termHash)
    pmidHashTable=IOmodule.pickleIn(_hashTablesDir, _pmidHash)

    files = sorted([f for f in os.listdir(_medlineDir+"/") if os.path.isfile(_medlineDir+"/" + f)])

    counter = 0
    for file in files:
        data = _gatherMatrixData(file)

        # [[PMID,[(term1,count1),...],...]

        # Get matrix dimensions (+1 for the [0,0] field)
        m=len(data)+1
        n=1
        test={}
        for pmid in data:
            for term in pmid[1]:
                test[term[1]]=0
        print "L:",len(test)

        M = _populateMatrix(m, n, data,termHashTable, pmidHashTable)
        diseaseName = file[0:file.find('.txt')]
        IOmodule.writeOutTDM(_subMatrixDir, diseaseName, M)
        counter += 1
        print str(counter),"matrices made. Total number of terms:",len(M.getrow(0).nonzero()[0])


def createTermAndPmidHashes():

    """
    This function creates two hash tables of the PMID's and terms to be used
    for the term-doc matrix.

    Note that the terms are sanitized for any non-alphanumerical characters.
    And it is default to remove stop words.
    """

    medlineDir = _medlineDir
    hashTables = _hashTablesDir
    termHashTable={}
    pmidHashTable={}
    termCounter = 0
    pmidCounter = 0

    files = sorted([f for f in os.listdir(medlineDir+"/") if os.path.isfile(medlineDir+"/"+f)])

    # Get the regex pattern that sanitizeses strings.
    sanitizer = TextCleaner.sanitizeString()

    for file in files:
        records = RecordHandler.loadMedlineRecords(medlineDir, file)

        # *Note*
        # Parts of the following loops could be optimized by using dictionaries
        # for direct loopkups instead of linear lookups, but since it's not
        # important, optimization will have to wait for another day.

        # Hash PMID's
        for diseaseRecords in records.values():
            for record in diseaseRecords:
                pmid=record[0]
                if pmid not in pmidHashTable:
                    pmidCounter+=1
                    pmidHashTable[pmid]=pmidCounter

                information=''
                # Get the abstract
		try:
			information=' '+record[1]['AB']
		except:
			print 'Unable to get abstract', record[0]
		try:
			information+=' '+record[1]['TI']
		except:
			print 'Unable to get title for', record[0]

		if 'MH' in record[1]:
			for meshterm in record[1]['MH']:
				information+=' '+meshterm
		# We do not want to print this, as most of the
		# records do not have MeSH.
		# print 'Unable to get MeSH terms for', record[0]
		
                # Sanitize the information
                information=sanitizer.sub(' ', information)
                # remove stopwords from the abstract
                information=FilterInterface.stopwordRemover(information)

                # OPTIONAL:
                # Stem the abstract
                if _stemmer: information=FilterInterface.porterStemmer(information)

                termList = [word for word in information.split(' ') if word != '']
                for term in termList:
                    if term not in termHashTable:
                        termCounter+=1
                        termHashTable[term]=termCounter
                    else: continue
                
        print str(termCounter)+" terms hashed. "+str(pmidCounter)+" pmids hashed."

    IOmodule.pickleOut(hashTables, _termHash, termHashTable)
    IOmodule.pickleOut(hashTables, _pmidHash, pmidHashTable)

    return termHashTable, pmidHashTable


def createDiseaseLabelHash():

    """

    """

    t1 = time.time()

    files = sorted([f for f in os.listdir(_subMatrixDir+"/") if os.path.isfile(_subMatrixDir+"/" + f)])

    labelHash={}

    fileCount=0
    for file in files:
        subMatrix=IOmodule.readInTDM(_subMatrixDir, file)
        colMatrix=subMatrix.tocsc()

        pmids=colMatrix.getcol(0)[1:].data

        for pmid in pmids:
            try:
                labelHash[pmid].append(file[:-4])
            except:
                labelHash[pmid]=[]
                labelHash[pmid].append(file[:-4])
            
        fileCount+=1
        print "Remaining:",(len(files)-fileCount),"Completed",file[:-4]

    t2 = time.time()

    print 'Created disease label hash in:',str(t2-t1)

    IOmodule.pickleOut(_hashTablesDir, _labelHash, labelHash)


def createTermDoc(refreshHash=False):

    """
    This function creates a large term-doc martix from a directory of sub term-
    doc matrices.

    It returns a matrix with dimensions given by the specified hash tables.

    It also saves the matrix for later use as a MatrixMarket .mtx file.
    """

    t1 = time.time()

    if refreshHash:
        createTermAndPmidHashes()

    files = sorted([f for f in os.listdir(_subMatrixDir+"/") if os.path.isfile(_subMatrixDir+"/" + f)])
    
    termHashTable=IOmodule.pickleIn(_hashTablesDir, _termHash)
    pmidHashTable=IOmodule.pickleIn(_hashTablesDir, _pmidHash)


    # Need to add one due to non zero indexing
    m=len(pmidHashTable)+1
    n=len(termHashTable)+1

    termDoc = sparse.lil_matrix((m,n))

    # Insert values representing hashes
    for i in range(m): termDoc[i,0]=i
    termDoc[0,:]=range(n)

    for file in files:
        subMatrix=IOmodule.readInTDM(_subMatrixDir, file)
        subMCopy=subMatrix.todok()
        for i,j,v in zip(subMatrix.row, subMatrix.col, subMatrix.data):
            m = subMCopy[i,0]
            n = subMCopy[0,j]

            # Make sure not to add index's
            if m==0 or n==0:
                continue

            termDoc[m,n] += v
        print "Added",file

    IOmodule.writeOutTDM(_termDocDir, _termDoc, termDoc)

    t2 = time.time()

    print 'Time elapsed:',str(t2-t1)

    return termDoc
