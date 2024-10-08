import time
import urllib.request as ULR
import urllib.parse
import x3ml as L2C
from lxml import etree
import rdflib as RF
import os,shutil

# General used namespaces
CRM = RF.Namespace("http://www.cidoc-crm.org/cidoc-crm/")
BN = RF.Namespace('http://www.gbv.de/id/')

def makeERM_URI(s):
    '''Returns URI' like e.g. crm:Enn_cccc'''
    rightToken = s.split(':')[-1]
    return CRM[rightToken]

def fixSC(s: str):
    '''Fix special characters'''
    if s!= None:
        return str(s)#s.replace("\"","\\\"").replace("\'","\\\'").replace(",", "%2C")
    return ""

def deep_get(d, keys):
    if not keys or d is None:
        return d
    return deep_get(d.get(keys[0]), keys[1:])

def isURI(s):
    return s.lower().startswith('http')

def safeURI(s):
    if isURI(s):
        return urllib.parse.quote(s).replace('%3A', ':')
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
    
def newGraph():
    g = RF.Graph()
    g.bind("crm", CRM)
    g.bind("bn", BN)
    return g

class LidoRDFConverter():
    def __init__(self, mappings):
        self.mappings = L2C.getMapping(mappings)

    def processURL(self, url:str):
        if os.path.exists('data'):
            shutil.rmtree('data',)
        os.mkdir('data')
        def proc(g,t):
            g.serialize(destination=f'./data/{t}.ttl', format='ttl')
            #print(f'{t}.ttl')
        '''Transfers all LIDO elements'''
        headers = {'User-Agent': 'pyoaiharvester/3.0','Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
        req = ULR.Request(url,headers=headers)
        self.numProcessed = 0
        if url.startswith('http'):
            req = oaiRequest(url, f'ListRecords&metadataPrefix=lido')
            while req:
                bFile = toBuffer(req,'oai_buffer.xml')
                g, rsToken =self.processXML(bFile,processor=proc)
                if not rsToken:
                    print('No more resumptionToken') 
                    break
                req = oaiRequest(url, f"ListRecords&resumptionToken={rsToken}")
        else:
            with ULR.urlopen(req) as response:
                g , _ = self.processXML(response)
                return g

    def processXML(self, xml,**kw):
        g =newGraph()
        lidoTag = f'{{{L2C.lidoSchemaURI}}}lido'
        resumTag = f'{{{L2C.oaiSchemaURL}}}resumptionToken'
        processor = kw.get('processor')
        tag = (lidoTag,resumTag,'error')
        token= None
        for _, elem in etree.iterparse(xml, events=("end",),tag=tag,encoding='UTF-8',remove_blank_text=True):
            if resumTag == elem.tag:
                token = elem.text
                print('completeListSize',elem.attrib['completeListSize'])
                print('cursor',elem.attrib['cursor'])
                print('expirationDate',elem.attrib['expirationDate'])
                print('token',token)
            elif 'error' in elem.tag :
                print('error',elem.tag,elem.text)
            elif elem.tag == lidoTag:
                self.process(elem,g)
            else:
               print('unexpeced :-(')
               elem.clear()
        if processor:
            processor(g,token)
        return g, token

    def process(self, elemRoot,g,**kw):
        '''Create graph LIDO root element w.r.t given mappings'''
        recId = ' '.join(L2C.lidoXPath(elemRoot,f"./lido:lidoRecID/text()"))
        for mData in [m.getData(elemRoot) for m in self.mappings]:
            for i,elemData in enumerate(mData):
                if elemData.get('valid'):
                    addSPO(g, elemData,index=i, recId=recId)


def addSPO(graph, elemData, **kw):
    entity_S = deep_get(elemData,['S','entity'])
    id_S = safeURI(deep_get(elemData,['info','id']))
    mode = deep_get(elemData,['info','mode'])
    recId = kw.get('recId','')
    key_S = id_S + recId
    S = BN[f"{L2C.md5Hash(key_S)}"]
    triples = [(S, RF.RDF.type, makeERM_URI(entity_S))]
    if mode == 'lidoID':
        O =  RF.term.URIRef(id_S) if isURI(id_S) else RF.Literal(id_S)
        triples.append((S, CRM['P48_has_preferred_identifier'], O))
    for i,po in enumerate(deep_get(elemData,['PO'])):
        if po.get('isValid'):
            entity_P = deep_get(po,['P','entity'])
            entity_O = deep_get(po,['O','entity'])
            isLiteral = deep_get(po,['O','isLiteral'])
            for po_data in po.get('data'):
                text = safeURI(str(po_data.get('text')))
                if isLiteral:
                    if text:
                        triples.append((S, makeERM_URI('P90_has_value'), RF.Literal(text)))
                else:
                    isURI_Id = isURI(text) and entity_O=="crm:E42_Identifier"
                    id_O = po_data.get('id')
                    key_O = id_O + recId + id_S + str(i)
                    if isURI(id_O) or isURI_Id:
                        triples.append((S, makeERM_URI(entity_P), RF.term.URIRef(text)))
                    else:
                        O = BN[f"{L2C.md5Hash(key_O)}"]
                        triples.append((O, RF.RDF.type, makeERM_URI(entity_O)))
                        if text:
                            triples.append((O, makeERM_URI('P90_has_value'), RF.Literal(text)))
                        triples.append((S, makeERM_URI(entity_P), O))
    #print(len(triples))
    if len(triples) > 1:
        for t in triples: 
            graph.add(t)

