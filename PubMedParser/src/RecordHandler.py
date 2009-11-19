
def loadMedlineRecords(dir,filename):

    modifiedRecords={}

    diseaseDic=eval(open(dir+filename,'r').read())

    diseaseName=filename[0:filename.find('.txt')]
    modifiedRecords[diseaseName]={}

    medlineRecords=diseaseDic['records']
    for record in medlineRecords:
        modifiedRecords[diseaseName][record['PMID']]=record

    return modifiedRecords


def readMedlineFields(modifiedRecords,listOfFields):

    recordFieldDic={}

    for diseaseRecords in modifiedRecords.values():
        for item in diseaseRecords.items():
            recordFieldDic[item[0]]={}
            for field in listOfFields:
                recordFieldDic[item[0]][field]=item[1][field]

    return recordFieldDic