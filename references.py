#!/bin/env python
# coding=utf-8
"""Extract and tag References from a PDF.

Created on Mar 1, 2010
@author: John Harrison

Usage: references.py OPTIONS FILEPATH

OPTIONS:
-h, --help     Print help and exit
-t, --test     Carry out unit tests on RegEx reference tagging
--noxml        Do not tag individual references, and their component parts with XML tags. 
                Default is to include tagging.
--highlight    Highlight inserted XML tags using a different color. 
                This is useful for a human user looking at the output, but should be omitted when the output is to be used in other programmes.
                Default is NOT to highlight.
                
Examples:

>>> split_refs('[1] J. S. Al-Sumait, J. K. Sykulski, and A. K. Al-Othman, "Solution of different types of economic load dispatch problems using a pattern search method," Electric Power Components and Systems, vol. 36, pp. 250-265, 2008. [2] J. S. Al-Sumait, A. K. Al-Othman, and J. K. Sykulski, "Application of pattern search method to power system valve-point economic load dispatch," International Journal of Electrical Power and Energy Systems, vol. 29, pp. 720-730, 2007.')
['[1] J. S. Al-Sumait, J. K. Sykulski, and A. K. Al-Othman, "Solution of different types of economic load dispatch problems using a pattern search method," Electric Power Components and Systems, vol. 36, pp. 250-265, 2008.', '[2] J. S. Al-Sumait, A. K. Al-Othman, and J. K. Sykulski, "Application of pattern search method to power system valve-point economic load dispatch," International Journal of Electrical Power and Energy Systems, vol. 29, pp. 720-730, 2007.']

>>> split_refs('[33] Wong KP, Wong YW. Thermal generator scheduling using hybrid genetic simulated-annealing. Generation, transmission and distribution. IEE Proc 1995;142:372-80. [34] Chen PH, Chang HC. Large-scale economic dispatch by genetic algorithm. Power Syst IEEE Trans 1995;10:1919-26.')
['[33] Wong KP, Wong YW. Thermal generator scheduling using hybrid genetic simulated-annealing. Generation, transmission and distribution. IEE Proc 1995;142:372-80.', '[34] Chen PH, Chang HC. Large-scale economic dispatch by genetic algorithm. Power Syst IEEE Trans 1995;10:1919-26.']

>>> tag_ref('''[1] J. S. Al-Sumait, J. K. Sykulski, and A. K. Al-Othman, "Solution of different types of economic load dispatch problems using a pattern search method," Electric Power Components and Systems, vol. 36, pp. 250-265, 2008.''')
'<reference>[1] J. S. Al-Sumait, J. K. Sykulski, and A. K. Al-Othman, "<title>Solution of different types of economic load dispatch problems using a pattern search method,</title>" Electric Power Components and Systems, vol. <volume>36</volume>, pp. <pages>250-265</pages>, <year>2008</year>.</reference>'

>>> tag_ref('''[33] Wong KP, Wong YW. Thermal generator scheduling using hybrid genetic simulated-annealing. Generation, transmission and distribution. IEE Proc 1995;142:372-80.''')
'<reference>[33] Wong KP, Wong YW. Thermal generator scheduling using hybrid genetic simulated-annealing. Generation, transmission and distribution. IEE Proc <year>1995</year>;142:<pages>372-80</pages>.</reference>'

>>> tag_ref('')
'<reference></reference>'
"""

import sys, getopt, re
from lxml import etree
from utils import Usage
from pdf2xml import pdf2etree

#ref_re = re.compile(".+?(?=\[\d+?\])", re.DOTALL)
ref_re = re.compile("\[\d+?\]\s.+?[0-9]{2}\.(?#=\s[[$])", re.MULTILINE)
url_re = re.compile("((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)")
title_re = re.compile(u'("|“|“)(.+?)("|”|”)'.encode('utf8'), re.DOTALL)
vol_re = re.compile('([Vv]ol(?:\.|ume)\s)([0-9]+)')
ed_re = re.compile('([0-9]+)(\sed\W)')
pages_re1 = re.compile(u'([Pp]p\.?\s?)([0-9]+[-\u2013][0-9]+)')
pages_re2 = re.compile(u'(:)([0-9]+[-\u2013][0-9]+)')
year_re1 = re.compile("(, )([1-2][0-9]{3})(\D)")
year_re2 = re.compile("\(([1-2][0-9]{3})\)")
year_re3 = re.compile("([1-2][0-9]{3})(;)")

def split_refs(txt):
    """Split text into individual references and return."""
    global ref_re
    refs = ref_re.findall(txt)
    if len(refs) <= 1:
        refs = txt.split('\n')
    return refs
    #- end get_refs()
                    
def tag_ref(txt, highlight=False):
    """Tag component parts of a reference and return."""
    global url_re, title_re, vol_re, ed_re, pages_re, year_re
    if highlight:
        txt = title_re.sub("\g<1>\033[0;32m<title>\033[0m\g<2>\033[0;32m</title>\033[0m\g<3>", txt, 1)
        txt = vol_re.sub("\g<1>\033[0;32m<volume>\033[0m\g<2>\033[0;32m</volume>\033[0m", txt)
        txt = ed_re.sub("\033[0;32m<edition>\033[0m\g<1>\033[0;32m</edition>\033[0m\g<2>", txt)
        txt = pages_re1.sub("\g<1>\033[0;32m<pages>\033[0m\g<2>\033[0;32m</pages>\033[0m", txt)
        txt = pages_re2.sub("\g<1>\033[0;32m<pages>\033[0m\g<2>\033[0;32m</pages>\033[0m", txt)
        txt = year_re1.sub("\g<1>\033[0;32m<year>\033[0m\g<2>\033[0;32m</year>\033[0m\g<3>", txt)
        txt = year_re2.sub("(\033[0;32m<year>\033[0m\g<1>\033[0;32m</year>\033[0m)", txt)
        txt = year_re3.sub("\033[0;32m<year>\033[0m\g<1>\033[0;32m</year>\033[0m\g<2>", txt)
        txt = url_re.sub("\033[0;34m\g<0>\033[0m", txt)
        txt = "\033[0;32m<reference>\033[0m" + txt + "\033[0;32m</reference>\033[0m"
    else:
        txt = title_re.sub("\g<1><title>\g<2></title>\g<3>", txt, 1)
        txt = vol_re.sub("\g<1><volume>\g<2></volume>", txt)
        txt = ed_re.sub("<edition>\g<1></edition>\g<2>", txt)
        txt = pages_re1.sub("\g<1><pages>\g<2></pages>", txt)
        txt = pages_re2.sub("\g<1><pages>\g<2></pages>", txt)
        txt = year_re1.sub("\g<1><year>\g<2></year>\g<3>", txt)
        txt = year_re2.sub("(<year>\g<1></year>)", txt)
        txt = year_re3.sub("<year>\g<1></year>\g<2>", txt)
        txt = "<reference>" + txt + "</reference>"
    return txt.encode('utf-8')
    #- end tag_ref()

def pdf2refs(opts, args):
    """."""
    global url_re
    xmltag = True
    highlight = False
    for o, a in opts:
        if (o == '--noxml'):
            xmltag = False
        elif (o == '--highlight'):
            highlight = True
    tree = pdf2etree(args)
    pubs = []
    urls = []
    try:
        xps = tree.xpath('//BLOCK')
    except AttributeError:
        return tree
    hit_ref = 0
    refs = []
    for el in xps:
        origtxts = []
        for el2 in el.iter():
            try: origtxts.append(el2.text.strip())
            except AttributeError: pass
            if el2 != el and el2.tail is not None:
                origtxts.append(el2.tail.strip())
        origtxt = ' '.join(origtxts)
        if not len(origtxt):
            continue
        elif origtxt.strip().startswith(('Reference', 'REFERENCE')) or origtxt.find('Reference') > 0 or origtxt[:20].find('REFERENCE') > 0:
            hit_ref = 1
            continue
        elif hit_ref:
            refs.append(origtxt)
            
    for ref in split_refs('\n'.join(refs)):
        for url in url_re.findall(ref):
            urls.append(url[0])
            
        pubbits = []
        for pubnode in el.xpath(".//TOKEN[@italic='yes']"):
            pubtxt = etree.tostring(pubnode, method='text', encoding="UTF-8")
            pubbits.append(pubtxt)

        if len(pubbits): pubs.append(' '.join(pubbits))
        if xmltag:
            ref = tag_ref(ref, highlight)
        sys.stdout.write(ref + '\n')
        sys.stdout.flush()

    if len(pubs):
        sys.stdout.write('-'*10 + "\nCited Publications\n" + '-'*10 + '\n')
        for pub in pubs:
            sys.stdout.write(pub + '\n')
            sys.stdout.flush()
    if len(urls):
        sys.stdout.write('-'*10 + "\nCited URLs\n" + '-'*10 + '\n')
        for url in urls:
            sys.stdout.write(url + '\n')
            sys.stdout.flush()
    # end pdf2refs()      


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        try:
            opts, args = getopt.getopt(argv, "ht", ["help", "test", "noxml", "highlight"])
        except getopt.error, msg:
            raise Usage(msg)
        for o, a in opts:
            if (o in ['-h', '--help']):
                # print help and exit
                sys.stdout.write(__doc__)
                sys.stdout.flush()
                return 0
            elif (o in ['-t', '--test']):
                # do unit test
                import doctest
                doctest.testmod()
                return 0
        pdf2refs(opts, args)

    except Usage, err:
        sys.stderr.write(err.msg)
        sys.stderr.write("for help use --help")
        sys.stderr.flush()
        return 2

if __name__ == '__main__':        
    sys.exit(main())
