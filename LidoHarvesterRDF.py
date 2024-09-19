import urllib.request as ULR
import urllib.error as ULE
import lido2cidoc as L2C
from lxml import etree
import rdflib as RF

# General used namespaces
ECRM = RF.Namespace("http://erlangen-crm.org/170309/")
BN = RF.Namespace('#')

def makeERM_URI(s):
    '''Returns URI' like e.g. crm:Enn_cccc'''
    rightToken = s.split(':')[-1]
    return ECRM[rightToken]

def fixSC(s: str):
    '''Fix special characters'''
    if s!= None:
        return s.replace("\"","\\\"").replace("\'","\\\'")
    return ""

def deep_get(d, keys):
    if not keys or d is None:
        return d
    return deep_get(d.get(keys[0]), keys[1:])

class LidoHarvesterRDF():
    def __init__(self, mappings):
        self.mappings = mappings
        self.graph = RF.Graph()
        self.graph.bind("ecrm", ECRM)
        self.graph.bind("bn", BN)

    def processURL(self, url:str):
        '''Transfers all lido elements'''
        headers = {'User-Agent': 'pyoaiharvester/3.0','Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
        req = ULR.Request(url,headers=headers)
        numProcessed = 0
        token = ''
        lidoTag = f'{{{L2C.lidoSchemaURI}}}lido'
        resumTag = f'{{{L2C.oaiSchemaURL}}}resumptionToken'
        tag = (lidoTag,resumTag,'error')
        try:
            with ULR.urlopen(req) as response:
                for _, elem in etree.iterparse(response, events=("end",),tag=tag,encoding='UTF-8',remove_blank_text=True):
                    if resumTag == elem.tag:
                        token = elem.text
                    elif 'error' in elem.tag :
                        print('error',elem.tag,elem.text)
                    elif elem.tag == lidoTag:
                        self.process(elem,index=numProcessed)
                        numProcessed += 1
                    else:
                       print('unexpeced :-(')
                       elem.clear()
        except (ULR.HTTPError,ULE.URLError) as exception:
            print(exception)
        return numProcessed,token

    def result(self):
        return self.graph

    def process(self, elemRoot,**kw):
        '''Create graph LIDO root element w.r.t given mappings'''
        recId = ' '.join(L2C.lidoXPath(elemRoot,f"./lido:lidoRecID/text()"))
        for mData in [m.getData(elemRoot) for m in self.mappings]:
            for i,elemData in enumerate(mData):
                if elemData.get('valid'):
                    addSPO(self.graph, elemData,index=i, recId=recId)

def addSPO(graph, elemData, **kw):
    entity_S = deep_get(elemData,['S','entity'])
    id_S = deep_get(elemData,['info','id'])
    mode = deep_get(elemData,['info','mode'])
    recId = kw.get('recId','')
    key_S = id_S + recId
    S = BN[f"{L2C.md5Hash(key_S)}"]
    graph.add((S, RF.RDF.type, makeERM_URI(entity_S)))
    if mode == 'lidoID':
        graph.add((S, ECRM['P48_has_preferred_identifier'], RF.Literal(id_S)))

    for i,po in enumerate(deep_get(elemData,['PO'])):
        if po.get('isValid'):
            entity_P = deep_get(po,['P','entity'])
            entity_O = deep_get(po,['O','entity'])
            isLiteral = deep_get(po,['O','isLiteral'])
            for po_data in po.get('data'):
                text = fixSC(po_data.get('text'))
                if isLiteral:
                    if text:
                        graph.add((S, makeERM_URI('P90_has_value'), RF.Literal(text)))
                else:
                    id_O = po_data.get('id')
                    key_O = id_O + recId + id_S + str(i)
                    O = BN[f"{L2C.md5Hash(key_O)}"]
                    graph.add((O, RF.RDF.type, makeERM_URI(entity_O)))
                    if text:
                        graph.add((O, makeERM_URI('P90_has_value'), RF.Literal(text)))
                    graph.add((S, makeERM_URI(entity_P), O))


