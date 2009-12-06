#! /usr/bin/python

import IOmodule as IO
import FilterInterface as FI
reload(IO)
reload(FI)

def run():
    M_coo=IO.readInTDM("/root/The_Hive/term_doc/termDoc", "TermDoc")
    tfidfMatrix=FI.generateLogTFIDF(M_coo)
    return tfidfMatrix
