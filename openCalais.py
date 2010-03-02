"""Module for communicating with OpenCalais Web-Service.

Created on Mar 2, 2010
@author: John Harrison
"""

import urllib, urllib2, socket, uuid

from rdflib import StringInputSource, URIRef
from rdflib import ConjunctiveGraph as Graph

from warnings import filterwarnings
filterwarnings('ignore', 'the sets module is deprecated',  DeprecationWarning, 'rdflib')


class OpenCalaisService(object):

    namespaces = {'rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         ,'c': "http://s.opencalais.com/1/pred/"
         }
    
    def __init__(self, api_url="http://api1.opencalais.com/enlighten/rest/", api_key="xxx", app_name="Semantic PDF Open Calais Tagger"):
        object.__init__(self)
        self.api_url = api_url
        self.api_key = api_key
        self.app_name = app_name

    def post_data(self, myUrl, postdata, tries=1, timeout=20):
        oldtimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        req = urllib2.Request(url=myUrl)
        for x in range(tries):
            try:
                f = urllib2.urlopen(req, postdata)
            except (urllib2.URLError):
                # problem accessing remote service
                continue
            except httplib.BadStatusLine:
                # response broken
                time.sleep(0.5)
                continue
            else:
                data = f.read()
                f.close()
                return data
        
        socket.setdefaulttimeout(oldtimeout)
        return None


    def rdfFromText(self, text):
        """Take text, return an RDF graph."""
        postdata = {}
        postdata['licenseID'] = self.api_key
        postdata['paramsXML'] = ' '.join(['<c:params xmlns:c="http://s.opencalais.com/1/pred/"'
                ,'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                ,'<c:processingDirectives c:contentType="text/raw"'
                ,'c:outputFormat="text/xml"'
                ,'c:enableMetadataType="GenericRelations,SocialTags">'
                ,'</c:processingDirectives>'
                ,'<c:userDirectives c:allowDistribution="false"'
                ,'c:allowSearch="false"'
                ,'c:externalID="{0}"'.format(uuid.uuid4()) 
                ,'c:submitter="{0}">'.format(self.app_name)
                ,'</c:userDirectives>'
                ,'<c:externalMetadata></c:externalMetadata>'
                ,'</c:params>'])

        postdata['content'] = text

        poststring = urllib.urlencode(postdata)
        data = self.post_data("{0}".format(self.api_url), poststring, timeout=60*5)
        graph = Graph()
        inpt = StringInputSource(data)
        try: graph.parse(inpt, 'xml')
        except:
            print data
            raise
        return graph

    def entitiesFromRdf(self, graph):
        """Use SPARQL to select entities and return them."""
        return [str(x) for x in graph.query('SELECT ?e WHERE { ?x c:detection ?d . ?x c:exact ?e }', initNs=self.namespaces).result]

    def tagsFromRdf(self, graph):
        """Use SPARQL to select semantic tags and return them."""
        tags = graph.query('SELECT ?tn ?x WHERE { ?x c:socialtag ?st . ?x c:name ?tn }', initNs=self.namespaces).result
        return tags

    def entitiesFromText(self, text):
        graph = self.rdfFromText(text)
        return entitiesFromRdf(graph)

    def tagsFromText(self, text):
        graph = self.rdfFromText(text)
        return tagsFromRdf(graph)
        