import os.path
import os
import pickle
from scipy.io import mmwrite
from scipy.io import mmread
import numpy

def writeOutTxt(dir,filename,text,mode='w'):

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

def pickleOut(dirname, filename, object):
# writeOut Term Document Matrix
# Where object = (Matrix, TermList, PmidList)

# Actually object do not need to look like that, the object just needs
# to be pickleable

    """
    Simple function for writing a term document matrix, and its
    associated term list and pmid list. It writes to a dirname and a
    filename, is these do not exists it creates them. If they do
    exists it simply overwrites the file.

    The directory is created in the $HOME directory of the user on the
    work station.

    The format is pythons seriaized object via the pickle module.

    """

    path=os.getenv("HOME")+'/'

    if not os.path.isdir(path+dirname):
        os.mkdir(path+dirname)

    filepath=path+dirname+'/'+filename+'.btd' # binary term document matrix
    print filepath
    fd = open(filepath,'w')
    pickle.dump(object,fd)
    fd.close()

def writeOutTDM(dirname, filename, matrix, type='numpy.float32'):
# writeOut Term Document Matrix

    """
    Receives a dirname, filename, matrix and optional type, which is
    defined by numpy, and is e.g. numpy.float32, numpy.integer etc.
    Uses mmwrite to write out matrices, saving them in Matrix Marked
    format which saves a lot of space 
    """

    path=os.getenv("HOME")+'/'
    
    if not os.path.isdir(path+dirname):
        os.mkdir(path+dirname)

    filepath=path+dirname+'/'+filename # binary term document matrix
    print filepath
    # Write out the Matrix Marked file
    try:
        mmwrite(filepath, matrix, type)
    except:
        print 'Unable to write', filepath,'\n'+matrix.__repr__(),'\n'+type

def readInTDM(dirname, filename):

    """
    Receives dirname without / infront or behind. And filename without
    extention.
    """

    path=os.getenv("HOME")+'/'

    path+=dirname+'/'+filename

    try:
        A = mmread(path)
    except:
        print 'Unable to read', path

    return A
