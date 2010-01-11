from __future__ import division
import DistanceMeasure
reload(DistanceMeasure)
from DistanceMeasure import sim_pearson as pearson, cosine_measure as cosine, cosine_measure_dense as cosine_dense
from math import sqrt, pow, fabs, floor
import random
from PIL import Image, ImageDraw
import time
import cPickle
import SearchTermDoc as STD
from scipy import sparse
from numpy import delete
import os
import IOmodule as IO

# Main folder
_mainFolder=os.getenv("HOME")+"/"+"The_Hive"
# Phase subfolder
_subFolder = _mainFolder+"/"+"term_doc"
# Term-doc directory
_termDocDir=_subFolder+"/"+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_subFolder+"/"+"hashTables"

_stemmed=False

if not _stemmed:
    _outlierRemoved='new_diseaseMatrices_outlierRemoved'

else:
    _outlierRemoved='new_diseaseMatrices_outlierRemoved_stemmed'

outlierRemoved=_outlierRemoved


def runOutlierDetector(dir, distance=cosine_dense, removePercent=0.05, output=False, time_log=False):

    files = IO.getSortedFilelist(dir+'/')

    if output:
        counter = 0

    for f in files:
        diseaseName = f[0:f.find('.mtx')]
        subTermDoc = IO.readInTDM(dir, diseaseName)
        if output:
            counter += 1
            print 'Count:', counter

        # If sub term document matrix is empty, just skip it.
        if subTermDoc.shape[0]==1 or subTermDoc.shape[1]==1:
            continue

        if time_log:
            t1 = time.time()
        subTermDoc = outlierDetector(subTermDoc, distance, removePercent, output, time_log)
        if time_log:
            print 'Time for outlier detection on', diseaseName, ':', str(time.time() -t1)[:4]

        if output:
            print 'Writing',

        subTermDoc = sparse.coo_matrix(subTermDoc)

        IO.writeOutTDM(_subFolder+'/'+outlierRemoved+str(int(removePercent*100)), diseaseName, subTermDoc)

def outlierDetector(stdm, distance=cosine_dense, removePercent=0.05, output=False, time_log=False):

    """
    Recieves a coo matrix and calculates cosine similarity between all
    rows.

    distance=pearson will not work as it is not yet able to work on
    dense matrices
    """
    
    n = stdm.shape[0] - 1
    stdmdense = stdm.todense()
    stdmdense = stdmdense[1:,1:]

    distance_matrix = sparse.lil_matrix((n,n))

    if time_log:
        t1 = time.time()

    for i in range(0,n):
        for j in range(0,n):
            # As it is symmetric only calculate what is needed.
            if distance_matrix[i,j] == 0:
#                distance_matrix[i,j] = distance_matrix[j,i] = distance(stdm_csr.getrow(i), stdm_csr.getrow(j))
                distance_matrix[i,j] = distance_matrix[j,i] = distance(stdmdense[i,:], stdmdense[j,:])

    if time_log:
        print '\tTime for distance calculations', str(time.time() - t1)

    # We need to do the outlier detection down here, but we need some
    # clever way of doing it. Perhaps getting the average correlation
    # for each vector with the others, and then using a threshold to
    # remove those below.

    stdm = stdm.todense()

    distance_matrix = distance_matrix.todense()

    numberToRemove = int(floor(removePercent * n))

    if output:
        print '\tNumber of rows to remove', numberToRemove, 'out of', n

    if time_log:
        t2 = time.time()
    toBeDeleted=[]
    listOfThings=[]
    for i in range(0,n):
        listOfThings.append(((distance_matrix[i,:].sum() / n), i))

    listOfThings.sort()

    # As we have worked on a matrix missing first row and first
    # column, we need to add one to the row index to convert it back
    # to the original matrix.
    toBeDeleted = [int(item[1])+1 for item in listOfThings[:numberToRemove]]

    if output:
        print '\tList of row indices to be removed as outliers:', toBeDeleted

        
    stdm = delete(stdm, toBeDeleted, 0)

    if time_log:
        print '\tTime for finding and deleting outliers:', str(time.time() - t2)[:4]

    stdm = sparse.lil_matrix(stdm)
            
    return stdm
