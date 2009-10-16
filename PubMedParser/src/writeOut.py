import os.path
import os

def writeOut(dir,filename,text):

    """
    Simple function for creating a dictionary (if it does not exsist) and
    writing a file to it.

    The dictionary is created in the home folder of the workstation.
    """

    string=str(text)

    path=os.getenv("HOME")+'/'
    if not os.path.isdir(path+dir):
        os.mkdir(path+dir)

    filepath=path+dir+'/'+filename+'.txt'
    print filepath
    out = file(filepath,'w')
    out.write(string)
    out.close()
