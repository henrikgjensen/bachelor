#! /usr/bin/python

import IOmodule as IO
import FilterInterface as FI

M_coo=IO.readInTDM("/root/The_Hive/term_doc/termDoc", "TermDoc")
FI.generateLogTFIDF(M_coo)
