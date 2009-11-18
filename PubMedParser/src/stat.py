import math
import DiseaseCrawler as DC
import os

def calculateStatistic(directory=None, dictionary=None, itemOfInterest=None):

    if(directory == None and dictionary == None and itemOfInterest=None):
        # Throw an exception you have to supply one or more of the things
        print 'missing argument'
#        break

    if(directory != None):
        path=os.getenv("HOME")+'/'+directory+'/'

        files=sorted([f for f in os.listdir(path) if os.path.isfile(path+f)])
        numberOfFiles = len(files)
        
        print 'Total number of files:', numberOfFiles
        
        numberOfDescriptions=0
        for file in files:
            diseaseName=file[0:file.find('.txt')]
            diseaseInformation = eval(open(path+file,'r').read())
            if(len(diseaseInformation['description']) != 0):
                numberOfDescriptions+=1

#            print diseaseInformation

        print 'Total number of descriptions:',numberOfDescriptions
        print 'Percent of diseases containing descriptions:', str(numberOfDescriptions/float(numberOfFiles)) + '%'

    print 'And we\'re done!'

