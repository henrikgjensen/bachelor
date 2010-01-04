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

    diseaseList=[("Infective endocarditis","Acute, aortic,  regurgitation, depression,  abscess "),
                ("Cushing's syndrome","hypertension, adrenal, mass"),
                ("Eosinophilic granuloma", "Hip, lesion, older, child"),
                ("Ehrlichiosis","fever, bilateral, thigh, pain, weakness"),
                ("Neurofibromatosis type 1","multiple, spinal, tumours, skin, tumours"),
                ("Pheochromocytoma","hypertension, papilledema, headache, renal, mass, cafe, au, lait"),
                ("Creutzfeldt-Jakob disease","ataxia, confusion, insomnia, death"),
                ("Churg-Strauss syndrome","Wheeze, weight, loss, ANCA, haemoptysis, haematuria"),
                ("Dermatomyositis","myopathy, neoplasia, dysphagia, rash, periorbital, swelling"),
                ("Cat Scratch Disease","renal, transplant, fever, cat, lymphadenopathy"),
                ("TEN","bullous, skin, conditions, respiratory, failure, carbamazepine"),
                ("MELAS","seizure, confusion, dysphasia, T2, lesions"),
                ("Brugada syndrome","cardiac arrest sleep")]

    #matrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_tfidf_stemmed_reduced_90"
    matrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_tfidf_stemmed_reduced_10"
    #matrixDir="/root/The_Hive/term_doc/new_diseaseMatrices_tfidf_stemmed_reduced90_outlierRemoved5"

    scoreDic={}
    for disease in diseaseList:

        filename=disease[0]
        symptoms=disease[1]

        symptoms=SearchTermDoc._modifySearchString(symptoms)
        symptoms=map(FilterInterface.porterStemmer,symptoms)

        M_coo=IOmodule.readInTDM(matrixDir,filename)

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
    return scoreDic
    