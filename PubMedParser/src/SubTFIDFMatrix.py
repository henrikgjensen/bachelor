import IOmodule
import math
import time
import os
import SearchTermDoc
from scipy import sparse

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Matrices folder
_matrixDir=_subFolder+"/"+"new_diseaseMatrices"
# Term-doc directory
_termDocDir = _subFolder+"/"+"new_diseaseMatrices_tfidf"


def _generateLogTFIDF(M_coo):

    """
    Creates a Term-Frequency Inverse-Document-Frequency from a sparse coo_matrix,
    using log-transformation on TF and IDF.

    Returns a sparse lil_matrix to be used for vector-normalization.
    """

    termSum=SearchTermDoc.createCLHash(M_coo, None, False)

    numberOfDocs = float(M_coo.shape[0]-1)

    tfidfMatrix=M_coo.tolil()

    # Use a dense matrix for constant time lookups
    tempDenseMatrix=M_coo.todense()

    for row in range(1,numberOfDocs+1):

        for col in (tfidfMatrix.getrow(row).nonzero()[1])[1:]:

            tf=tempDenseMatrix[row,col]
            #tf=tfidfMatrix[row,col]

            if tf == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception
            tf = math.log(1 + tf)

            idf = math.log(numberOfDocs / termSum[col])

            #tfidfMatrix[row,col]=tf*idf
            tempDenseMatrix[row,col]=tf*idf

    return tempDenseMatrix,tfidfMatrix
    #return tfidfMatrix


def _normalizeVectorLengths(M_dense,M_lil,filename):

    """
    Normalize the length of a sparse lil_matrix.
    """

    vectorLength=SearchTermDoc.createRLHash(M_lil, None, False)

    for row in range(1,M_lil.shape[0]):

        norm=vectorLength[row]
        for col in (M_lil.getrow(row).nonzero()[1])[1:]:
            #M_lil[row,col]=(M_lil[row,col])/norm
            M_dense[row,col]=(M_dense[row,col])/norm

    tfidfMatrix = sparse.coo_matrix(M_dense)

    # Save and overwrite the log_tfidf generated above
    IOmodule.writeOutTDM(_termDocDir,filename, tfidfMatrix)


def runTFIDF():

    """
    Create a normalized log-transformed TFIDF-matrix from a sparse coo_matrix.
    """

    files = sorted([f for f in os.listdir(_matrixDir+"/") if os.path.isfile(_matrixDir+"/" + f)])

    for file in files:

        file=file[:-4]

        subM_coo=IOmodule.readInTDM(_matrixDir,file)

        t1=time.time()
        #subTFIDFMatrix=_generateLogTFIDF(subM_coo)
        dense,lil=_generateLogTFIDF(subM_coo)
        t2=time.time()
        print "Generated log_TFIDF in "+str(t2-t1)

        t1=time.time()
        #_normalizeVectorLengths(subTFIDFMatrix,file)
        _normalizeVectorLengths(dense,lil,file)
        t2=time.time()
        print "Normalized vector lengths in "+str(t2-t1)

        print "Done with: "+file+"\n"