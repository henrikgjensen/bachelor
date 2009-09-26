import urllib2
import re
import os
from BeautifulSoup import BeautifulSoup

DIRECTORY = 'abstractFiles'
try:
        os.mkdir(DIRECTORY)

#except OSError:
#        print 'the directory %s is already exist' %DIRECTORY
except:
    print 'test'

f=open('output-1.txt', 'r')

tickers = ['1111111']
#for line in f:
#        tickers.append(line[13:21])

os.chdir(DIRECTORY)
for t in tickers:
        try:

                rows=urllib2.urlopen( \
                'http://www.ncbi.nlm.nih.gov/sites/entrez?db=pubmed&cmd=search&term=%s' \
                %t).read()

                #print 'rows:'+rows+'\n'

                soup = BeautifulSoup(rows)

                print 'soup:'+str(soup)+'\n'
                temp = file('214681.txt','w')
                tempopen = open('214681','w')
                tempopen.write(str(soup))


                abs = soup.findAll('p',attrs={'class' : re.compile('abstract')})

                print 'abs:'+str(abs)+'\n'

                ab = str(abs[0])
                ab = ab[20:]

                ab = ab.replace('</p>','\"')
                t = open(t+'.txt','w')

                t.write(ab)
                t.close()

        except IOError:

                errors = [t]
                errf = open('bad_trickers.txt','w+')

                errf.write(str(errors))
                errf.close()

                print errors
f.close()