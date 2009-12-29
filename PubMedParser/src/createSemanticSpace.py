from scipy import linalg, mat, sparse, array
import IOmodule
import os

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Matrices folder (read in)
_oldMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed"
# Matrices folder (write out)
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed_reduced_5"
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed_reduced_50"
_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_stemmed_reduced_95"

def _svd(M_dense):

    """
    Singular Value Decomposition.

    Takes a sparse coo-matrix.

    Returns left, right and singular values.
    """

    X=M_dense

    X = X[1:,1:]

    U, S, Vt = linalg.svd(X)

    M, N = X.shape

    Sig = mat(linalg.diagsvd(S, M, N))
    U, Vt = mat(U), mat(Vt)

    return U,Sig,Vt


def _semanticSpace(U,Sig,Vt,reduce=90):

    """

    """

    Sig_csc=sparse.csc_matrix(Sig)
    eigSum = Sig_csc.sum()
    diagLen = Sig_csc.getnnz()

    percentReduce=(float(eigSum)/100)*reduce
    print "Reducing with "+str(percentReduce)+" percent"

    counter=0
    n=0
    for i in range(1,diagLen):

        bottomUp=diagLen-i

        counter+=Sig[bottomUp,bottomUp]

        if counter >= percentReduce:
            n=i
            break

    print "Dimensions reduced: "+str(n)
    U=U[:,:-n]
    Sig=Sig[:-n,:-n]
    Vt=Vt[:-n,:]

    U=sparse.csc_matrix(U)
    Sig=sparse.csc_matrix(Sig)
    Vt=sparse.csc_matrix(Vt)

    S=U*Sig*Vt

    return S


def runAndSaveMatrices():

    """
    
    """

    files = sorted([f for f in os.listdir(_oldMatrixDir+"/") if os.path.isfile(_oldMatrixDir+"/" + f)])


    for file in files:

        M_coo=IOmodule.readInTDM(_oldMatrixDir,file)

        X = M_coo.todense()


        U,Sig,Vt=_svd(X)


        S =  _semanticSpace(U,Sig,Vt)


        X[1:,1:]=S.todense()


        X=sparse.coo_matrix(X)


        IOmodule.writeOutTDM(_newMatrixDir, file, X)





"""
    #termHashTable=IOmodule.pickleIn("/root/The_Hive/term_doc/hashTables", "termHash_stemmed")
    #revTermHashTable=dict(zip(termHashTable.values(),termHashTable.keys()))
    #hashes=[]
    #termHashes=array(X[0,1:])
    #for termHash in termHashes[0]:
    #    hashes.append(revTermHashTable[termHash])


def topSemanticTerms(M_csc,hashes):

    # Make magic...

    l=[]

    for col in range(M_csc.shape[1]):
        l.append((sum(M_csc.getcol(col).data),hashes[col]))

    l.sort()
    l.reverse()

    return l

"""

