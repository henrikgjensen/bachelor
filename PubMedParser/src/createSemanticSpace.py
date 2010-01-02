from scipy import linalg, mat, sparse
import IOmodule
import os

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"

#################

# Matrices folder (read in)
#_oldMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf"
# Matrices folder (write out)
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_reduced_5"
#_reduceBy=5
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_reduced_50"
#_reduceBy=50
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_reduced_90"
#_reduceBy=90

################

# Matrices folder (read in)
_oldMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed"
# Matrices folder (write out)
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed_reduced_5"
#_reduceBy=5
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed_reduced_50"
#_reduceBy=50
_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed_reduced_90"
_reduceBy=90

################

def _svd(M_dense):

    """
    Singular Value Decomposition.

    Takes a sparse coo-matrix.

    Returns left, right and singular values.
    """

    # Cut away the indices (row 0 and col 0)
    M_dense = M_dense[1:,1:]

    # Calculate singular values
    U, S, Vt = linalg.svd(M_dense)

    # Get the dimensions of the matrix
    M, N = M_dense.shape

    # Return the SVD matrices
    Sig = mat(linalg.diagsvd(S, M, N))
    U, Vt = mat(U), mat(Vt)
    return U,Sig,Vt


def _semanticSpace(U,Sig,Vt,reduce=90):

    """
    Create and return a reduced semantic space
    from U, Sig and Vt given in svd above.

    *Note that since its faster to multiply csc-
    matrices (compared to dense-matrices), csc
    and dense is used interchangeably for
    improved speed.
    """

    Sig_csc=sparse.csc_matrix(Sig)
    eigSum = Sig_csc.sum()
    diagLen = Sig_csc.getnnz()

    print "eigsum:"+str(eigSum)
    print "diaglen:"+str(diagLen)

    percentReduce=(float(eigSum)/100)*reduce

    counter=0
    n=0
    for i in range(1,diagLen+1):

        # Since the most interesting singular values are organised top-down
        # along the diagonal, we work our way bottom-up when reducing noisy
        # dimensions.
        bottomUp=diagLen-i

        counter+=Sig[bottomUp,bottomUp]

        if counter >= percentReduce:
            n=i
            break

    # Make sure there are at least 3 dimensions in the reduced matrix
    if n>diagLen-3:
        n=diagLen-3
    # If there are 3 or less dimensions, do not reduce dimensionality
    if diagLen<=3:
        n=(-diagLen)

#    print "Dimensions reduced: "+str(n)
#    U=U[:,:-n]
#    Sig=Sig[:-n,:-n]
#    Vt=Vt[:-n,:]
    U=U[:,1]
    Sig=Sig[1,1]
    Vt=Vt[1,:]
    print "U",U.shape,", Sig",Sig.shape,", Vt",Vt.shape

    U=sparse.csc_matrix(U)
    Sig=sparse.csc_matrix(Sig)
    Vt=sparse.csc_matrix(Vt)

    S=U*Sig*Vt

    print "Number of elements: "+str(len(S.data))

    return S


def runAndSaveMatrices():

    """
    Transform a directory of matrices to a directory of decomposed matrices.
    """

    files = IOmodule.getSortedFilelist(_oldMatrixDir+'/')

#    files = sorted([f for f in os.listdir(_oldMatrixDir+"/") if os.path.isfile(_oldMatrixDir+"/" + f)])

    for file in files:

        M_coo=IOmodule.readInTDM(_oldMatrixDir,file)

        # Make sure the matrix contains information (1-dim. is an empty matrix)
        if M_coo.shape[0]==1:
            continue

        print "Shape:"+str(M_coo.shape)

        # SVD does not run well single dimenstion matrices
        ## (remembering that the first dimension is indices and does not count)
        if M_coo.shape[0]>2:
            M_dense=M_coo.todense()

            # Run SVD
            U,Sig,Vt=_svd(M_dense)

            # Get the reduced semantic space
            S= _semanticSpace(U,Sig,Vt,_reduceBy)

            # Recombine the indices and the reduced matrix
            M_dense[1:,1:]=S.todense()

            # Save the matrix
            M_coo=sparse.coo_matrix(M_dense)

            IOmodule.writeOutTDM(_newMatrixDir, file, M_coo)
            print ''
        else:
            print "Dimensionality too low for svd"
            IOmodule.writeOutTDM(_newMatrixDir, file, M_coo)
            print ''

