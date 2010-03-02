#!/bin/env python
"""Convert PDF to XML.

Created on Mar 1, 2010
@author: John Harrison

Usage: pdf2xml.py [OPTIONS] FILEPATH

OPTIONS:
-h, --help     Print help and exit
"""

import sys, commands, getopt, os, tempfile
from lxml import etree
from utils import Usage
from config import pdf2xmlexe

def pdf2etree(argv=None):
    """Convert a PDF to XML then parse to an LXML etree and return."""
    try:
        if argv is None:
            argv = sys.argv[1:]
        try:
            opts, args = getopt.getopt(argv, "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
        for o, a in opts:
            if (o in ['-h', '--help']):
                print __doc__
                return 0
        try:
            pdfpath = args[-1]
        except IndexError:
            raise Usage("You must provide the name of a valid PDF to analyse")
        
        pdffn = os.path.split(pdfpath)[-1]
        tmpdir = tempfile.mkdtemp(suffix='.d', prefix=pdffn)
        tmppath = os.path.join(tmpdir, "{0}.xml".format(pdffn))
        cmdline = "{0} -q -blocks {1} {2}".format(pdf2xmlexe, pdfpath, tmppath)
        commands.getoutput(cmdline)
        try:
            with open(tmppath, 'r') as fh:
                tree = etree.parse(fh)
        except IOError:
            raise Usage("Could not convert to XML. Are you sure you provided the name of a valid PDF?")
        else:
            return tree
        
    except Usage as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2    

def pdf2xml(argv=None):
    tree = pdf2etree(argv)
    try:
        print etree.tostring(tree, method="xml", pretty_print=True, encoding="UTF-8")
    except TypeError:
        return tree
    else:
        return 0

if __name__ == '__main__':
    sys.exit(pdf2xml(None))
