#!.venv/bin/python
from lxml import etree
import sys
import hashlib
import json
from pathlib import Path

lidoSchemaURI = 'http://www.lido-schema.org'
lidoSchemaXSD = 'http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd'
lidoSchemaXSI = 'http://www.w3.org/2001/XMLSchema-instance'
gmlSchemaURI = 'http://www.opengis.net/gml'
skosSchemaURL = 'http://www.w3.org/2004/02/skos/core'
oaiSchemaURL = 'http://www.openarchives.org/OAI/2.0/'
xmlnsURI = 'http://www.w3.org/XML/1998/namespace'
lidoNS = {'lido': lidoSchemaURI, 'gml': gmlSchemaURI, 'skos': skosSchemaURL}


def xpath_lido(elem: etree.Element, path: str) -> list:
    '''Wrapper for xpath with Lido namespaces'''
    return elem.xpath(path, namespaces=lidoNS)


def lidoExpandNS(s):
    return s.replace('lido:', f'{{{lidoSchemaURI}}}')


def lidoCompressNS(s):
    return s.replace(f'{{{lidoSchemaURI}}}', 'lido:')


def md5Hash(s):
    return hashlib.md5(s.encode()).hexdigest()


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
    'lido:repositoryName': lxpath('lido:legalBodyID'),
    'lido:measurementType': lxpath(),
    'lido:appellationValue': lxpath(),
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


def fullLidoPath(elem):
    '''Return the full lido path of an element'''
    tags = [elem.tag.replace(f'{{{lidoSchemaURI}}}', '')]
    if tags[0] != 'lido':
        parent = elem.getparent()
        if notNone(parent):
            tags = fullLidoPath(parent) + tags
    return tags


class ResultData:
    '''Generic result data class for S, P, O, PO, Mapping'''

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def getLidoInfo(elem, i):
    t = elem.text.strip() if elem.text else ''
    a = elem.attrib
    if ids := getIDs(elem):
        return ResultData(text=t, attrib=a, mode='lidoID', id=ids[0])
    else:
        ids = '/'.join(fullLidoPath(elem) + [str(i)])
        return ResultData(text=t, attrib=a, mode='path', id=ids)


class ExP:
    '''Linking a XML path to a entity label'''

    def __init__(self, path: str, entity: str, var: str = ''):
        self.path: str = path
        self.entity = entity
        self.var = var

    def isRoot(self):
        return self.path.startswith('//')

    def __str__(self):
        return f"{self.path}|{self.entity}"

    def isLiteral(self):
        return self.entity.startswith('http')

    def classLabel(self):
        return self.entity.split(':')[-1]

    def sPath(self):
        return self.path.replace('lido:', '')

    def subs(self, elem) -> list:
        xpath = "." if self.isRoot() else f".//{self.path}"
        return xpath_lido(elem, xpath)


def stripPath(link: ExP, txt: str) -> str:
    return txt.removeprefix(link.path)


class Condition():
    def __init__(self):
        self.access = ''
        self.values = set()

    def toDict(self):
        if self.values:
            return {'access': self.access, 'values': [str(x) for x in self.values]}
        return {}

    def add(self, path, value):
        self.access = path
        self.values.add(value)

    def isValid(self, elem) -> bool:
        if self.values:
            if self.access.endswith('/text()'):
                pathValue = xpath_lido(elem, f"./{self.access}")
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
    def __init__(self, p: ExP, o: ExP):
        self.P = p
        self.O = o
        self.intermediates = []
        self.condition = Condition()

    def __str__(self):
        return f"{self.P} -> {self.O}"

    def isValid(self, elem):
        return self.condition.isValid(elem)

    def evaluate(self, elem):
        data = [getLidoInfo(e, i) for i, e in enumerate(self.O.subs(elem))]
        return ResultData(P=self.P, O=self.O, data=data, valid=self.isValid(elem))


class Mapping:
    def __init__(self, s: ExP, n=0):
        self.S = s
        self.n = n
        self.condition = Condition()
        self.POs = []

    def isValid(self, elem):
        return self.condition.isValid(elem)

    def evaluate_n(self, elem, i):
        POs = [po.evaluate(elem) for po in self.POs]
        return ResultData(S=self.S, POs=POs, valid=self.isValid(elem), info=getLidoInfo(elem, i))

    def evaluate(self, elem):
        return [self.evaluate_n(e, i) for i, e in enumerate(self.S.subs(elem))]

    def __str__(self):
        poStr = '\n'.join([f"\t{x}" for x in self.POs])
        return f"{self.S}:\n{poStr}"

    def addPO(self, po: PO):
        self.POs.append(po)

    def addIntermediate(self, intermediate):
        if intermediate:
            self.intermediates.append(intermediate)


Mappings = list[Mapping]


def makeExP(pathElem: etree.Element, typeElem: etree.Element, varStr: str = '') -> ExP | None:
    if notNone(pathElem, typeElem):
        pathText = pathElem.text
        typeText = typeElem.text
        if typeText and pathText:
            return ExP(pathText.strip(), typeText.strip(), varStr)


def mappingsFromNode(mappingElem) -> Mappings:
    '''Reads single mappings from an x3ml mapping node'''
    mappings = []
    if sExP := makeExP(mappingElem.find(DOMAIN_PATH), mappingElem.find(DOMAIN_TYPE)):
        mapping = Mapping(sExP)
        # Find domain conditions
        for cndElem in mappingElem.findall(DOMAIN_COND):
            mapping.condition.add(
                stripPath(sExP, cndElem.text), cndElem.get('value'))
        for linkElem in mappingElem.findall('./link'):
            if not skipped(linkElem):
                if pExP := makeExP(linkElem.find(PATH_SRR), linkElem.find(PATH_TRR)):
                    varStr = findVar(linkElem)
                    if oExP := makeExP(linkElem.find(RANGE_SN), linkElem.find(RANGE_TYPE), varStr):
                        po = PO(pExP, oExP)
                        for cndElem in linkElem.findall(PATH_TRE):
                            po.condition.add(
                                stripPath(oExP, cndElem.text), cndElem.get('value'))
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


class NS():
    """ docstring
    """

    def __init__(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri

    def __len__(self):
        if self.prefix:
            return 1
        return 0

    def toDict(self):
        return {'prefix': self.prefix, 'uri': self.uri}

    def __repr__(self):
        return str(self.toDict())


def getNamespaces(fname: str):
    '''Returns all namepsaces from a file'''
    mNS = lambda e: NS(e.get('prefix'), e.get('uri'))
    elements = etree.iterparse(fname, events=("end",), tag=(
        'namespace'), encoding='UTF-8', remove_blank_text=True)
    return [mNS(elem) for _, elem in elements if elem.get('prefix')]


if __name__ == "__main__":
    args = sys.argv[1:]
    mappings = args[0] if len(args) == 1 else "defaultMapping.x3ml"
    for t in mappings_from_file(mappings):
        print(json.dumps(t.toDict(), indent=3))
