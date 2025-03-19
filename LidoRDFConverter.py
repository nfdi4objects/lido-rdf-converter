import time
import urllib.request as ULR
import urllib.parse as ULP
import x3ml as L2C
from lxml import etree
import rdflib as RF
import os,shutil

# General used namespaces
CRM = RF.Namespace("http://www.cidoc-crm.org/cidoc-crm/")
N4O = RF.Namespace('http://graph.nfdi4objects.net/id/')
LIDO_TAG = f'{{{L2C.lidoSchemaURI}}}lido'
RESUMPTION_TAG = f'{{{L2C.oaiSchemaURL}}}resumptionToken'

def makeERM_URI(s):
    '''Returns URI' like e.g. crm:Enn_cccc'''
    rightToken = s.split(':')[-1]
    return CRM[rightToken]

def deep_get(d, keys):
    if not keys or d is None:
        return d
    return deep_get(d.get(keys[0]), keys[1:])

def isURI(s):
    return ULP.urlparse(s).scheme.startswith('http')
 
def safeURI(s):
    if isURI(s):
        return ULP.quote(s).replace('%3A', ':')
    return s

def oaiRequest(serverURI:str, command:str)->ULR.Request|None:
    """Primary function for requesting OAI-PMH data from repository,
       checking for errors, handling possible compression and returning
       the XML string to the rest of the script for writing to a file."""

    global N_RECOVERIES, MAX_RECOVERIES
    requestStr = serverURI + f'?verb={command}'
    headers = {'User-Agent': 'pyoaiharvester/3.0','Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
    try:
        return ULR.Request(requestStr, headers=headers)
    except ULR.HTTPError as ex_value:
        print('Http Error:',ex_value)
        if ex_value.code == 503:
            retry_wait = int(ex_value.hdrs.get("Retry-After", "-1"))
            if retry_wait < 0:
                return None
            print(f'Waiting {retry_wait} seconds')
            time.sleep(retry_wait)
            return oaiRequest(serverURI, command)
        if N_RECOVERIES < MAX_RECOVERIES:
            N_RECOVERIES += 1
            return oaiRequest(serverURI, command)
        return None

def toBuffer(req:ULR.Request,oaiFile)->str:
    '''Buffer q request in a file'''
    with ULR.urlopen(req) as response, open(oaiFile,'w') as f:
        answer = response.read()
        f.write(answer.decode('utf-8'))
        return oaiFile
    
def makeResultGraph():
    g = RF.Graph()
    g.bind("crm", CRM)
    g.bind("n4o", N4O)
    return g

def makeCleanSubDir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

class LidoRDFConverter():
    def __init__(self, filePath):
        self.mappings = L2C.getMapping(filePath) if filePath else []

    @classmethod
    def from_str(cls, mappingStr):
        obj = cls('')
        obj.mappings = L2C.getMappingS(mappingStr)
        return obj

    def processURL(self, url:str,**kw):
        rdfFolder = kw.get('rdfFolder','data')
        makeCleanSubDir(rdfFolder)
        def serialize(g,t):
            g.serialize(destination=f'./{rdfFolder}/{t}.ttl', format='ttl')
            #print(f'{t}.ttl')

        '''Transfers all LIDO elements'''
        headers = {'User-Agent': 'pyoaiharvester/3.0','Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
        req = ULR.Request(url, headers=headers)
        self.numProcessed = 0
        if url.startswith('http'):
            req = oaiRequest(url, f'ListRecords&metadataPrefix=lido')
            while req:
                bFile = toBuffer(req,'oai_buffer.xml')
                g, rsToken =self.parse_file(bFile,processor=serialize)
                if not rsToken:
                    print('No more resumptionToken') 
                    break
                req = oaiRequest(url, f"ListRecords&resumptionToken={rsToken}")
        else:
            with ULR.urlopen(req) as response:
                g , _ = self.parse_file(response)
                return g

 
    def parse_file(self, xmlFile,**kw):
        graph = makeResultGraph()
        processor = kw.get('processor')
        tag = (LIDO_TAG,RESUMPTION_TAG,'error')
        token= None
        for _, elem in etree.iterparse(xmlFile, events=("end",),tag=tag,encoding='UTF-8',remove_blank_text=True):
            token = self.processValidElement(graph, elem)
        if processor:
            processor(graph,token)
        return graph, token

    def parse_string(self, xmlStr):
        graph = makeResultGraph()
        tag = (LIDO_TAG)
        parser = etree.XMLPullParser(events=("end",),tag = tag, encoding='UTF-8',remove_blank_text=True)
        parser.feed(xmlStr)
        for _ , elem in parser.read_events():
            self.processLidoElement(elem,graph)        
        return graph

    def processValidElement(self, graph, elem):
        token = None
        if RESUMPTION_TAG == elem.tag:
            token = elem.text
            print('completeListSize',elem.attrib['completeListSize'])
            print('cursor',elem.attrib['cursor'])
            print('expirationDate',elem.attrib['expirationDate'])
            print('token',token)
        elif 'error' in elem.tag :
            print('error',elem.tag,elem.text)
        elif elem.tag == LIDO_TAG:
            self.processLidoElement(elem,graph)
        else:
           print('unexpeced :-(')
           elem.clear()
        return token

    def processLidoElement(self, elem, g,**kw):
        '''Create graph LIDO root element w.r.t given mappings'''
        recId = ' '.join(L2C.lidoXPath(elem, "./lido:lidoRecID/text()"))
        for data in [m.getData(elem) for m in self.mappings]:
            for i, elemData in enumerate(data):
                if elemData.get('valid'):
                    addSPO(g, elemData,index=i, recId=recId)


def _hash(s):
    return L2C.md5Hash(s)

def makeItem(s,a=''):
    if isURI(s):
        return RF.term.URIRef(s) 
    return N4O[f"{_hash(s + a)}"] #No URI for ID => local ID from path and recID


def addSPO(graph, elemData, **kw):
    entity_S = deep_get(elemData,['S','entity'])
    id_S = safeURI(deep_get(elemData,['info','id']))
    recId = kw.get('recId','')
    j = kw.get('index',0)
    S = makeItem(id_S, recId)
    triples = [(S, RF.RDF.type, makeERM_URI(entity_S))]
    for i,po in enumerate(deep_get(elemData,['PO'])):
        poTriples =  []
        if po.get('isValid'):
            entity_P = deep_get(po,['P','entity'])
            entity_O = deep_get(po,['O','entity'])
            for po_data in po.get('data'):
                if text := po_data.get('text'):
                    if not isURI(text):
                        poTriples.append((S, makeERM_URI('P90_has_value'), RF.Literal(text)))
                    else:
                        text = safeURI(text)
                        isURI_Id = isURI(text) and entity_O=="crm:E42_Identifier"
                        id_O = po_data.get('id')

                        if id_S != id_O:
                            if isURI(id_O) or isURI_Id:
                                O = RF.term.URIRef(text)
                                poTriples.append((S, makeERM_URI(entity_P), O))
                            else:
                                O = makeItem(id_O, recId)
                                poTriples.append((O, RF.RDF.type, makeERM_URI(entity_O)))
                                poTriples.append((O, makeERM_URI('P90_has_value'), RF.Literal(text)))
                                poTriples.append((S, makeERM_URI(entity_P), O))
        if poTriples:
            triples += poTriples
    for t in triples: 
        graph.add(t)

