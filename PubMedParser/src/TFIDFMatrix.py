import IOmodule
import math
import time
import os
import SearchTermDoc

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Hashtable directory
_hashTablePath = _subFolder+"/"+"hashTables"
# Term-doc directory
_termDocDir = _subFolder+"/"+"termDoc"


####################################################################
#### Use stopword-removed TermDoc ##################################
####################################################################

 # TFIDF-matrix file name
#_tfidfName = "TFIDFMatrix"
 # Vector-norm hash for then TFIDFMatrix
#_RLHash = "RLHash"
 # Hash for the number of documents each term occur in
#_CLHash = "CLHash"
 # Load the precomputed norm of each row-vector in the term-doc matrix.
#_vectorLength = IOmodule.pickleIn(_hashTablePath,_RLHash)
 # Load the precomputed length of each column in the term-doc matrix
#_termSum = IOmodule.pickleIn(_hashTablePath,_CLHash)
 

####################################################################
#### Use stopword-removed and Porter-stemmed (english) TermDoc: ####
####################################################################

 # TFIDF-matrix file name
#_tfidfName = "TFIDFMatrix_stemmed"
 # Vector-norm hash for then TFIDFMatrix
#_RLHash = "RLHash_stemmed"
 # Hash for the number of documents each term occur in
#_CLHash = "CLHash_stemmed"
 # Load the precomputed norm of each row-vector in the stemmed term-doc matrix.
#_vectorLength = IOmodule.pickleIn(_hashTablePath,_RLHash)
 # Load the precomputed length of each column in the stemmed term-doc matrix
#_termSum = IOmodule.pickleIn(_hashTablePath,_CLHash)


#######################################################################################
#### Use stopword-removed, Porter-stemmed (english) and TFIDF-prefiltered TermDoc: ####
#######################################################################################

 # TFIDF-matrix file name
_tfidfName = "nolog_TFIDFMatrix_tfidf_stemmed"
 # Vector-norm hash for then TFIDFMatrix
_RLHash = "RLHash_tfidf_stemmed"
 # Hash for the number of documents each term occur in
_CLHash = "CLHash_tfidf_stemmed"
 # Load the precomputed norm of each row-vector in the stemmed term-doc matrix.
_vectorLength = IOmodule.pickleIn(_hashTablePath,_RLHash)
 # Load the precomputed length of each column in the stemmed term-doc matrix
_termSum = IOmodule.pickleIn(_hashTablePath,_CLHash)

####################################################################

print "Hashes loaded."


def _generateLogTFIDF(M_coo):

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
            #tf = math.log(1 + tf)
            
            idf = math.log(numberOfDocs / _termSum[col])
            
            tfidfMatrix[row,col]=tf*idf
        
        print "Row:",row
        
    t2=time.time()
    print "Total:"+str(t2-t1)

    # Save and overwrite the log_tfidf generate above
    IOmodule.writeOutTDM(_termDocDir, _tfidfName, tfidfMatrix)

    totalTime2=time.time()
    print "Total time: "+str(totalTime2-totalTime1)

    return tfidfMatrix

def _normalizeVectorLengths(M_lil):

    """
    Normalize the length of a sparse lil_matrix.
    """

    t1=time.time()

    SearchTermDoc.createRLHash(M_lil, _RLHash)

    for row in range(1,M_lil.shape[0]):

        norm=_vectorLength[row]
        for col in (M_lil.getrow(row).nonzero()[1])[1:]:
            M_lil[row,col]=(M_lil[row,col])/norm
        print "Normalized:",row
    t2=time.time()
    print "Total:"+str(t2-t1)

    # This is madness
    tfidfMatrix = M_lil

    # Save and overwrite the log_tfidf generated above
    IOmodule.writeOutTDM(_termDocDir, _tfidfName+'_norm', tfidfMatrix)

def runTFIDF(M_coo):

    """
    Create a normalized log-transformed TFIDF-matrix from a sparse coo_matrix.
    """

    print "Generating log_TFIDF..."
    TFIDFMatrix=_generateLogTFIDF(M_coo)
    print "Normalizing vector lengths..."
    _normalizeVectorLengths(TFIDFMatrix)
    print "Done."
