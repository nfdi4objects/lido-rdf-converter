import urllib.request as ULR
import x3ml as L2C
from lxml import etree
import rdflib as RF

# General used namespaces
CRM = RF.Namespace("http://www.cidoc-crm.org/cidoc-crm/")
BN = RF.Namespace('#')

def makeERM_URI(s):
    '''Returns URI' like e.g. crm:Enn_cccc'''
    rightToken = s.split(':')[-1]
    return CRM[rightToken]

def fixSC(s: str):
    '''Fix special characters'''
    if s!= None:
        return s.replace("\"","\\\"").replace("\'","\\\'")
    return ""

def deep_get(d, keys):
    if not keys or d is None:
        return d
    return deep_get(d.get(keys[0]), keys[1:])

class LidoRDFConverter():
    def __init__(self, mappings):
        self.mappings = L2C.getMapping(mappings)
        self.graph = RF.Graph()
        self.graph.bind("crm", CRM)
        self.graph.bind("bn", BN)

    def processURL(self, url:str):
        '''Transfers all LIDO elements'''
        headers = {'User-Agent': 'pyoaiharvester/3.0','Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
        req = ULR.Request(url,headers=headers)
        self.numProcessed = 0
        with ULR.urlopen(req) as response:
            return self.processXML(response)

    def processXML(self, xml):
        lidoTag = f'{{{L2C.lidoSchemaURI}}}lido'
        resumTag = f'{{{L2C.oaiSchemaURL}}}resumptionToken'
        tag = (lidoTag,resumTag,'error')
        for _, elem in etree.iterparse(xml, events=("end",),tag=tag,encoding='UTF-8',remove_blank_text=True):
            if resumTag == elem.tag:
                pass
            elif 'error' in elem.tag :
                print('error',elem.tag,elem.text)
            elif elem.tag == lidoTag:
                self.process(elem)
            else:
               print('unexpeced :-(')
               elem.clear()

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
        graph.add((S, CRM['P48_has_preferred_identifier'], RF.Literal(id_S)))

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
                    isURI_Id = text.startswith('http') and entity_O=="crm:E42_Identifier"
                    id_O = po_data.get('id')
                    key_O = id_O + recId + id_S + str(i)
                    if id_O.startswith('http') or isURI_Id:
                        graph.add((S, makeERM_URI(entity_P), RF.Literal(text)))
                    else:
                        O = BN[f"{L2C.md5Hash(key_O)}"]
                        graph.add((O, RF.RDF.type, makeERM_URI(entity_O)))
                        if text:
                            graph.add((O, makeERM_URI('P90_has_value'), RF.Literal(text)))
                        graph.add((S, makeERM_URI(entity_P), O))


