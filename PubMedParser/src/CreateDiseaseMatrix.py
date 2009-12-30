import IOmodule as IO
import os
from scipy import sparse
from numpy import mat
import time

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

# names
# pmid hash
_pmidHash="pmidHash"
# disease hash
diseaseHash='diseaseHash'
# labelMatrix
label = 'LabelMatrix'

def getRowIndices(file_content, pmidHashTable, output=False, time_log=False):

    # Read through medline articles and get PMID to extract from
    # complete term doc.

    pmids=[]
    for i in range(len(file_content['records'])):
        pmids.append(file_content['records'][i]['PMID'])

    pmids=[pmidHashTable[pmid] for pmid in pmids]

    print 'PMIDs:', pmids

    return pmids

def createLabelVector(tdm, PMIDHashes, output=False, time_log=False):

    # Sum over all columns and return a 1 x 456xxx vector

    n = tdm.shape[1] - 1

    labelVector = sparse.csr_matrix((1,n))
    labelVector = labelVector.todense()

    for pH in PMIDHashes:
        row = tdm.getrow(pH)
        row = row.todense()[0,1:]

        labelVector += row

    return sparse.csr_matrix(labelVector)

def constructLabelMatrix(tdm, output=False, time_log=False):

    if output:
        'Converting matrix to csr'

    if time_log:
        t1 = time.time()

    tdm = tdm.tocsr()

    if time_log:
        print 'Time for matrix convertion', str(time.time() - t1)[:4]

    files = IO.getSortedFilelist(_medlineDir+'/',stopIndex=1)

    n = tdm.shape[1]

    if output:
        print 'Creating a ', str(len(files)+1)+'x'+str(n), 'label matrix'
    
    labelMatrix = sparse.lil_matrix((len(files)+1,n))

    diseaseHashTable = IO.pickleIn(_hashTablesDir, diseaseHash+'.hash')

    pmidHashTable=IO.pickleIn(_hashTablesDir, _pmidHash+'.btd')

    if output:
        counter = 0

    for f in files:
        if time_log:
            t2 = time.time()
        diseaseName=f[0:f.find('.txt')]
        if output:
            counter+=1
            print 'Processing', diseaseName, len(files)-counter, 'Numbers remaining',
            
        file_content = IO.evalIn(_medlineDir+'/'+f)
        
        pmidHashes=getRowIndices(file_content, pmidHashTable)

        labelVector = createLabelVector(tdm, pmidHashes)

        diseaseH = diseaseHashTable[diseaseName]

        labelMatrix[diseaseH,0] = diseaseH

        labelMatrix[diseaseH,1:] = labelVector

        if time_log:
            print 'Process time:', str(time.time() - t2)[:4],

        print 

    labelMatrix[0,:] = tdm.getrow(0)

    if output:
        print 'Done making label matrix, writing to', _termDocDir+'/'+label,'...'

    IO.writeOutTDM(_termDocDir, label, labelMatrix)

    if output:
        print 'Done wrting label matrix.'

def createDiseaseHash(dir):

    diseaseHashes={}

    files = IO.getSortedFilelist(dir)
    counter=0
    for f in files:
        diseaseName=f[0:f.find('.txt')]
        if diseaseName not in diseaseHashes.keys():
            counter+=1
            print 'Created', diseaseName, 'with hash', counter
            diseaseHashes[diseaseName]=counter

    IO.pickleOut(_hashTablesDir, diseaseHash, 'hash', diseaseHashes)
