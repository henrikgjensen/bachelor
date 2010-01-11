import IOmodule as IO
import os
from scipy import sparse
from numpy import mat
import time

"""
Module used for creating a document matrix over the diseases, either
by summing or taking the average over the column of the sub disease
matrices.
"""

# Main folder
_mainFolder=os.getenv("HOME")+"/"+"The_Hive"
# Phase subfolder
_subFolder = _mainFolder+"/"+"term_doc"
# Term-doc directory
_termDocDir=_subFolder+"/"+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_subFolder+"/"+"hashTables"

########################################################################
#### Use only stopword-removal as filter: ##############################
########################################################################

_stemmer=False

if not _stemmer:
    # Sub-matrix directory
    _subMatrixDir=_subFolder+"/"+"new_diseaseMatrices"
    # Hashtable filenames:
    _termHash="termHash"
    _pmidHash="pmidHash"
    _termDoc="TermDoc"
    _label = 'LabelMatrix'

########################################################################
#### Use stopword-removal and Porter-stemming (english) as filters: ####
########################################################################
else:
    # Stemmed sub-matrix directory
    _subMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed"
    # Stemmed hashtable filenames:
    _termHash="termHash_stemmed"
    _pmidHash="pmidHash_stemmed"
    _termDoc="TermDoc_stemmed"
    _label = 'LabelMatrix_stemmed'

label=_label+'_tfidf'

# Name of disease filename
diseaseHash='diseaseHash_reduced'

def getColumnSum(subTermDoc, avg=False):

    """
    Recieves a sub term document matrix and optional flag for getting
    average instead of sum.
    """

    sumVector = sparse.lil_matrix((2,subTermDoc.shape[1]))
    sumVector = sumVector.todense()

    if avg:
        counter = 0

    for i in range(1, subTermDoc.shape[0]):
        row = subTermDoc.getrow(i)
        row = row.todense()[0,1:]

        sumVector[1,1:] += row

        if avg:
            counter+=1

    if avg:
        sumVector[1,1:]/=counter
        
    return sparse.lil_matrix(sumVector)

def constructLabelMatrix(subMatrixDir, avg=False, output=False, time_log=False):

    """
    Recieves a subMatrixDir goes through all the files and sums up the
    column of it, creating a single row vector containing the sum of
    all column in the sub term doc matrix. It then proceeds to making
    a disease term doc, based on these row vector

    Optional flags are:

    avg, takes the average over the columns of the sub matrices
    instead of the sum.

    output, makes the funtion produce additional output

    time_log, makes the function print out how much time is spend on
    what
    """

    if output:
        print 'Initialising...'

    if time_log:
        t1 = time.time()

    files = IO.getSortedFilelist(subMatrixDir)

    termHashTable = IO.pickleIn(_hashTablesDir, _termHash)
    diseaseHashTable = IO.pickleIn(_hashTablesDir, diseaseHash)

    labelMatrix=sparse.lil_matrix((len(files)+1,len(termHashTable)+1))

    # Initialize subTermSum to something
    subTermSum = sparse.lil_matrix((1,1))

    if output:
        print 'Done initialising label matrix of size', str((len(files)+1,len(termHashTable)+1))
        count = 0

    if time_log:
        print 'Time for initialization:', str(time.time() - t1)[:4]

    for f in files:
        if time_log:
            t2 = time.time()
        diseaseName = f[0:f.find('.mtx')]
        if output:
            print 'Processing', diseaseName
            count+=1
            print 'Numbers remaining', len(files)-count

        subTermDoc = IO.readInTDM(subMatrixDir, diseaseName)
        subTermDoc = subTermDoc.tolil()

        # If the subTermDoc contains nothing, just skip it
        if(subTermDoc.shape[0] == 1 and subTermDoc.shape[1] == 1):
            continue
        
        subTermSum = getColumnSum(subTermDoc,avg)
        subTermSum[0,0] = diseaseHashTable[diseaseName]
        subTermSum[0,:] = subTermDoc.getrow(0)

        labelMatrix[diseaseHashTable[diseaseName],0] = diseaseHashTable[diseaseName]
        
        if time_log:
            print 'Time for', diseaseName, str(time.time() - t2)[:4]
            t3 = time.time()

        if output:
            print 'Filling in values in label matrix for', diseaseName
        for columnIndex in range(1,subTermSum.shape[1]):
            labelMatrix[diseaseHashTable[diseaseName],subTermSum[0,columnIndex]] = subTermSum[1,columnIndex]
        if time_log:
            print 'Values filled into label matrix in', str(time.time() - t3)[:4]
        if output:
            print 'Completed filling in values.'

    # Hack way of making term hashes
    labelMatrix[0,:] = range(0,len(termHashTable))
    
    if output:
        print 'Done making label matrix, writing to'

    IO.writeOutTDM(_termDocDir, label, labelMatrix)

    if output:
        print 'Done wrting label matrix.'
        
    return labelMatrix

def createDiseaseHash(dir,output=False):

    """
    Recieves a directory containing files to be hashed. It uses the
    filename as a key. It requires the files to be in .mtx format. The
    hashes starts from 1 ... number_of_files
    """

    diseaseHashes={}

    files = IO.getSortedFilelist(dir)
    counter=0
    for f in files:
        diseaseName=f[0:f.find('.mtx')]
        stdm=IO.readInTDM(dir+'/'+f)
        if stdm.shape[0]==1:
            continue
        if diseaseName not in diseaseHashes.keys():
            counter+=1
            if output:
                print 'Created', diseaseName, 'with hash', counter
            diseaseHashes[diseaseName]=counter

    IO.pickleOut(_hashTablesDir, diseaseHash,"btd", diseaseHashes)
