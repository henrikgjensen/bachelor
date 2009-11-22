import RecordHandler
import IOmodule
from scipy import sparse
import WordCounter
import os

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
    interesting_records = RecordHandler.readMedlineFields(records, ['AB'])
    for entry in interesting_records.items():
        l.append(WordCounter.wc(entry[0], entry[1]['AB']))

    return l

def populateMatrix(m, n, termDoc):

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

        if item[0] not in pmidList:
            pmidList.append(item[0])
            pmidIndex = len(pmidList)-1
        else:
            pmidIndex = pmidList.index(item[0])

        for term in item[1]:
            if term[0] not in termList:
                termList.append(term[0])
                termIndex = len(termList)-1
                M[pmidIndex, termIndex] = term[1]
            else:
                termIndex = termList.index(term[0])
                M[pmidIndex, termIndex] += term[1]

    return M, termList, pmidList


def medlineDir2MatrixDir(medlineDir, m, n):

    """
    This function converts a directory of MedLine records to a new directory of
    corresponding matrices.

    It takes a MedLine record directory (full path) and the matrix dimensions
    (row: m, col: n).

    It creates a directory (in the home folder) named 'diseaseMatrices' and
    stores the matrices as 'pickeled' .bdt files, named by the disease name.
    """

    files = sorted([f for f in os.listdir(medlineDir) if os.path.isfile(medlineDir + f)])

    counter = 0
    for file in files:
        data = gatherMatrixData(medlineDir, file)
        M, termList, pmidList = populateMatrix(m, n, data)
        diseaseName = file[0:file.find('.txt')]
        IOmodule.writeOutTDM('diseaseMatrices', diseaseName, (M, termList, pmidList))
        counter += 1
        print str(counter) + " matrices made." + "Term length: " + str(len(termList))
