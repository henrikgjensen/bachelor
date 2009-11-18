

def _loadDiseaseFile(filepath):

    try:
        diseaseDic=eval(open(filepath,'r').read())
    except:
        print "Failed to open",filepath

    return diseaseDic


def readMedlineFields(filepath,listOfFields):

    diseaseDic=_loadDiseaseFile(filepath)

    medlineRecords=diseaseDic['records']

    fieldDic={}
    for field in listOfFields:
        fieldDic[field]=[]

    for record in medlineRecords:
            
            fieldDic[field]=record[field]

