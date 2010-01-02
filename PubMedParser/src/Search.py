import SearchInterface
import SearchTermDoc
import FilterInterface
import IOmodule
import os
import TextCleaner

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Hashtable directory
_hashTablePath = _subFolder+"/"+"hashTables"
# Set True for Porter-stemming
_stemmer=True

############

# Disease label hash (for pmid lookup)
#_labelHash = IOmodule.pickleIn(_hashTablePath,"labelHash")
#print "Label hash loaded"

############

# Disease label hash (for label lookup)
_labelHash = IOmodule.pickleIn(_hashTablePath,"diseaseHash")
_labelHash=dict(zip(_labelHash.values(),_labelHash.keys()))
print "Label hash loaded"

############


def search20(M_lil, M_csc, queryString, AND=False):

    """
    This function is still a work in progress..
    """

    # OPTIONAL:
    # Stem the information
    if _stemmer: queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasureOR(M_lil, M_csc, queryString)

    if AND: results=SearchInterface.cosineMeasureAND(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    results.sort()
    results.reverse()

    top20=[result[1] for result in results[:20]]

    # Retrieve the top 20 results as PMIDs
    pmidList=SearchTermDoc.getPMIDList(top20)

    pmidList=' '.join(pmid for pmid in pmidList)

    return pmidList


def search(M_lil, M_csc, queryString, top=20, AND=False):

    """
    This function is still a work in progress..
    """

    # OPTIONAL:
    # Stem the information
    if _stemmer:
        # Get the regex pattern that sanitizeses information and sanitize it
        sanitizer = TextCleaner.sanitizeString()
        queryString=sanitizer.sub(' ', queryString)
        # Stem the information
        queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasureOR(M_lil, M_csc, queryString)

    if AND: results=SearchInterface.cosineMeasureAND(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    results.sort()
    results.reverse()

#    resultDic={}
#    for item in results[:top]:
#        pmid=item[1] #SearchTermDoc.getPMID(item[1])
#        labels=_labelHash[pmid]
#        for label in labels:
#            try:
#                resultDic[label]+=item[0]
#            except:
#                resultDic[label]=item[0]

    resultDic={}
    for item in results[:top]:
        pmid=item[1] #SearchTermDoc.getPMID(item[1])
        label=_labelHash[pmid]
        resultDic[label]=item[0]
    
    resultList=sorted(resultDic.items(), key=lambda(k,v):(v,k), reverse=True)

    return resultList

def getScore(resultList,diseaseName):

    Found=False

    for result in resultList:
        if result[0]==diseaseName:
            print "<<<<<<<",diseaseName,">>>>>>>"
            print "Scored",resultList.index(result),"out of",len(resultList)
            print "Cosine score:",result[1]
            Found=True

    if not Found: print "Did not locate the disease"
        

def runScoreTest1(M_lil, M_csc, queryString, diseaseName):

    topList=[None,3000,2000,1000,500,100,50]

    for top in topList:

        results=search(M_lil, M_csc, queryString, top, AND=False)

        getScore(results,diseaseName)

    print "TEST DONE"


def runScoreTest2(M_lil, M_csc):

    top=3000

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


    printout1=''
    printout2=''

    for disease in diseaseList:

        printout1+=str(disease[0])[0:5]+","

        symptoms=FilterInterface.stopwordRemover(disease[1])

        results=search(M_lil, M_csc, symptoms, top, AND=False)

        for result in results:
            if result[0]==disease[0]:
                printout2+=str(results.index(result))+","

    print printout1
    print printout2
    print "TEST DONE"


def runScoreTest3(M_lil, M_csc):

    top=3000

    diseaseList=[('Apparent mineralocorticoid excess','early-onset, severe hypertension, associated, low renin levels, hypoaldosteronism'),
                ('Rubinstein-Taybi syndrome','congenital anomalies, intellectual deficit, behavioural characteristics'),
                ('Aagenaes syndrome','chronic severe lymphoedema, severe neonatal cholestasis, lessens during early childhood and becomes episodic'),
                ('Aase Smith syndrome','congenital malformations: hydrocephalus, cleft palate, severe joint contractures'),
                ('Achondroplasia','short limbs, hyperlordosis, short hands, macrocephaly, high forehead and saddle nose'),
                ('Acalvaria','missing scalp and flat bones over an area of the cranial vault'),
                ('Acrodysostosis','abnormally short and malformed bones of the hands and feet (peripheral dysostosis), nasal hypoplasia and mental retardation'),
                ('Acromegaly','progressive somatic disfigurement (face and extremities) and systemic manifestations'),
                ('Biliary atresia','biliary obstruction of unknown origin, neonatal period'),
                ('Bronchiolitis obliterans with obstructive pulmonary disease','inflammatory and fibrosing thickening of bronchiolar walls, airflow obstruction'),
                ('Cholera','severe diarrhea and vomiting'),
                ('Choroideremia','progressive degeneration of the choroid, retinal pigment epithelium (RPE), and neural retina'),
                ('Coats disease','abnormal development of retinal vessels (telangiectasia) with a progressive deposition of intraretinal or subretinal exudates'),
                ('Omphalocele cleft palate syndrome lethal','omphalocele and cleft palate'),
                ('Darier disease','keratotic papules in seborrheic areas and specific nail anomalies'),
                ('Ichthyosis hepatosplenomegaly cerebellar degeneration','ichthyosis, hepatosplenomegaly and late-onset cerebellar ataxia'),
                ('Emery-Dreifuss muscular dystrophy','muscular weakness and atrophy, with early contractures of the tendons and cardiomyopathy'),
                ('Costello syndrome','postnatal growth retardation, coarse facies, intellectual deficit, skin anomalies and cardiac abnormalities'),
                ('Fibrodysplasia ossificans progressiva','congenital malformation of great toes, progressive, disabling heterotopic osteogenesis in predictable anatomical patterns'),
                ('Deafness skeletal dysplasia lip granuloma','deafness, intellectual deficit , facial dysmorphy, and skeletal abnormalities'),
                ('Acropectorovertebral dysplasia','fusion of the carpal and tarsal bones, with complex anomalies of the fingers and toes'),
                ('Osteogenesis imperfecta','increased bone fragility and low bone mass'),
                ('Primary biliary cirrhosis','injury of the intrahepatic bile ducts'),
                ('Hennekam syndrome','lymphoedema, intestinal lymphangiectasia, intellectual deficit and facial dysmorphism'),
                ('Hyperlysinemia','elevated levels of lysine in the cerebrospinal fluid and blood'),
                ('Jackson-Weiss syndrome','tarsal and/or metatarsal coalitions and variable craniosynostosis, accompanied by facial anomalies, broad halluces and normal hands'),
                ('Jalili syndrome','amelogenesis imperfecta and cone-rod retinal dystrophy'),
                ('Jeune syndrome','narrow thorax and short limbs'),
                ('Jackson-Weiss syndrome','tarsal and/or metatarsal coalitions and variable craniosynostosis, accompanied by facial anomalies, broad halluces and normal hands'),
                ('Multiple myeloma','overproduction of abnormal plasma cells in the bone marrow and manifested by skeletal destruction, bone pain, and presence of abnormous immunoglobulins'),
                ('Trichodental syndrome','fine, dry and short hair with dental anomalies')]

    printout1=''
    printout2=''

    for disease in diseaseList:

        printout1+=str(disease[0])[0:5]+","

        symptoms=FilterInterface.stopwordRemover(disease[1])

        results=search(M_lil, M_csc, symptoms, top, AND=False)

        for result in results:
            if result[0]==disease[0]:
                printout2+=str(results.index(result))+","

    print printout1
    print printout2
    print "TEST DONE"

