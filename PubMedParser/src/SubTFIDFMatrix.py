import IOmodule
import math
import time
import os
import SearchTermDoc

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Matrices folder
_matrixDir=_subfolder+"/"+"diseaseMatrices_stemmed"
# Term-doc directory
_termDocDir = _subFolder+"/"+"diseaseMatrices_tfidf_stemmed"


def _generateLogTFIDF(M_coo,termSum):

    """
    Creates a Term-Frequency Inverse-Document-Frequency from a sparse coo_matrix,
    using log-transformation on TF and IDF.

    Returns a sparse lil_matrix to be used for vector-normalization.
    """

    totalTime1=time.time()

    numberOfDocs = float(M_coo.shape[0]-1)

    print "Converting from coo to lil..."
    t1=time.time()
    tfidfMatrix=M_coo.tolil()
    t2=time.time()
    print "Matrix converted to lil in",(t2-t1)


    t1=time.time()

    for row in range(1,numberOfDocs+1):

        for col in (tfidfMatrix.getrow(row).nonzero()[1])[1:]:

            tf=tfidfMatrix[row,col]

            if tf == 0:
                print "Looked up zero-value at: "+str(docIndex)+" "+str(termVectorIndex)
                raise Exception
            tf = math.log(1 + tf)

            idf = math.log(numberOfDocs / termSum[col])

            tfidfMatrix[row,col]=tf*idf

        print "Row:",row

    t2=time.time()
    print "Total:"+str(t2-t1)

    totalTime2=time.time()
    print "Total time: "+str(totalTime2-totalTime1)

    return tfidfMatrix


def _normalizeVectorLengths(M_lil,vectorLength,filename):

    """
    Normalize the length of a sparse lil_matrix.
    """

    t1=time.time()

    SearchTermDoc.createRLHash(M_lil, _RLHash)

    for row in range(1,M_lil.shape[0]):

        norm=vectorLength[row]
        for col in (M_lil.getrow(row).nonzero()[1])[1:]:
            M_lil[row,col]=(M_lil[row,col])/norm
        print "Normalized:",row
        
    t2=time.time()
    print "Total:"+str(t2-t1)

    # This is madness
    tfidfMatrix = M_lil

    # Save and overwrite the log_tfidf generated above
    IOmodule.writeOutTDM(_termDocDir,filename+"_tfidf", tfidfMatrix)


def runTFIDF():

    """
    Create a normalized log-transformed TFIDF-matrix from a sparse coo_matrix.
    """

    files = sorted([f for f in os.listdir(_matrixDir+"/") if os.path.isfile(_matrixDir+"/" + f)])

    for file in files:

        subM_coo=IOmodule.readInTDM(_matrixDir,file)

        vectorLength=SearchTermDoc.createRLHash(M_lil, None, False)
        termSum=SearchTermDoc.createCLHash(M_coo, None, False)

        print "Generating log_TFIDF..."
        subTFIDFMatrix=_generateLogTFIDF(subM_coo,termSum)
        print "Normalizing vector lengths..."
        _normalizeVectorLengths(subTFIDFMatrix,vectorLength,file)
        print "Done."