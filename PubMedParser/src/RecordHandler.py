
def loadMedlineRecords(dir,filename):

    """
    This function loads a MedLine record file and returns a dictionary on the
    form {DiseaseName: [[PMID, {MedLine Records}],...]} for further processing.

    It takes the full path to the record directory and the filename of the
    given disease/records.
    """

    modifiedRecords={}

    diseaseDic=eval(open(dir+filename,'r').read())

    diseaseName=filename[0:filename.find('.txt')]
    modifiedRecords[diseaseName]=[]

    medlineRecords=diseaseDic['records']
    for record in medlineRecords:
        modifiedRecords[diseaseName].append([record['PMID'],record])

    return modifiedRecords


def readMedlineFields(modifiedRecords,listOfFields):

    """

    """

    recordFieldDic={}

    for diseaseRecords in modifiedRecords.values():
        for item in diseaseRecords:
            recordFieldDic[item[0]]={}
            for field in listOfFields:
                recordFieldDic[item[0]][field]=item[1][field]
    return recordFieldDic