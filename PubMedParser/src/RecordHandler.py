
def loadMedlineRecords(dir,filename):

    """
    This function loads a MedLine record file and returns a dictionary on the
    form {DiseaseName: [[PMID, {MedLine Records}],...]} for further processing.

    It takes the full path to the record directory and the filename of the
    given disease/records.
    """

    modifiedRecords={}

    diseaseDic=eval(open(dir+"/"+filename,'r').read())

    diseaseName=filename[0:filename.find('.txt')]
    modifiedRecords[diseaseName]=[]

    medlineRecords=diseaseDic['records']
    for record in medlineRecords:
        modifiedRecords[diseaseName].append([record['PMID'],record])

    return modifiedRecords


def readMedlineFields(modifiedRecords,listOfFields):

    """
    This function is used to extract field information in MedLine records.
    It returns a dictionary on the form {PMID: {Field1 : content1,...},...}

    It takes a dictionary on the form given by the 'loadMedlineRecords'
    function, and a list of the fields to be returned.
    """

    recordFieldDic={}

    for diseaseRecords in modifiedRecords.values():
        for item in diseaseRecords:
            recordFieldDic[item[0]]={}
            for field in listOfFields:
                try:
                    recordFieldDic[item[0]][field]=item[1][field]
                except:
                    # Lots of records do not have the field 'MH' so we
                    # skip printing
                    # print "Did not locate",field
                    continue
    return recordFieldDic
