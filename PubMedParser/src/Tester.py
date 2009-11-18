import WordCounter
import RecordHandler

def test(dirname, filename):

    l = []
    
#    filename = 'Diabetes hypogonadism deafness mental retardation.txt'
#    dirname = '/home/bp/diseaseInformation2/'

    records = RecordHandler.loadMedlineRecords(dirname,filename)

    interesting_records = RecordHandler.readMedlineFields(records,['AB'])

    for entry in interesting_records.items():
        l.append(WordCounter.wc(entry[0],entry[1]['AB']))

    return l
