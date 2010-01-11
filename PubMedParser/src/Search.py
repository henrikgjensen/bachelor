import SearchInterface
import FilterInterface
import IOmodule
import os
import TextCleaner
import SearchTermDoc

# Main folder
_path = os.getenv("HOME")+"/"+"The_Hive"
# Sub folder
_subFolder = _path+"/"+"term_doc"
# Hashtable directory
_hashTablePath = _subFolder+"/"+"hashTables"
# Set True for Porter-stemming
_stemmer=True

############

#Disease label hash (for pmid lookup)
#_labelHash = IOmodule.pickleIn(_hashTablePath,"labelHash")
#print "Label hash loaded"

############

# Disease label hash (for label lookup)
_labelHash = IOmodule.pickleIn(_hashTablePath,"diseaseHash")
_labelHash=dict(zip(_labelHash.values(),_labelHash.keys()))
print _labelHash
print "Disease hash loaded"


############


def search(M_lil, M_csc, queryString, top=20):

    """
    This function is still a work in progress..
    """
    
    sanitizer = TextCleaner.sanitizeString()
    queryString=sanitizer.sub(' ', queryString)

    # OPTIONAL:
    # Stem the information
    if _stemmer:
        # Get the regex pattern that sanitizeses information and sanitize it
        # Stem the information
        queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results

    #    results=SearchInterface.cosineMeasure(M_lil, M_csc, queryString)
    results=SearchInterface.cosineMeasure(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    results.sort()
    results.reverse()

    # ###########################################################################
    # ### For the term-doc matrix: ##############################################

    # ###########
    # # 1: Mean #
    # ###########

    # # Get the sum cosine score the labels
    # ## (normDic counts the number of times a label has been summed)
#    resultDic1={}
#    normDic1={}
#    for item in results[:top]:
#        pmid=item[1]
#        # Get the labels linked to the PMID
#        ## (Several labels can be linked to one PMID)
#        labels=_labelHash[pmid]
#        for label in labels:
#            try:
#                resultDic1[label]+=item[0]
#                normDic1[label]+=1
#            except:
#                resultDic1[label]=item[0]
#                normDic1[label]=1
#
#    # #############
#    # # 2: Median #
#    # #############
#
#    # # Get the median cosine score of the labels
#    # ## (normDic counts the number of times a label has been summed)
#    resultDicList2={}
#    normDic2={}
#    for item in results[:top]:
#        pmid=item[1]
#        # Get the labels linked to the PMID
#        ## (Several labels can be linked to one PMID)
#        labels=_labelHash[pmid]
#        for label in labels:
#            try:
#                resultDicList2[label].append(item[0])
#                normDic2[label]+=1
#            except:
#                resultDicList2[label]=[]
#                resultDicList2[label].append(item[0])
#                normDic2[label]=1
#    resultDic2={}
#    for label in resultDicList2.keys():
#        labelList=resultDicList2[label]
#        numOfScores=len(labelList)
#        if numOfScores>2:
#            medianIndex=numOfScores/2
#        else:
#            medianIndex=0
#        resultDic2[label]=sorted(labelList)[medianIndex]
#
#    # ##########
#    # # 3: Max #
#    # ##########
#
#    # # Get the max cosine score of labels
#    # ## (normDic counts the number of times a label has been summed)
#    resultDicList3={}
#    normDic3={}
#    for item in results[:top]:
#        pmid=item[1]
#        # Get the labels linked to the PMID
#        ## (Several labels can be linked to one PMID)
#        labels=_labelHash[pmid]
#        for label in labels:
#            try:
#                resultDicList3[label].append(item[0])
#                normDic3[label]+=1
#            except:
#                resultDicList3[label]=[]
#                resultDicList3[label].append(item[0])
#                normDic3[label]=1
#    resultDic3={}
#    for label in resultDicList3.keys():
#        labelList=resultDicList3[label]
#        resultDic3[label]=max(labelList)


    # # Normalize the summed labels
    #for label in resultDic1.keys():
    #    resultDic1[label]/=normDic1[label]
    #for label in resultDic2.keys():
    #    resultDic2[label]/=normDic2[label]
    #for label in resultDic3.keys():
    #    resultDic3[label]/=normDic3[label]




    ###########################################################################
    ### For the label matrix: #################################################

    resultDic={}
    for item in results[:top]:
        pmid=item[1] #SearchTermDoc.getPMID(item[1])
        label=_labelHash[pmid]
        resultDic[label]=item[0]

    ###########################################################################

       ###################################
       ####### return pmid results #######

    # Reverse and sort the concensus list
    #resultList_mean=sorted(resultDic1.items(), key=lambda(k,v):(v,k), reverse=True)
    #resultList_median=sorted(resultDic2.items(), key=lambda(k,v):(v,k), reverse=True)
    #resultList_max=sorted(resultDic3.items(), key=lambda(k,v):(v,k), reverse=True)

    #return [resultList_mean,resultList_median,resultList_max]

    
    # Return label results ######

    resultLabelList = sorted(resultDic.items(), key=lambda(k,v):(v,k), reverse=True)

    return resultLabelList

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


    printout1=[]
    printout2=([],[],[])
    formatString = ['Mean:','Median:','Max:' ]

    clusterThis = ([],[],[])

    for disease in diseaseList:

        printout1.append(disease[0][0:5])

        symptoms=FilterInterface.stopwordRemover(disease[1])

        resultLists=search(M_lil, M_csc, symptoms, top)

        found=False
        count=0
        for results in resultLists:

            found=False
            for result in results:
                if result[0]==disease[0]:
                    printout2[count].append(results.index(result))
                    found=True
                    clusterThis[count].append(results[:50])
                    count+=1
            if not found:
                printout2[count].append(" ")
                count+=1

    print printout1
    cnt = 0
    for list in printout2:
        print formatString[cnt], list
        cnt+=1
    print "TEST DONE"

    return clusterThis

def runScoreTest3(M_lil, M_csc):

    top=3000

#    diseaseList=[('Apparent mineralocorticoid excess','early-onset, severe hypertension, associated, low renin levels, hypoaldosteronism'),
#                ('Rubinstein-Taybi syndrome','congenital anomalies, intellectual deficit, behavioural characteristics'),
#                ('Aagenaes syndrome','chronic severe lymphoedema, severe neonatal cholestasis, lessens during early childhood and becomes episodic'),
#                ('Aase Smith syndrome','congenital malformations: hydrocephalus, cleft palate, severe joint contractures'),
#                ('Achondroplasia','short limbs, hyperlordosis, short hands, macrocephaly, high forehead and saddle nose'),
#                ('Acalvaria','missing scalp and flat bones over an area of the cranial vault'),
#                ('Acrodysostosis','abnormally short and malformed bones of the hands and feet (peripheral dysostosis), nasal hypoplasia and mental retardation'),
#                ('Acromegaly','progressive somatic disfigurement (face and extremities) and systemic manifestations'),
#                ('Biliary atresia','biliary obstruction of unknown origin, neonatal period'),
#                ('Bronchiolitis obliterans with obstructive pulmonary disease','inflammatory and fibrosing thickening of bronchiolar walls, airflow obstruction'),
#                ('Cholera','severe diarrhea and vomiting'),
#                ('Choroideremia','progressive degeneration of the choroid, retinal pigment epithelium (RPE), and neural retina'),
#                ('Coats disease','abnormal development of retinal vessels (telangiectasia) with a progressive deposition of intraretinal or subretinal exudates'),
#                ('Omphalocele cleft palate syndrome lethal','omphalocele and cleft palate'),
#                ('Darier disease','keratotic papules in seborrheic areas and specific nail anomalies'),
#                ('Ichthyosis hepatosplenomegaly cerebellar degeneration','ichthyosis, hepatosplenomegaly and late-onset cerebellar ataxia'),
#                ('Emery-Dreifuss muscular dystrophy','muscular weakness and atrophy, with early contractures of the tendons and cardiomyopathy'),
#                ('Costello syndrome','postnatal growth retardation, coarse facies, intellectual deficit, skin anomalies and cardiac abnormalities'),
#                ('Fibrodysplasia ossificans progressiva','congenital malformation of great toes, progressive, disabling heterotopic osteogenesis in predictable anatomical patterns'),
#                ('Acropectorovertebral dysplasia','fusion of the carpal and tarsal bones, with complex anomalies of the fingers and toes'),
#                ('Osteogenesis imperfecta','increased bone fragility and low bone mass'),
#                ('Primary biliary cirrhosis','injury of the intrahepatic bile ducts'),
#                ('Hennekam syndrome','lymphoedema, intestinal lymphangiectasia, intellectual deficit and facial dysmorphism'),
#                ('Hyperlysinemia','elevated levels of lysine in the cerebrospinal fluid and blood'),
#                ('Jackson-Weiss syndrome','tarsal and/or metatarsal coalitions and variable craniosynostosis, accompanied by facial anomalies, broad halluces and normal hands'),
#                ('Jalili syndrome','amelogenesis imperfecta and cone-rod retinal dystrophy'),
#                ('Jeune syndrome','narrow thorax and short limbs'),
#                ('Jackson-Weiss syndrome','tarsal and/or metatarsal coalitions and variable craniosynostosis, accompanied by facial anomalies, broad halluces and normal hands'),
#                ('Multiple myeloma','overproduction of abnormal plasma cells in the bone marrow and manifested by skeletal destruction, bone pain, and presence of abnormous immunoglobulins'),
#                ('Trichodental syndrome','fine, dry and short hair with dental anomalies')]

    #diseaseList=[("Adrenoleukodystrophy  autosomal  neonatal form","Normally developed boy age 5, seizures, ataxia, adrenal insufficiency and degeneration of visual and auditory functions"),
    #            ("Childhood-onset cerebral X-linked adrenoleukodystrophy","Normally developed boy age 5, seizures, ataxia, adrenal insufficiency and degeneration of visual and auditory functions")]

    diseaseList=[("Adrenoleukodystrophy  autosomal  neonatal form","Normally developed boy age 5, progessive development of talking difficulties, seizures, ataxia, adrenal insufficiency and  degeneration of visual and auditory functions"),
                ("Childhood-onset cerebral X-linked adrenoleukodystrophy","Normally developed boy age 5, progessive development of talking difficulties, seizures, ataxia, adrenal insufficiency and  degeneration of visual and auditory functions")]


    printout1=[]
    printout2=[]
    #printout2=([],[],[])
    #formatString = ['Mean:','Median:','Max:' ]

    #clusterThis = ([],[],[])

    print 'Done processing',

#    for disease in diseaseList:
#
#        printout1.append(disease[0][0:5])
#
#        symptoms=FilterInterface.stopwordRemover(disease[1])
#
#        resultLists=search(M_lil, M_csc, symptoms, top)
#
#        found=False
#        count=0
#        for results in resultLists:
#            found=False
#            for result in results:
#                if result[0]==disease[0]:
#                    printout2[count].append(results.index(result))
#                    found=True
#                    clusterThis[count].append(results[:50])
#                    count+=1
#            if not found:
#                printout2[count].append(" ")
#                count+=1
#        print disease[0],

    for disease in diseaseList:

        printout1.append(disease[0][0:5])

        symptoms=FilterInterface.stopwordRemover(disease[1])

        results=search(M_lil, M_csc, symptoms, top)

        found=False
        #count=0
        found=False
        for result in results:
            if result[0]==disease[0]:
                printout2.append(results.index(result))
                found=True
                #clusterThis[count].append(results[:50])
                #count+=1
        if not found:
            printout2.append(" ")
            #count+=1


    print printout1
    print printout2
    #cnt = 0
    #for list in printout2:
    #    print formatString[cnt], list
    #    cnt+=1
    print "TEST DONE"

    #return clusterThis

def runScoreTest4(M_lil, M_csc):

    top=3000

    symptomList=[(""),
                 (""),
                 ("")]

    formatString = ['Mean:','Median:','Max:' ]
    printout2=([],[],[])

    clusterThis = ([],[],[])

    for symptoms in symptomList:

        symptoms=FilterInterface.stopwordRemover(disease[0])

        resultLists=search(M_lil, M_csc, symptoms, top)

        count=0
        for results in resultLists:
            printout2[count].append(results[:20])
            clusterThis[count].append(resultLists[:50])
            count+=1
    cnt = 0
    for list in printout2:
        print formatString[cnt], list
        cnt+=1
    print "TEST DONE"

    return clusterThis


def runScoreTest5(lil, csc):

    top=3000

    """
    ============================================================================
    1) Dreng, normal ved fdslen bortset fra deformitet af begge storeter (de
    manglede et led). Udvikler sig normalt efterflgende. Ved 5 rs alderen


    der viser knoglevv uden malignitetstegn. Kort tid efter biopsien udvikles
    mere knoglevkst, prcis der hvor man har skret.
    ----------------------------------------------------------------------------
    System symptom query:
    Boy, normal birth, deformity of both big toes (missing joint),
    quick development of bone tumor near spine and osteogenesis at biopsy.
    ============================================================================
    2) Normally developed boy until age 5, where he progressively developed the
    following symptoms: Talking difficulties, seizures, ataxia, adrenal
    insufficiency and  degeneration of visual and auditory functions.
    ----------------------------------------------------------------------------
    System symptom query:
    Normally developed boy age 5, progessive development of talking difficulties,
    seizures, ataxia, adrenal insufficiency and  degeneration of visual and
    auditory functions
    ============================================================================
    3) A boy age 14 comes to the doctor with yellow, keratotic plaques on the
    skin of his palms and soles going up onto the dorsal side. Both hands and
    feet are affected.
    
    He equally had swollen and very vulnerable gums since the age of 4 with loss
    of most of his permanent teeth.
    ----------------------------------------------------------------------------
    System symptom query:
    Boy age 14, yellow, keratotic plaques on the skin of palms and soles going
    up onto the dorsal side. Both hands and feet are affected.
    ============================================================================
    4) 16-aarig joedisk dreng har en til to gange om maaneden anfald, hvor han
    foerst og fremmest skal sove utroligt meget - ca. 18 timer om dagen.
    Anfaldene varer ca en uges tid. Han aendrer karakter under anfaldene og
    bliver irritabel og aggressiv, naar han vaekkes. Naar han er vaagen i
    anfaldsperioden spiser han helt utroligt store maengder mad, og hans appetit
    paa sex er endvidere abnormt stor.
    ----------------------------------------------------------------------------
    System symptom query:
    Jewish boy age 16, monthly seizures, sleep deficiency, aggressive and
    irritable when woken, highly increased sexual appetite and hunger.

    ============================================================================
    """

    #diseaseList=[("Boy, normal birth, deformity of both big toes (missing joint), quick development of bone tumor near spine and osteogenesis at biopsy"),
    #             ("Normally developed boy age 5, progessive development of talking difficulties, seizures, ataxia, adrenal insufficiency and  degeneration of visual and auditory functions"),
    #             ("Boy age 14, yellow keratotic plaques on the skin of palms and soles going up onto the dorsal side. Both hands and feet are affected. swollen vulnerable gums, loss of permanent teeth.")]

    #diseaseList=[("Jewish boy age 16, monthly seizures, sleep deficiency, aggressive and irritable when woken, highly increased sexual appetite and hunger")]

    diseaseList=[("Normally developed boy age 5, seizures, ataxia, adrenal insufficiency and degeneration of visual and auditory functions")]


    printout2=[[],[],[]]
    clusterThis=[[],[],[]]

    sanitizer = TextCleaner.sanitizeString()
    count=0
    for disease in diseaseList:

        queryString=sanitizer.sub(' ', disease)

        symptoms=FilterInterface.stopwordRemover(queryString)

        resultLists=searchLabel(lil, csc, symptoms, top)

        printout2[count].append(resultLists)
        clusterThis[count].append(resultLists)
        count+=1

    for list in printout2:
        print list
    print "TEST DONE"

    return clusterThis, printout2


def searchLabel(M_lil, M_csc, queryString, top=20):

    """
    This function is still a work in progress..
    """

    sanitizer = TextCleaner.sanitizeString()
    queryString=sanitizer.sub(' ', queryString)
    
    # OPTIONAL:
    # Stem the information
    if _stemmer:
        # Get the regex pattern that sanitizeses information and sanitize it
        # Stem the information
        queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasure(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    results.sort()
    results.reverse()

    ###########################################################################
    ### For the label matrix: #################################################

    resultDic={}
    for item in results[:top]:
        pmid=item[1]
        label=_labelHash[pmid]
        resultDic[label]=item[0]

    ###########################################################################

       ###################################
       ####### return pmid results #######

    # Reverse and sort the concensus list
    # resultList_mean=sorted(resultDic1.items(), key=lambda(k,v):(v,k), reverse=True)
    # resultList_median=sorted(resultDic2.items(), key=lambda(k,v):(v,k), reverse=True)
    # resultList_max=sorted(resultDic3.items(), key=lambda(k,v):(v,k), reverse=True)

    # return [resultList_mean,resultList_median,resultList_max]

    
    #    Return label results ######

    resultLabelList = sorted(resultDic.items(), key=lambda(k,v):(v,k), reverse=True)

    #return resultLabelList[:20]
    return resultLabelList

    # for disease in diseaseList:

    #     printout1.append(disease[0][0:5])

    #     symptoms=FilterInterface.stopwordRemover(disease[1])

    #     resultLists=search(M_lil, M_csc, symptoms, top)

    #     #        print resultLists
    #     found=False
    #     count=0
    #     # for results in resultLists:
    #     #     found=False
    #     #     print results
    #     # for result in results:
    #     for result in resultLists:
    #         if result[0]==disease[0]:
    #             printout2.append(resultLists.index(result))
    #             #                printout2[count].append(results.index(result))
    #             found=True
    #     if not found:
    #         printout2.append(' ')
    #             #                printout2[count].append(" ")
    #             #            count+=1

    # print printout1
    # #    for list in printout2:
    # #        print list
    # print printout2
    # print "TEST DONE"

