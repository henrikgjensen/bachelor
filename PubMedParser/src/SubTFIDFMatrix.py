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
_matrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed"
# Term-doc directory
_termDocDir = _subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed"


def _generateLogTFIDF(M_coo):

    """
    Creates a Term-Frequency Inverse-Document-Frequency from a sparse coo_matrix,
    using log-transformation on TF and IDF.

    Returns a sparse dense- and lil-matrix to be used for vector-normalization.
    """

    termSum=SearchTermDoc.createCLHash(M_coo, None, False)

    numberOfDocs = float(M_coo.shape[0]-1)

    # Use a lil-matrix for nonzero row lookups
    M_lil=M_coo.tolil()
    # Use a dense-matrix for constant-time lookups
    M_dense=M_coo.todense()

    for row in range(1,numberOfDocs+1):

        for col in (M_lil.getrow(row).nonzero()[1])[1:]:

            # Term frequency
            tf=M_dense[row,col]

            if tf == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception
            # Log-transformation of the term frequency
            tf = math.log(1 + tf)

            # Inverse-document frequency
            idf = math.log(numberOfDocs / termSum[col])

            M_dense[row,col]=tf*idf

    return M_dense,M_lil


def _normalizeVectorLengths(M_dense,M_lil,filename):

    """
    Normalize the length of a sparse matrix, represented as a dense and a lil -
    format.
    """

    vectorLength=SearchTermDoc.createRLHash(M_lil, None, False)

    for row in range(1,M_lil.shape[0]):

        norm=vectorLength[row]
        for col in (M_lil.getrow(row).nonzero()[1])[1:]:
            M_dense[row,col]=(M_dense[row,col])/norm

    tfidfMatrix = sparse.coo_matrix(M_dense)

    # Save the matrix
    IOmodule.writeOutTDM(_termDocDir,filename, tfidfMatrix)


def runTFIDF():

    """
    Create a normalized log-transformed TFIDF-matrix from a sparse coo_matrix.
    """

    files = IOmodule.getSortedFilelist(_matrixDir+'/')

#    files = sorted([f for f in os.listdir(_matrixDir+"/") if os.path.isfile(_matrixDir+"/" + f)])

    for file in files:

        file=file[:-4]

        subM_coo=IOmodule.readInTDM(_matrixDir,file)

        t1=time.time()
        dense,lil=_generateLogTFIDF(subM_coo)
        t2=time.time()
        print "Generated log_TFIDF in "+str(t2-t1)

        t1=time.time()
        _normalizeVectorLengths(dense,lil,file)
        t2=time.time()
        print "Normalized vector lengths in "+str(t2-t1)

        print "Done with: "+file+"\n"
