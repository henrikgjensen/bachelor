import os

def countRecordfield(directory,field):

    fieldSum={}
    files=sorted([f for f in os.listdir(directory) if os.path.isfile(directory+f)])

    for file in files:

        #diseaseName=file[0:file.find('.txt')]
        diseaseDic=eval(open(filepath+file,'r').read())

        medlineRecords=diseaseDic['records']

        for record in medlineRecords:
            item=record[field]
            fieldSum.setdefault(item,0)
            fieldSum[item]+=1

    return fieldSum
    