#!.venv/bin/python
from lxml import etree
import sys
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, field

lidoSchemaURI = 'http://www.lido-schema.org'
lidoSchemaXSD = 'http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd'
lidoSchemaXSI = 'http://www.w3.org/2001/XMLSchema-instance'
gmlSchemaURI = 'http://www.opengis.net/gml'
skosSchemaURL = 'http://www.w3.org/2004/02/skos/core#'
oaiSchemaURL = 'http://www.openarchives.org/OAI/2.0/'
xmlnsURI = 'http://www.w3.org/XML/1998/namespace'
suported_NS = {'lido': lidoSchemaURI, 'gml': gmlSchemaURI, 'skos': skosSchemaURL, 'xml':xmlnsURI}


def lidoExpandNS(s):
    '''Expands lido: prefix to full namespace'''
    return s.replace('lido:', f'{{{lidoSchemaURI}}}').replace('skos:', f'{{{skosSchemaURL}}}').replace('gml:', f'{{{gmlSchemaURI}}}')


def lidoCompressNS(s):
    '''Compresses full namespace to lido: prefix'''
    return s.replace(f'{{{lidoSchemaURI}}}', 'lido:')


def md5Hash(s):
    '''Returns the MD5 hash of a string'''
    return hashlib.md5(s.encode()).hexdigest()

def xpath_lido(elem: etree.Element, path: str) -> list:
    '''Wrapper for xpath with Lido namespaces'''
    elems = elem.xpath(path, namespaces=suported_NS)
    if '@' in path and not elem.text: 
        attr_name = lidoExpandNS(path.split('[@')[-1].strip(']'))
        for elem in elems:
            elem.text = elem.get(attr_name)
    return elems



DOMAIN_PATH = './domain/source_node'
DOMAIN_TYPE = './domain/target_node/entity/type'
DOMAIN_COND = './domain/target_node/if/or/if/equals'

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

    def __init__(self, tag=None):
        self.tag = tag

    def children(self, elem):
        '''Returns all child elements'''
        if not self.tag:
            return [elem]
        return xpath_lido(elem, f"./{self.tag}")

    def firstId(self, elem):
        if ch := self.children(elem):
            return ch[0]


'''Mapping lido tags to its ID tags (lxpath)'''
LIDO_ID_MAP = {
    'lido:lido': lxpath('lido:lidoRecID'),
    'lido:event': lxpath('lido:eventID'),
    'lido:eventType': lxpath('lido:eventID'),
    'lido:actor': lxpath('lido:actorID'),
    'lido:category': lxpath('lido:conceptID'),
    'lido:repositorySet': lxpath('lido:workID'),
    'lido:place': [lxpath('lido:placeID'), lxpath('lido:namePlaceSet/lido:appellationValue')],
    'lido:namePlaceSet': lxpath('lido:appellationValue'),
    'lido:subjectConcept': lxpath('lido:conceptID'),
    'lido:recordWrap': lxpath('lido:recordID'),
    'lido:object': lxpath('lido:objectID'),
    'lido:recordType': lxpath('lido:conceptID'),
    'lido:rightsHolder': lxpath('lido:legalBodyID'),
    'lido:resourceSet': lxpath('lido:resourceID'),
    'lido:repositoryName': lxpath('lido:legalBodyID')
}

'''Valid Lido ID type URIs'''
LIDO_ID_TYPE_URIS = ('http://terminology.lido-schema.org/lido00099',
                     'http://terminology.lido-schema.org/identifier_type/uri', 'uri')

'''Valid Lido type attributes'''
LIDO_TYPE_ATTR = lidoExpandNS('lido:type')
XML_LANG_ATTR = '{{http://www.w3.org/XML/1998/namespace}}lang'


def notNone(*args) -> bool:
    '''Tests all args to not None'''
    return not any(x is None for x in args)


def executeS(fun, x, default=None):
    '''Applies a function on a valid argument'''
    return fun(x) if notNone(x) else default


def hasText(elem: etree.Element) -> bool:
    return notNone(elem.text)


def getIDs(elem):
    '''Returns all texts from valid Id elements'''
    validItems = filter(hasText, getIdElements(elem))
    return list(map(lambda x: x.text, validItems))


def getIdElements(elem):
    '''Returns all ID child elements'''
    tag = lidoCompressNS(elem.tag)
    if lxp := LIDO_ID_MAP.get(tag):
        if isinstance(lxp, lxpath):
            return lxp.children(elem)
        if isinstance(lxp, list):
            for l in lxp:
                if ch := l.children(elem):
                    return ch
    return []


def findVar(elem: etree.Element) -> str | None:
    return executeS(lambda x: x.get('variable', ''), elem.find(RANGE_ENTT + "[@variable]"), '')


def str2bool(bstr) -> bool:
    return bstr.lower() in ("yes", "true", "t", "1")


def skipped(elem: etree.Element) -> bool:
    return str2bool(elem.get('skip', 'false'))


def root_path_as_list(elem):
    '''Return the full lido path of an element'''
    tags = elem.tag.replace(f'{{{lidoSchemaURI}}}', '')
    parent = elem.getparent()
    if notNone(parent):
        tags = root_path_as_list(parent) + '/' + tags
    return tags


@dataclass
class Info:
    '''Information about an element'''
    text: str = ''
    attrib: dict = None
    mode: str = ''
    id: str = ''
    index: int = -1
    lang: str = ''


def getLidoInfo(elem, i):
    '''Returns Info for an element'''
    text = elem.text.strip() if elem.text else ''
    lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang','') 
    info = Info(text=text, attrib=elem.attrib, index=i,lang=lang)
    if rpl := getIDs(elem):
        info.mode = 'lidoID'
        info.id = rpl[0]
    else:
        info.mode = 'path'
        info.id = root_path_as_list(elem) + '/'+str(i)
    return info


@dataclass
class LinkEP:
    '''Linking of path and entity'''
    path: str = ''
    entity: str = ''
    var: str = ''

    def isRoot(self):
        '''Tests if the path is the root element'''
        return self.path.startswith('//')

    def isLiteral(self):
        '''Tests if the entity is a literal'''
        return self.entity.startswith('http')

    def subs(self, elem) -> list:
        '''Returns all subelements for the given path'''
        xpath = "." if self.isRoot() else f".//{self.path}"
        return xpath_lido(elem, xpath)


def stripPath(link: LinkEP, txt: str) -> str:
    return txt.removeprefix(link.path)


@dataclass
class Condition():
    '''Condition for filtering elements'''
    access: str = ''
    values: set = None

    def add(self, path, value):
        if self.values is None:
            self.values = set()
        self.access = path
        self.values.add(value)

    def isValid(self, elem) -> bool:
        if self.values:
            if self.access.endswith('/text()'):
                pathValues = elem.xpath(f"./{self.access}", namespaces=suported_NS)
                if self.values.intersection(pathValues):
                    return True
            else:
                # assume path as an attribute label
                attrName = lidoExpandNS(self.access)
                attrValue = elem.get(attrName, '')
                if attrValue in self.values:
                    return True
            return False
        return True


@dataclass
class PO_Data:
    '''Data for a single PO'''
    P: LinkEP = None
    O: LinkEP = None
    infos: list = None
    valid: bool = False


@dataclass
class PO():
    '''Mapping for a single PO'''
    P: LinkEP = None
    O: LinkEP = None
    condition: Condition = field(default_factory=Condition)

    def isValid(self, elem):
        return self.condition.isValid(elem)

    def evaluate(self, elem):
        infos = [getLidoInfo(e, i) for i, e in enumerate(self.O.subs(elem))]
        return PO_Data(P=self.P, O=self.O, infos=infos, valid=self.isValid(elem))


@dataclass
class Mapping_Data:
    '''Data for a single mapping'''
    S: LinkEP = None
    POs: list = None
    valid: bool = False
    info: Info = None


@dataclass
class Mapping:
    '''Mapping for a single S with multiple POs'''
    S: LinkEP = None
    POs: list = field(default_factory=list)
    condition: Condition = field(default_factory=Condition)
    intermediates: list = field(default_factory=list)

    def isValid(self, elem):
        return self.condition.isValid(elem)

    def evaluate_n(self, elem, i):
        POs = [po.evaluate(elem) for po in self.POs]
        return Mapping_Data(S=self.S, POs=POs, valid=self.isValid(elem), info=getLidoInfo(elem, i))

    def evaluate(self, elem):
        return [self.evaluate_n(e, i) for i, e in enumerate(self.S.subs(elem))]

    def addPO(self, po: PO):
        self.POs.append(po)

    def addIntermediate(self, intermediate):
        if intermediate:
            self.intermediates.append(intermediate)


Mappings = list[Mapping]
'''List of mappings'''


def makeExP(pathElem: etree.Element, typeElem: etree.Element, varStr: str = '') -> LinkEP | None:
    '''Creates an LinkEP from path and type elements'''
    if notNone(pathElem, typeElem):
        pathText = pathElem.text
        typeText = typeElem.text
        if typeText and pathText:
            return LinkEP(pathText.strip(), typeText.strip(), varStr)


def mappingsFromNode(mappingElem) -> Mappings:
    '''Reads single mappings from an x3ml mapping node'''
    mappings = []
    if sExP := makeExP(mappingElem.find(DOMAIN_PATH), mappingElem.find(DOMAIN_TYPE)):
        mapping = Mapping(sExP)
        # Find domain conditions
        for elemS in mappingElem.findall(DOMAIN_COND):
            mapping.condition.add(elemS.text, elemS.get('value'))
        for linkElem in mappingElem.findall('./link'):
            if not skipped(linkElem):
                if pExP := makeExP(linkElem.find(PATH_SRR), linkElem.find(PATH_TRR)):
                    varStr = findVar(linkElem)
                    if oExP := makeExP(linkElem.find(RANGE_SN), linkElem.find(RANGE_TYPE), varStr):
                        po = PO(P=pExP, O=oExP)
                        for elemO in linkElem.findall(PATH_TRE):
                            po.condition.add(elemO.text, elemO.get('value'))
                        mapping.addPO(po)
        mappings.append(mapping)
    return mappings


def mappings_from_str(xmlStr: str) -> Mappings | None:
    '''Returns all mappings from a string'''
    mappings = []
    parser = etree.XMLPullParser(events=("end",), tag=(
        'mapping'), encoding='UTF-8', remove_blank_text=True)
    parser.feed(xmlStr)
    for _, elem in parser.read_events():
        if not str2bool(elem.get('skip', 'false')):
            mappings += mappingsFromNode(elem)
    return mappings


def mappings_from_file(fileName: str) -> Mappings | None:
    '''Returns all mappings from a file'''
    s = Path(fileName).read_text(encoding='UTF-8')
    return mappings_from_str(s)


if __name__ == "__main__":
    args = sys.argv[1:]
    mappings = args[0] if len(args) == 1 else "defaultMapping.x3ml"
    for t in mappings_from_file(mappings):
        print(json.dumps(t.toDict(), indent=3))
