import IOmodule as IO

# Main folder
_mainFolder=os.getenv("HOME")+"/"+"The_Hive"
# Phase subfolder
_subFolder = _mainFolder+"/"+"term_doc"
# MedLine record directory
_medlineDir=_mainFolder+"/data_acquisition/"+"medline_records"
# Term-doc directory
_termDocDir=_subFolder+"/"+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_subFolder+"/"+"hashTables"
# Disease label hash
_labelHash="labelHash"


def getRowIndices():

    # Read through medline articles and get PMID to extract from
    # complete term doc.

    pmidHashTable=IOmodule.pickleIn(_hashTablesDir, _pmidHash)

    listofpmids=[]
    for i in range(len(f['records'])):
        listofpmids.append(f['records'][field]['PMID'])

    return listofpmids

def createLabelVector():

    # Sum over all columns and return a 1 x 456xxx vector

    return labelVector

def constructLabelMatrix():

    listoffiles = IO.getSortedFilelist('/root/The_Hive/data_acquisition/medline_records/'):    

    listofpmids=[]
    for f in listoffiles:
        file_content = IO.evalIn(f)
        
        listofpmids=getRowIndices(file_content)

    IO.writeOutTDM('/tmp', 'test')
