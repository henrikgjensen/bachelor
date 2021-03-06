from scipy import linalg, mat, sparse
import IOmodule
import FilterInterface
import os
import SearchTermDoc

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Hash tables
_hashTablesDir=_path+'/'+'term_doc'+'/'+"hashTables"

#################

# Matrices folder (read in)
#_oldMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf"
# Matrices folder (write out)
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_reduced_10"
#_reduceBy=10
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_reduced_50"
#_reduceBy=50
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_reduced_90"
#_reduceBy=90

################

# Matrices folder (read in)
_oldMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed"
# Matrices folder (write out)
_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed_reduced_10"
_reduceBy=10
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed_reduced_50"
#_reduceBy=50
#_newMatrixDir=_subFolder+"/"+"new_diseaseMatrices_tfidf_stemmed_reduced_90"
#_reduceBy=90

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

    print "Dimensions reduced: "+str(n)
    U=U[:,:-n]
    Sig=Sig[:-n,:-n]
    Vt=Vt[:-n,:]
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


termHashTable=IOmodule.pickleIn(_hashTablesDir, "termHash_stemmed")
revTermHashTable=dict(zip(termHashTable.values(),termHashTable.keys()))
def getSemanticKeywords(top=20):

    diseaseList=[("Fibrodysplasia ossificans progressiva","Boy, normal birth, deformity of both big toes (missing joint), quick development of bone tumor near spine and osteogenesis at biopsy"),
                ("Adrenoleukodystrophy  autosomal  neonatal form","Normally developed boy age 5, progessive development of talking difficulties, seizures, ataxia, adrenal insufficiency and degeneration of visual and auditory functions"),
                ("Papillon Lefevre syndrome","Boy age 14, yellow keratotic plaques on the skin of palms and soles going up onto the dorsal side. Both hands and feet are affected. swollen vulnerable gums, loss of permanent teeth"),
                ("Kleine Levin Syndrome","Jewish boy age 16, monthly seizures, sleep aggressive and irritable when woken, highly increased sexual appetite and hunger"),
                ("Schinzel Giedion syndrome","Male child, malformations at birth, midfacial retraction with a deep groove under the eyes, and hypertelorism, short nose with a low nasal bridge and large low-set ears, wide mouth and retrognathia. Hypertrichosis with bright reddish hair and a median frontal cutaneous angioma, short neck with redundant skin, Bilateral inguinal hernias, hypospadias with a megameatus, and cryptorchidism")]

    matrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_stemmed_reduced_90"
    #matrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_stemmed_reduced_10"
    #matrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_tfidf_stemmed_reduced90_outlierRemoved5"

    scoreDic={}
    totalTermDic={}
    for disease in diseaseList:

        filename=disease[0]
        symptoms=disease[1]

        symptoms=SearchTermDoc._modifySearchString(symptoms)
        symptoms=map(FilterInterface.porterStemmer,symptoms)

        M_coo=IOmodule.readInTDM(matrixDir,filename)
        totalTermDic[filename]=(M_coo.shape[1]-1)

        M_csc=M_coo.tocsc()
    
        termSum=[]
        for col in range(1,M_coo.shape[1]):
            term=revTermHashTable[M_csc[0,col]]
            termSum.append((sum(M_csc.getcol(col).data[:-1]),term))

        termSum.sort()
        termSum.reverse()

        scoreDic[filename]={}
        for item in termSum:
            if item[1] in symptoms:
                scoreDic[filename][item[1]]=termSum.index(item)

    #return termSum[:top]

    for score in scoreDic.items():
        print "Total number of terms for the disease:",totalTermDic[score[0]]
        print str(score[0])+'\t'+str(score[1].items())
        print ''
    