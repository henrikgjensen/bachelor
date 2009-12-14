import RecordHandler as RH

def testRH():

    path="/root/The_Hive/data_acquisition/medline_records"
    disease="Winkelman Bethge Pfeiffer syndrome.txt"


    records = RH.loadMedlineRecords(path,disease)

    fields = RH.readMedlineFields(records,['TI','MH', 'AB'])

    l = []

    

    for entry in fields.items():
        # Get the abstract
        try:
            information=entry[1]['TI']
        except:
            print 'Unable to find title in', entry[0]
            continue
        try:
            information+=entry[1]['AB']
        except:
            print 'Unable to find abstract in', entry[0]
            continue
        try:
            for meshterm in entry[1]['MH']:
                information+=' '+meshterm
        except:
            print 'Unable to find MeSH in', entry[0]
            continue
        # MESH GOES HERE

        # Sanitize the abstract
#        abstract=sanitizer.sub(' ', abstract)
        # Remove english stopwords from the abstract
 #       abstract=FilterInterface.stopwordRemover(abstract)

        # OPTIONAL:
        # Stem the abstract
  #      if _stemmer: abstract=FilterInterface.porterStemmer(abstract)

        l.append((entry[0],information))

    return l
