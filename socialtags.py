"""Use a Web-Service to generate Social Tags for the PDF.

Created on Mar 2, 2010
@author: John Harrison

Usage: socialtags.py OPTIONS FILEPATH

OPTIONS:
--help, -h     Print help and exit
"""

import sys, getopt, commands
from lxml import etree
from utils import Usage
from config import OpenCalais_API_Key as api_key
from pdf2xml import pdf2etree
from openCalais import OpenCalaisService

def opencalaistags(opts, args):
    global api_key
    tree = pdf2etree(args)
    # could do something more sophisticated, but for now use full text
    full_text = ' '.join([etree.tostring(el, method="text", encoding="UTF-8") for el in tree.xpath('//TOKEN')])
    oc = OpenCalaisService("http://api1.opencalais.com/enlighten/rest/", api_key, "PDF SSA4MET Open Calais Tagger")
    ft_graph = oc.rdfFromText(full_text)
    
#    for t in oc.entitiesFromRdf(ft_graph):
#        print str(t)

#    print '-'*10,"\nEntities from Open Calais\n",'-'*10
#    for t in oc.entitiesFromRdf(ft_graph):
#        print str(t)

#    print '-'*10,"\nSocial Tags from Open Calais\n",'-'*10
    for tn, uri in oc.tagsFromRdf(ft_graph):
        sys.stdout.writelines([str(tn).ljust(35), str(uri), '\n'])
        sys.stdout.flush()
    return 0
    #- end opencalais()

def main(argv=None):
    global api_key
    if argv is None:
        argv = sys.argv[1:]
    if api_key == "XXX":
        sys.stderr.write("You need to register for an Open Calaise API key and configure it in config.py\n")
        sys.stderr.flush()
        return 0
    try:
        try:
            opts, args = getopt.getopt(argv, "h", ["help"])
        except getopt.error as msg:
            raise Usage(msg)
        for o, a in opts:
            if (o in ['-h', '--help']):
                # print help and exit
                sys.stdout.write(__doc__)
                sys.stdout.flush()
                return 0
            
        opencalaistags(opts, args)

    except Usage, err:
        sys.stderr.writelines([str(err.msg)+'\n', "for help use --help\n"])
        sys.stderr.flush()
        return 2
    

if __name__ == '__main__':        
    sys.exit(main())
