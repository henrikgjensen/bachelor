import os
import numpy as np
#from matplotlib import pylab as pl
import math
import IOmodule

def countRecordfield(directory,field):

    """
    This function counts the number of identical fields in the MedLine records.

    This could for instance be used for a view into how many identical PMIDs
    that have been downloaded on the cross of different disease searches.

    It takes a medline record directory (full path) and a field.

    It returns a dictionary on the form: {PMID: #ids,...}
    """
    
    fieldSum={}
#    files=sorted([f for f in os.listdir(directory) if os.path.isfile(directory+f)])
    files = IOmodule.getSortedFilelist(directory+'/')

    counter=0
    for f in files:

        diseaseDic=eval(open(directory+f,'r').read())

        medlineRecords=diseaseDic['records']

        for record in medlineRecords:
            print record
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

def countFields(directory, fields):

        # files=sorted([f for f in os.listdir(directory) if os.path.isfile(directory+f)])

        files = IOmodule.getSortedFilelist(directory+'/')
        
        fieldSum={}
        counter=0
        pmidCounter=0
        emptyCounter=0
        noDescription=0

        for f in files:
            
            fd = open(directory+f,'r')
            
            diseaseDic=eval(fd.read())

            fd.close()
            
            medlineRecords=diseaseDic['records']

            descriptionField=diseaseDic['description']

            if descriptionField== '':
                noDescription+=1

            if medlineRecords == []:
                print "Found empty record"
                emptyCounter+=1

            for record in medlineRecords:
                pmidCounter+=1
                for label in fields:
                    fieldSum.setdefault(label,0)
                    if label in record:
                        fieldSum[label]+=1

            counter+=1
            print "Files remaining:",(len(files)-counter)
                
        return fieldSum,{'pmid count': pmidCounter},{'empty diseases': emptyCounter}

def pmidDuplicateCounter(directory, number=None):

        # files=sorted([f for f in os.listdir(directory) if os.path.isfile(directory+f)])[:number]
        files = IOmodule.getSortedFilelist(directory+'/')
        
        pmidCount={}
        counter=0
        for f in files:
            # Open file descriptor
            fd = open(directory+'/'+f,'r')
            # Read in from file
            diseaseDic=eval(fd.read())
            # Close the file descriptor nicely again
            fd.close()
            
            medlineRecords=diseaseDic['records']

            for record in medlineRecords:
                pmidCount.setdefault(record['PMID'],0)
                pmidCount[record['PMID']]+=1

            counter+=1
            if counter % 1000 == 0:
                print counter
#            print "Files remaining:",(len(files)-counter)
                
        return pmidCount

# def makeHistogram(data, numberOfBins=None):

#     """
#     Recieves a list of the form: [1,1,2,3,5,2,6,7,3,2,1,2,3,...,]

#     Makes a histogram of the different counts. This is very screwed as
#     we have some 602205 'unique' pmids with the count 1, and all the
#     uothers are insignificant in relation to that number.
#     """

#     # Need to transform the dictionary into a list of single values
# #    data = [v for k,v in dictionaryToMakeHistogramFrom.items()]
    
#     hN = pl.hist(data, bins=numberOfBins)

#     xmin = min(hN[2])
#     xmin = math.floor(xmin)

#     xmax = max(hN[2])
#     xmax = math.ceil(xmax)

#     range = xmax - xmin

#     delta = 0.0 * range
#     print "Delta is",delta

#     pl.xlim([xmin - delta, xmax + delta])

#     pl.show()    
#     hN = pl.hist(dataTwo, orientation='horizontal', normed=0, rwidth=0.8, label='ONE')
#     hS = pl.hist(dataOne, bins=hN[1], orientation='horizontal', normed=0, 
#                  rwidth=0.8, label='TWO')

#     for p in hS[2]:
#         p.set_width( - p.get_width())
        
#     xmin = min([ min(w.get_width() for w in hS[2]), 
#                  min([w.get_width() for w in hN[2]]) ])
#     xmin = np.floor(xmin)
#     xmax = max([ max(w.get_width() for w in hS[2]), 
#                  max([w.get_width() for w in hN[2]]) ])
#     xmax = np.ceil(xmax)
#     range = xmax - xmin
#     delta = 0.0 * range
#     pl.xlim([xmin - delta, xmax + delta])
#     xt = pl.xticks()
#     n = xt[0]
#     s = ['%.1f'%abs(i) for i in n]
#     pl.xticks(n, s)
#     pl.legend(loc='best')
#     pl.axvline(0.0)
#     pl.show()

#    return data
