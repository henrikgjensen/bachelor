import os

def loadMedlineRecords(dir):

    modifiedRecords={}

    files=sorted([f for f in os.listdir(dir) if os.path.isfile(dir+f)])

    counter=0
    for file in files:

        diseaseDic=eval(open(dir+file,'r').read())

        diseaseName=file[0:file.find('.txt')]
        modifiedRecords[diseaseName]={}

        medlineRecords=diseaseDic['records']
        for record in medlineRecords:
            modifiedRecords[diseaseName][record['PMID']]=record

        counter+=1
        print "Files remaining:",(len(files)-counter)

    return modifiedRecords



def readMedlineFields(modifiedRecords,listOfFields):

    recordFieldDic={}

    for diseaseRecords in modifiedRecords.values():
        for item in diseaseRecords.items():
            recordFieldDic[item[0]]={}
            for field in listOfFields:
                recordFieldDic[item[0]][field]=item[1][field]

    return recordFieldDic
