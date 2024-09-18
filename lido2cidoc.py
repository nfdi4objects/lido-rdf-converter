import xml.dom.pulldom as PD
import xml.etree.ElementTree as ET
import tools as tools
import xml.dom.minidom as MD
import hashlib
import json

lidoSchemaURI = 'http://www.lido-schema.org'
lidoSchemaXSD = 'http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd'
lidoSchemaXSI = 'http://www.w3.org/2001/XMLSchema-instance'
gmlSchemaURI = 'http://www.opengis.net/gml'
skosSchemaURL = 'http://www.w3.org/2004/02/skos/core'
oaiSchemaURL = 'http://www.openarchives.org/OAI/2.0/'
xmlnsURI = 'http://www.w3.org/XML/1998/namespace'
lidoNS = {'lido': lidoSchemaURI, 'gml': gmlSchemaURI, 'skos': skosSchemaURL}



def lidoXPath(elem, path):
    return elem.xpath(path,namespaces=lidoNS)

def lidoExpandNS(s):
    return s.replace('lido:', f'{{{lidoSchemaURI}}}')

def lidoCompressNS(s):
    return s.replace(f'{{{lidoSchemaURI}}}','lido:')


def md5Hash(s):
    #return s
    return hashlib.md5(s.encode()).hexdigest()


def MAPPING_FILE(): return 'lido_1.0_to_CIDOC_6.0.x3ml'


DOMAIN_PATH = './domain/source_node'
DOMAIN_TYPE = './domain/target_node/entity/type'
DOMAIN_DST = './domain/target_node/if/or/if/equals'

PATH_SRR = './path/source_relation/relation'
PATH_TRR = './path/target_relation/relationship'
PATH_TRE = './path/target_relation/if/or/if/equals'

RANGE_SN = './range/source_node'
RANGE_ENTT = './range/target_node/entity'
RANGE_TYPE = './range/target_node/entity/type'

COLLECTION_ID_TAG = 'cID'
COLLECTION_TAG = 'collection'
PATH_ID_TAG = 'lidoPath'


class lxpath():
    '''Wrapper for lidoXPath'''
    def __init__(self, tag):
        self.tag = tag

    def firstId(self, elem):
        '''Returns the first id'''
        if not self.tag: return elem.text
        if iDs := lidoXPath(elem, f"./{self.tag}/text()"):
            return iDs[0]

    def children(self, elem):
        '''Retruns all child elements'''
        if not self.tag: return [elem]
        return lidoXPath(elem, f"./{self.tag}")


'''Mapping lido tags to its ID tags (lxpath)'''
LIDO_ID_MAP = { 
    'lido:lido':lxpath('lido:lidoRecID'),
    'lido:event': lxpath('lido:eventID'),
    'lido:eventType': lxpath('lido:eventID'),
    'lido:actor': lxpath('lido:actorID'),
    'lido:category': lxpath('lido:conceptID'),
    'lido:repositorySet': lxpath('lido:workID'),
    'lido:place': lxpath('lido:placeID'),
    'lido:namePlaceSet': lxpath('lido:appellationValue'),
    'lido:subjectConcept': lxpath('lido:conceptID'),
    'lido:recordWrap': lxpath('lido:recordID'),
    'lido:object': lxpath('lido:objectID'),
    'lido:recordType': lxpath('lido:conceptID'),
    'lido:rightsHolder': lxpath('lido:legalBodyID'),
    'lido:repositoryName': lxpath('lido:legalBodyID'),
    'lido:measurementType': lxpath(''),
    'lido:appellationValue': lxpath(''),
    'lido:resourceSet': lxpath('lido:resourceID')}

'''Valid Lido ID type URIs'''
LIDO_ID_TYPE_URIS = ('http://terminology.lido-schema.org/lido00099', 'http://terminology.lido-schema.org/identifier_type/uri','uri')

'''Valid Lido type attributes'''
LIDO_TYPE_ATTR = lidoExpandNS('lido:type')
XML_LANG_ATTR = f'{{http://www.w3.org/XML/1998/namespace}}lang'



def notNone(*args) -> bool:
    '''Tests all args to not None'''
    return not any(x is None for x in args)


def executeS(fun, x, default=None):
    '''Applies a function on a valid argument'''
    return fun(x) if notNone(x) else default


def isValidType(elem: ET.Element) -> bool:
    '''Tests for valid lido type attribute'''
    return True 


def getIDs(elem):
    '''Returns all texts from valid Id elements'''
    validItems = filter(isValidType, getIdElements(elem))
    return list(map(lambda x: (x.text), validItems))


def getIdElements(elem):
    '''Returns all ID child elements'''
    tag = lidoCompressNS(elem.tag)
    return executeS(lambda x: x.children(elem), LIDO_ID_MAP.get(tag), [])


def findVar(elem: ET.Element) -> str | None:
    return executeS(lambda x: x.get('variable', ''), elem.find(RANGE_ENTT+"[@variable]"), '')


def str2bool(v) -> bool:
    return v.lower() in ("yes", "true", "t", "1")


def skipped(elem: ET.Element) -> bool:
    return str2bool(elem.get('skip', 'false'))


Attributes = dict

def fullLidoPath(elem):
    '''Return the full lido path of an element'''
    tags = [elem.tag.replace(f'{{{lidoSchemaURI}}}','')]
    if tags[0] != 'lido':
        parent = elem.getparent()
        if notNone(parent):
            tags = fullLidoPath(parent) + tags
    return tags

def getLidoInfo(elem,i):  
    if ids := getIDs(elem):
       mode = 'lidoID'
       id = ids[0]
    else:
       mode = 'path'
       id = '/'.join(fullLidoPath(elem)+[str(i)])
    return {'id':id, 'text':elem.text,'mode':mode}

class ExP:
    '''Linking a XML path to a entity label'''

    def __init__(self, pathStr: str, typeStr: str, varStr: str = ''):
        self.path: str = pathStr
        self.entity = typeStr
        self.var = varStr

    def isRoot(self):
        return self.path.startswith('//')

    def toDict(self):
        return {'path':self.path.strip('/'), 'entity':self.entity,'var':self.var,'isRoot':self.isRoot(), 'isLiteral':self.isLiteral()}
    
    def __str__(self):
        return f"{self.path}|{self.entity}"

    def isLiteral(self):
        return self.entity.startswith('http')
    
    def classLabel(self):
        return self.entity.split(':')[-1]

    def sPath(self):
        return self.path.replace('lido:', '')

    def elements(self,root):
        xpath = f"." if self.isRoot() else f".//{self.path}"
        return lidoXPath(root,xpath) 

def stripPath(link: ExP, txt: str) -> str:
    return txt.removeprefix(link.path)


class Condition():
    def __init__(self):
        self.access = ''
        self.values = set()

    def toDict(self):
        if self.values:
            return {'access':self.access, 'values':[str(x) for x in self.values]}
        return {}

    def add(self, path, value):
        self.access = path
        self.values.add(value)

    def isValid(self, elem) -> bool:
        if self.values:
            if self.access.endswith('/text()'):
                pathValue = lidoXPath(elem, f"./{self.access}")
                if self.values.intersection(pathValue):
                    return True
            else:
                # assume path as an attribute label
                attrName = lidoExpandNS(self.access)
                attrValue = elem.get(attrName, '')
                if attrValue in self.values:
                    return True
            return False
        return True

class PO():
    def __init__(self, p: ExP, o: ExP ):
        self.P = p
        self.O = o
        self.intermediates = []
        self.condition = Condition()

    def toDict(self):
        return {'P':self.P.toDict(), 'O':self.O.toDict(), 'condition':self.condition.toDict()}

    def __str__(self):
        return f"{self.P} -> {self.O}"
    
    def isValid(self,elem) : return self.condition.isValid(elem)

    def getData(self, root):
        data = [getLidoInfo(elem,i) for i,elem in enumerate(self.O.elements(root))]
        return {'P':self.P.toDict(),'O':self.O.toDict(), 'data':data, 'isValid':self.isValid(root)}


class Mapping:
    def __init__(self, s:ExP, n=0):
        self.S = s
        self.n = n
        self.condition = Condition()
        self.POs = []

    def isValid(self,elem) : return self.condition.isValid(elem)

    def toDict(self):
        return {'S':self.S.toDict(), 'POs':[po.toDict() for po in self.POs], 'condition':self.condition.toDict(),'n':self.n}

    def getSData(self, elem, i):
        info = getLidoInfo(elem,i)
        poData = [po.getData(elem) for po in self.POs]
        return {'S':self.S.toDict(), 'info':info, 'PO':poData, 'valid':self.isValid(elem)}
    
    def getData(self, root):
        return [self.getSData(elemS,i) for i,elemS in enumerate(self.S.elements(root))]


    def __str__(self):
        poStr ='\n'.join([f"\t{x}" for x in self.POs])
        return f"{self.S}:\n{poStr}"
    
    def addPO(self,po:PO):
        self.POs.append(po)

    def addIntermediate(self, intermediate):
        if intermediate:
            self.intermediates.append(intermediate)


Mappings = list[Mapping]


def fix(txt) -> str: 
    return tools.fixSC(txt).strip()

def getElemText(elem) -> str:
    return fix(elem.text)

def getElemTextL(elem) -> str:
    txt = getElemText(elem)
    if lang := elem.attrib.get(XML_LANG_ATTR,''):
        txt = f"{txt} ({lang})" 
    return txt

def getTextAndTerms(elem):
    attrs = {}
    if terms := [getElemTextL(x) for x in lidoXPath(elem, './lido:term')]:
        attrs['P3_has_note'] = terms
    if text := elem.findtext('.', default='').strip():
        attrs['P90_has_value'] = fix(text)
    return attrs

def makeSerial(attibutes):
    ids = [attibutes.get(COLLECTION_TAG, ''), attibutes.get(COLLECTION_ID_TAG, ''), attibutes.get(PATH_ID_TAG, '')]
    return  '-'.join(ids)

def makeHashID(attibutes):
    return  md5Hash(makeSerial(attibutes))

def makeAttrs(link: ExP, elem: ET.Element, attibutes: Attributes = Attributes(),**kw) -> str:
    resultAttrs = {}
    if not link.isLiteral():
        resultAttrs = getTextAndTerms(elem)
        resultAttrs[COLLECTION_TAG] = attibutes.get(COLLECTION_TAG, '')
    return resultAttrs

def makeLink(pathElem: ET.Element, typeElem: ET.Element, varStr: str = '') -> ExP | None:
    if notNone(pathElem, typeElem):
        pathText = pathElem.text.strip()
        typeText = typeElem.text.strip()
        if typeText and pathText:
            return ExP(pathText, typeText, varStr)


def mappingsFromEvents(events: PD.DOMEventStream) -> Mappings:
    '''Reads x3ml mapping nodes from an event stream'''
    mappings = []
    nodeIndex = 0
    for (event, node) in events:
        if event == "START_ELEMENT":
            if node.tagName == 'mapping':
                events.expandNode(node)
                if not str2bool(node.getAttribute('skip')):
                    mappings += mappingsFromNode(node, nodeIndex)
                    nodeIndex += 1
    return mappings


def mappingsFromNode(mappingNode, nodeIndex=0) -> Mappings:
    '''Reads single mappings from an x3ml mapping node'''
    mappings = []
    mappingElem = ET.fromstring(mappingNode.toxml())
    if tS := makeLink(mappingElem.find(DOMAIN_PATH), mappingElem.find(DOMAIN_TYPE)):
        mapping = Mapping(tS,nodeIndex)
        # Find domain conditions
        for el in mappingElem.findall(DOMAIN_DST):
            mapping.condition.add(stripPath(tS, el.text), el.get('value'))
        for linkElem in mappingElem.findall('./link'):
            if not skipped(linkElem):
                if tP := makeLink(linkElem.find(PATH_SRR), linkElem.find(PATH_TRR)):
                    varStr = findVar(linkElem)
                    if tO := makeLink(linkElem.find(RANGE_SN), linkElem.find(RANGE_TYPE), varStr):
                        po = PO(tP, tO)
                        for el in linkElem.findall(PATH_TRE):
                            po.condition.add(stripPath(tO, el.text), el.get('value'))
                        mapping.addPO(po)
        mappings.append(mapping)
    return mappings


def getMapping(fname: str = MAPPING_FILE()) -> Mappings | None:
    '''Returns all mappings from a file'''
    with open(fname, 'r') as f:
        events = PD.parse(f)
        return mappingsFromEvents(events)


if __name__ == "__main__":
    for t in getMapping():
        print(json.dumps(t.toDict(),indent=3))