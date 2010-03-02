#!/bin/env python
""" Extract and tag References from a PDF.

Created on Mar 1, 2010
@author: John Harrison

Usage: headings.py OPTIONS FILEPATH

OPTIONS:
--help, -h     Print help and exit
--noxml        Do not tag individual headings with XML tags.
                Default is to include tagging.
--title        Only print title then exit
--author       Only print author then exit
"""

import sys, getopt
from lxml import etree
from utils import UsageError, ConfigError, mean, median
from pdf2xml import pdf2etree


def pdf2heads(opts, args):
    xmltag = True
    highlight = False
    titleonly = False
    authonly = False
    for o, a in opts:
        if (o == '--noxml'):
            xmltag = False
        elif (o == '--highlight'):
            highlight = True
        if (o == '--title'):
            titleonly = True
        elif (o == '--author'):
            authonly = True

        tree = pdf2etree(args)

    # find title
    page = 1
    block = 1
    title_node = None
    while True:
        try: title_node = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
        except IndexError: page+=1
        else: break
        if page > 2:
            # probably not going to find it now
            break
        
    # find author
    page = 1
    block = 2
    auth_node = None
    while True:
        try: auth_node  = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
        except InbdexError: block+=1
        else: break
        if block > 4:
            # probably not going to find it now
            break
    
    font_sizes = tree.xpath('//TOKEN/@font-size')
    mean_font_size =  mean(font_sizes)
    median_font_size = median(font_sizes)

    #print "Median Font Size (i.e. body text):", median_font_size

    font_colors = tree.xpath('//TOKEN/@font-color')
    font_color_hash = {}
    for fc in font_colors:
        try:
            font_color_hash[fc]+=1
        except KeyError:
            font_color_hash[fc] = 1

    sortlist = [(v,k) for k,v in font_color_hash.iteritems()]
    sortlist.sort(reverse=True)
    main_font_color = sortlist[0][1]
    head_txts = []
    stop = False
    for page_node in tree.xpath('//PAGE'):
        for block_node in page_node.xpath('.//BLOCK'):
            if xmltag:
                if block_node == title_node:
                    st = "<title>"
                    et = "</title>"
                elif block_node == auth_node:
                    st = "<author>"
                    et = "</author>"
                else:
                    st = "<heading>"
                    et = "</heading>"
                    
                if highlight:
                    st = "\033[0;32m{0}\033[0m".format(st)
                    et = "\033[0;32m{0}\033[0m".format(et)
            else:
                st = et = ""
            if block_node == title_node and authonly:
                continue
            headers = block_node.xpath(".//TOKEN[@font-size > {0} or @bold = 'yes' or @font-color != '{1}']".format(mean_font_size*1.05, main_font_color))
            head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in headers])
            if len(head_txt):
                head_txts.append("{0}{1}{2}".format(st, head_txt, et))
                
            if block_node == title_node and titleonly:
                stop = True
                break
            elif block_node == auth_node and authonly:
                stop = True
                break
        if stop:
            break
    for txt in head_txts:
        sys.stdout.writelines([txt, '\n'])

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        try:
            opts, args = getopt.getopt(argv, "ht", ["help", "test", "noxml", "highlight", "title", "author"])
        except getopt.error as msg:
            raise UsageError(msg)
        for o, a in opts:
            if (o in ['-h', '--help']):
                # print help and exit
                sys.stdout.write(__doc__)
                sys.stdout.flush()
                return 0
            
        pdf2heads(opts, args)

    except UsageError as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    except ConfigError, err:
        sys.stderr.writelines([str(err.msg),'\n'])
        sys.stderr.flush()
        return 1

if __name__ == '__main__':        
    sys.exit(main())
