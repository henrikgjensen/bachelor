import os

def countRecordfield(directory,field):

    fieldSum={}
    files=sorted([f for f in os.listdir(directory) if os.path.isfile(directory+f)])

    counter=0
    for file in files:

        diseaseDic=eval(open(directory+file,'r').read())

        medlineRecords=diseaseDic['records']

        for record in medlineRecords:
            item=record[field]
            fieldSum.setdefault(item,0)
            fieldSum[item]+=1

        counter+=1
        print "Files remaining:",(len(files)-counter)

    return fieldSum


def getSortedValues(dic,option="small2large"):

    l=sorted(dic.values())
    if option==large2small:
        l.reverse()

    return l
