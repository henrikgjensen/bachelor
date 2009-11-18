def getD():
    # URL
    # http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&Term=%22aagenaes+syndrome%22%5BAll+Fields%5D+OR+%22CHOLESTASIS%2DLYMPHEDEMA+SYNDROME%22%5BAll+Fields%5D

    #Synonyms
    # Cholestasis lymphedema syndrome, CHLS, LCS, LCS1, Lymphedema cholestasis syndrome

    d={}
    d['Aagenaes syndrome']={}
    d['Aagenaes syndrome']['terms'] = '"aagenaes+syndrome"[All+Fields]+OR+"CHOLESTASIS-LYMPHEDEMA+SYNDROME"[All+Fields]'
    d['Aagenaes syndrome']['syn'] = []
    d['Aagenaes syndrome']['db'] = 'pubmed'
    d['Aagenaes syndrome']['syn'].extend(['Cholestasis lymphedema syndrome','CHLS','LCS','LCS1','Lymphedema cholestasis syndrome'])
    d['Aagenaes syndrome']['desc'] = 'This is beatiful'
    
    return d

def getF():
    # URL
    # http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=omim&cmd=Display&dopt=omim_pubmed_calculated&from_uid=100700

    # Synonyms
    # Arachnodactyly, receding lower jaw and joint laxity of hands/feet

    f={}
    f['Achard syndrome']={}
    f['Achard syndrome']['terms'] = ''
    f['Achard syndrome']['syn'] = []
    f['Achard syndrome']['uid'] = '100700'
    f['Achard syndrome']['db'] = 'omim'
    f['Achard syndrome']['syn'].extend(['Arachnodactyly', 'receding lower jaw and joint laxity of hands feet'])
    f['Achard syndrome']['desc'] = 'This is beatiful'
    
    return f
