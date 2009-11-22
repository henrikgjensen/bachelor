import os

def countRecordfield(directory,field):

    """
    This function counts the number of identical fields in the MedLine records.

    This could for instance be used for a view into how many identical PMIDs
    that have been downloaded on the cross of different disease searches.

    It takes a medline record directory (full path) and a field.

    It returns a dictionary on the form: {PMID: #ids,...}
    """
    
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

    """
    This function simply sorts the values of a dictionry and optionally
    reverses them.
    """

    l=sorted(dic.values())
    if option==large2small:
        l.reverse()

    return l
