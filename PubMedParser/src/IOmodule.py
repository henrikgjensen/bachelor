import os.path
import os

def writeOut(dir,filename,text,mode='w'):

    """
    Simple function for creating a directory (if it does not exsist) and
    writing a file to it.

    The mode-parameter is set to 'w' (or 'write') by default and overwrites any
    existing file with the same name. For appending text, use 'a' in the
    optional mode-parameter.

    The directory is created in the home folder of the workstation.
    """

    string=str(text)

    path=os.getenv("HOME")+'/'
    if not os.path.isdir(path+dir):
        os.mkdir(path+dir)

    filepath=path+dir+'/'+filename+'.txt'
    print filepath
    out = file(filepath,mode)
    out.write(string)
    out.close()

