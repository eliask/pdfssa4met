#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert PDF to XML.

Created on Mar 1, 2010
@author: John Harrison

Usage: pdf2xml.py [OPTIONS] FILEPATH

OPTIONS:
-h, --help     Print help and exit
"""

import sys, commands, getopt, os, tempfile
import shutil
from lxml import etree
from utils import UsageError, ConfigError
from config import pdf2xmlexe

def pdf2etree(argv=None):
    """Convert a PDF to XML then parse to an LXML etree and return."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.error, msg:
        raise UsageError(msg)
    for o, a in opts:
        if (o in ['-h', '--help']):
            print __doc__
            return 0
    try:
        pdfpath = args[-1]
    except IndexError:
        raise UsageError("You must provide the name of a valid PDF to analyse")

    if not os.path.exists(pdf2xmlexe):
        raise ConfigError("pdftoxml exectutable does not exist at specified path: '{0}'\nPlease check config.py".format(pdf2xmlexe))

    pdffn = os.path.split(pdfpath)[-1]
    tmpdir = tempfile.mkdtemp(suffix='.d', prefix='pdf2xml.py')
    tmppath = os.path.join(tmpdir, "{0}.xml".format(pdffn))

    def escape(x):
        return x.replace('\\', r'\\').replace('"', '\\"')
    cmdline = '"{0}" -q -blocks "{1}" "{2}"'.format(*map(escape,[pdf2xmlexe, pdfpath, tmppath]))
    x = commands.getoutput(cmdline)
    if x: print >>sys.stderr, x
    try:
        with open(tmppath, 'r') as fh:
            tree = etree.parse(fh)
    except IOError, e:
        raise UsageError("Could not convert to XML: {0}. Are you sure you provided the name of a valid PDF? ".format(e))
    else:
        return tree
    finally:
        shutil.rmtree(tmpdir)

def pdf2xml(argv=None):
    try:
        tree = pdf2etree(argv)
        print etree.tostring(tree, method="xml", pretty_print=True, encoding="UTF-8")
    except TypeError:
        return tree
    except UsageError as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    except ConfigError, err:
        sys.stderr.writelines([str(err.msg),'\n'])
        sys.stderr.flush()
        return 1
    else:
        return 0

if __name__ == '__main__':
    sys.exit(pdf2xml(None))
