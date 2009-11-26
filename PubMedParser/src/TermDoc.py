import RecordHandler
import IOmodule
from scipy import sparse
import WordCounter
import os
import cPickle
import TextCleaner

path=os.getenv("HOME")+'/'

def gatherMatrixData(dir, filename):

    """
    This function utilizes the RecordHandler module to create and structure the
    data to populate the term-doc matrices.

    It takes a MedLine record directory (full path) and the records file to
    gather data from.

    It returns a doc-term list on the form: [[PMID,[(term1,count1),...],...]
    """

    l = []
    records = RecordHandler.loadMedlineRecords(dir, filename)
    fields = RecordHandler.readMedlineFields(records, ['AB'])
    for entry in fields.items():
        l.append(WordCounter.wc(entry[0], entry[1]['AB']))

    return l

def populateMatrix(m, n, termDoc, termHashTable, pmidHashTable):

    """
    This function creates and populates the term-doc matrices.

    It takes the matrix dimensions (row: m, col: n) and the term-doc data,
    structered as returned by the 'gatherMatrixData' function.

    It returns a sparse matrix, a term list and pmid (doc) list.

    Structure: If term A occurs x times in doc B, the coordinate of x in matrix M
    is given by the index: x = M[list-index of B, list-index of A].
    """
    
    M = sparse.lil_matrix((m, n))

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


def medlineDir2MatrixDir(medlineDir, m, n,termHash, pmidHash):

    """
    This function converts a directory of MedLine records to a new directory of
    corresponding matrices.

    It takes a MedLine record directory (full path) and the matrix dimensions
    (row: m, col: n).

    It creates a directory (in the home folder) named 'diseaseMatrices' and
    stores the matrices as 'pickeled' .bdt files, named by the disease name.
    """

    files = sorted([f for f in os.listdir(medlineDir) if os.path.isfile(medlineDir + f)])

    termHashData=open(termHash)
    pmidHashData=open(pmidHash)
    termHashTable=cPickle.load(termHashData)
    pmidHashTable=cPickle.load(pmidHashData)

    counter = 0
    for file in files:
        data = gatherMatrixData(medlineDir, file)
        M = populateMatrix(m, n, data,termHashTable, pmidHashTable)
        diseaseName = file[0:file.find('.txt')]
        IOmodule.writeOutTDM('diseaseMatrices', diseaseName, M)
        counter += 1
        #print str(counter) + " matrices made." + "Term length: " + str(len(termList))


def createHashes(medlineDir):

    files = sorted([f for f in os.listdir(medlineDir) if os.path.isfile(medlineDir + f)])

    termHashTable={}
    pmidHashTable={}
    termCounter = 0
    pmidCounter = 0

    # Get the regex pattern that sanitizeses strings.
    sanitize = TextCleaner.sanitizeString()

    for file in files:
        records = RecordHandler.loadMedlineRecords(medlineDir, file)

        # Hash PMID's
        for diseaseRecords in records.values():
            for record in diseaseRecords:
                pmid=record[0]
                if pmid not in pmidHashTable:
                    pmidCounter+=1
                    pmidHashTable[pmid]=pmidCounter

                # Hash terms
                termList = [word.lower() for word in sanitize.sub(' ', record[1]['AB']).split(' ') if word != '']
                for term in termList:
                    if term not in termHashTable:
                        termCounter+=1
                        termHashTable[term]=termCounter
                    else: continue
                
        print str(termCounter)+" terms hashed. "+str(pmidCounter)+" pmids hashed."

    IOmodule.pickleOut("hashTables", "termHash", termHashTable)
    IOmodule.pickleOut("hashTables", "pmidHash", pmidHashTable)

    return termHashTable, pmidHashTable


def createTermDoc(subMatrixDir,termDocDir,termHash,pmidHash,refreshHash=False):

    path=os.getenv("HOME")+'/'
    files = sorted([f for f in os.listdir(path+subMatrixDir) if os.path.isfile(path+subMatrixDir + f)])
    print path+subMatrixDir

    termHashData=open(termHash)
    pmidHashData=open(pmidHash)
    termHashTable=cPickle.load(termHashData)
    pmidHashTable=cPickle.load(pmidHashData)

    m=len(termHashTable)
    n=len(pmidHashTable)

    termDoc = sparse.lil_matrix((m,n))

    for file in files:
        subMatrix=IOmodule.readInTDM(subMatrixDir, file)
        subMCopy=subMatrix.todok()
        for i,j,v in zip(subMatrix.row, subMatrix.col, subMatrix.data):
            m = subMCopy[i,0]
            n = subMCopy[0,j]

            # Make sure not to add index's
            if m==0 or n==0:
                continue

            termDoc[m,n] += v
        print "Added",file

    return termDoc

    """
    for file in files:
        subMatrix=readInTDM(subMatrixDir, file)

        for i,j,v in zip(subMatrix.row, subMatrix.col, subMatrix.data):
            m = subMatrix[i,0]
            n = subMatrix[0,j]
            MLarge[m,n] += v
    """
    """
    t1 = time.time()

    MSmall2 = sparse.coo_matrix(MSmall)

    for i,j,v in zip(MSmall2.row, MSmall2.col, MSmall2.data):
        m = MSmall[i,0]
        n = MSmall[0,j]

        MLarge[m,n] += v

    t2 = time.time()
    print 'Time used: ',(t2-t1)
    """

    return None