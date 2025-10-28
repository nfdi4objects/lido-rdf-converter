#!.venv/bin/python
from lxml import etree
import sys
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, field

############################################################################################################################


def not_none(*args) -> bool:
    '''Tests all args to not None'''
    return not any(x is None for x in args)


def apply_valid_arg(func, x, default=None):
    '''Applies a function on a valid argument'''
    return func(x) if not_none(x) else default


def str2bool(bool_str) -> bool:
    '''Converts a string to boolean'''
    return bool_str.lower() in ("yes", "true", "t", "1")


def skipped(elem: etree.Element) -> bool:
    '''Tests if an element is marked as skipped'''
    return str2bool(elem.get('skip', 'false'))


def md5Hash(s: str) -> str:
    '''Returns the MD5 hash of a string'''
    return hashlib.md5(s.encode()).hexdigest()

############################################################################################################################


used_namespaces = {
    'lido': 'http://www.lido-schema.org',
    'gml': 'http://www.opengis.net/gml',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}


def expand_with_namespaces(xml_tag, namespaces=used_namespaces):
    '''Expands a short tag, assume tags like prefix:tag'''
    tokens = xml_tag.split(':', 2)
    if len(tokens) == 2:
        for prefix, ns in namespaces.items():
            if prefix == tokens[0]:
                return f'{{{ns}}}{tokens[1]}'
    return xml_tag


def compress_with_namespaces(xml_tag, namespaces=used_namespaces):
    '''Compresses a long tag, assume tags like {namespace}tag'''
    tokens = xml_tag.split('}', 2)
    if len(tokens) == 2:
        ns_uri = tokens[0].lstrip('{')
        for prefix, ns in namespaces.items():
            if ns == ns_uri:
                return f'{prefix}:{tokens[1]}'
    return xml_tag


def xpath_lido(elem: etree.Element, path_to_subs: str) -> list:
    '''Wrapper for xpath with Lido namespaces'''
    sub_elements = elem.xpath(path_to_subs, namespaces=used_namespaces)
    if '@' in path_to_subs and not elem.text:
        transform_subs(path_to_subs, sub_elements)
    return sub_elements

def transform_subs(path_to_subs, sub_elements):
    attr_name = expand_with_namespaces(path_to_subs.split('[@')[-1].strip(']'))
    for se in sub_elements:
        se.text = se.get(attr_name)


def root_path_as_list(elem):
    '''Return the full lido path of an element'''
    tags = elem.tag.replace(f"{{{ used_namespaces.get('lido','') }}}", '')
    parent = elem.getparent()
    if not_none(parent):
        tags = root_path_as_list(parent) + '/' + tags
    return tags


############################################################################################################################

DOMAIN_SN_PATH = './domain/source_node'
DOMAIN_ET_PATH = './domain/target_node/entity/type'
DOMAIN_COND_PATH = './domain/target_node/if/or/if/equals'

PATH_SRR_PATH = './path/source_relation/relation'
PATH_TRR_PATH = './path/target_relation/relationship'
PATH_COND_PATH = './path/target_relation/if/or/if/equals'

RANGE_SN_PATH = './range/source_node'
RANGE_ENTITY_PATH = './range/target_node/entity'
RANGE_ET_PATH = './range/target_node/entity/type'


def findVar(elem: etree.Element) -> str | None:
    '''Finds the variable attribute'''
    return apply_valid_arg(lambda x: x.get('variable', ''), elem.find(RANGE_ENTITY_PATH + "[@variable]"), '')


def findGen(elem: etree.Element) -> str | None:
    '''Finds the generator name attribute'''
    return apply_valid_arg(lambda x: x.get('name', ''), elem.find(RANGE_ENTITY_PATH + "/instance_generator[@name]"), '')


############################################################################################################################
@dataclass
class ID_Host():
    '''Host for ID tags'''
    tag: str

    def elements(self, elem: etree.Element) -> list:
        '''Returns child elements'''
        if not self.tag:
            return [elem]
        return xpath_lido(elem, f"./{self.tag}")


@dataclass
class ID_Host_List():
    '''Host for multiple ID tags'''
    tags: list = field(default_factory=list)

    def elements(self, elem: etree.Element) -> list:
        '''Returns first child elements from multiple tags'''
        for tag in self.tags:
            if ch := ID_Host(tag=tag).elements(elem):
                return ch
        return []


'''Mapping lido tags to its ID tags'''
LIDO_ID_MAP = {
    'lido:lido': ID_Host('lido:lidoRecID'),
    'lido:event': ID_Host('lido:eventID'),
    'lido:eventType': ID_Host('lido:eventID'),
    'lido:actor': ID_Host('lido:actorID'),
    'lido:category': ID_Host('lido:conceptID'),
    'lido:repositorySet': ID_Host('lido:workID'),
    'lido:place': ID_Host_List(['lido:placeID', 'lido:namePlaceSet/lido:appellationValue']),
    'lido:namePlaceSet': ID_Host('lido:appellationValue'),
    'lido:subjectConcept': ID_Host('lido:conceptID'),
    'lido:recordWrap': ID_Host('lido:recordID'),
    'lido:object': ID_Host('lido:objectID'),
    'lido:recordType': ID_Host('lido:conceptID'),
    'lido:rightsHolder': ID_Host('lido:legalBodyID'),
    'lido:resourceSet': ID_Host('lido:resourceID'),
    'lido:repositoryName': ID_Host('lido:legalBodyID')
}


def get_ID_elements(elem):
    '''Returns all ID child elements'''
    tag = compress_with_namespaces(elem.tag)
    if id_host := LIDO_ID_MAP.get(tag):
        return id_host.elements(elem)
    return []


def get_IDs(elem):
    '''Returns all texts from valid Id elements'''
    validItems = filter(lambda t: not_none(t.text), get_ID_elements(elem))
    return list(map(lambda x: x.text, validItems))


############################################################################################################################

@dataclass
class Info:
    '''Information about an element'''
    text: str = ''
    attrib: dict = field(default_factory=dict)
    mode: str = ''
    id: str = ''
    index: int = -1
    lang: str = ''

    @classmethod
    def from_elem(cls, elem, i):
        '''Creates an Info object from an element'''
        text = elem.text.strip() if elem.text else ''
        lang = elem.get(expand_with_namespaces('xml:lang'), '')

        info = cls(text=text, attrib=elem.attrib, index=i, lang=lang)
        # Priority of ID assignment
        if ids := get_IDs(elem):
            # Has an explicit ID
            info.mode = 'lidoID'
            info.id = ids[0]
        elif len(elem) > 0 and not text:
            # Has subelements, use path as ID
            info.mode = 'path'
            info.id = root_path_as_list(elem) + '/'+str(i)
        else:
            # Just text
            info.mode = 'text'

        return info


############################################################################################################################

@dataclass
class ExP:
    '''Linking of entity and path'''
    path: str = ''
    entity: str = ''
    variable: str = ''
    generator: str = ''

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

    @classmethod
    def fromElements(cls, path_elem: etree.Element, entity_elem: etree.Element, variable: str = '', gen: str = ''):
        '''Creates an cls object from path and type elements'''
        if not_none(path_elem, entity_elem):
            path = path_elem.text
            entity = entity_elem.text
            if entity and path:
                return cls(path=path.strip(), entity=entity.strip(), variable=variable, generator=gen)


def stripPath(link: ExP, txt: str) -> str:
    return txt.removeprefix(link.path)


############################################################################################################################

@dataclass
class Condition():
    '''Condition for filtering elements'''
    access: str = ''
    values: set = field(default_factory=set)

    def add(self, path, value):
        self.access = path
        self.values.add(value)

    def isValid(self, elem) -> bool:
        if len(self.values) > 0:
            if self.access.endswith('/text()'):
                pathValues = elem.xpath(f"./{self.access}", namespaces=used_namespaces)
                return self.values.intersection(pathValues) != set()
            else:
                # assume path as an attribute label
                attrName = expand_with_namespaces(self.access)
                attrValue = elem.get(attrName, '')
                return attrValue in self.values
        return True


############################################################################################################################
@dataclass
class PO_Data:
    '''Data for a single PO'''
    P: ExP = None
    O: ExP = None
    infos: list = field(default_factory=list)
    valid: bool = False


@dataclass
class PO():
    '''Mapping for a single PO'''
    P: ExP = None
    O: ExP = None
    condition: Condition = field(default_factory=Condition)

    def isValid(self, elem):
        return self.condition.isValid(elem)

    def evaluate(self, elem):
        infos = [Info.from_elem(e, i) for i, e in enumerate(self.O.subs(elem))]
        return PO_Data(P=self.P, O=self.O, infos=infos, valid=self.isValid(elem))


############################################################################################################################
@dataclass
class Mapping_Data:
    '''Data for a single mapping'''
    S: ExP = None
    POs: list = field(default_factory=list)
    valid: bool = False
    info: Info = field(default_factory=Info)


@dataclass
class Mapping:
    '''Mapping for a single S with multiple POs'''
    S: ExP = None
    POs: list = field(default_factory=list)
    condition: Condition = field(default_factory=Condition)
    intermediates: list = field(default_factory=list)

    def isValid(self, elem):
        return self.condition.isValid(elem)

    def evaluate_n(self, elem, i):
        POs = [po.evaluate(elem) for po in self.POs]
        return Mapping_Data(S=self.S, POs=POs, valid=self.isValid(elem), info=Info.from_elem(elem, i))

    def evaluate(self, elem):
        return [self.evaluate_n(e, i) for i, e in enumerate(self.S.subs(elem))]

    def addPO(self, po: PO):
        self.POs.append(po)

    def addIntermediate(self, intermediate):
        if intermediate:
            self.intermediates.append(intermediate)

############################################################################################################################


Mappings = list[Mapping]
'''List of mappings'''


def mappingsFromNode(elem) -> Mappings:
    '''Reads single mappings from an x3ml mapping element'''
    mappings = []
    if subject_ExP := ExP.fromElements(elem.find(DOMAIN_SN_PATH), elem.find(DOMAIN_ET_PATH)):
        mapping = Mapping(subject_ExP)
        # Find domain conditions
        for elem_d in elem.findall(DOMAIN_COND_PATH):
            mapping.condition.add(elem_d.text, elem_d.get('value'))
        for elem_l in elem.findall('./link'):
            if not skipped(elem_l):
                if predicate_ExP := ExP.fromElements(elem_l.find(PATH_SRR_PATH), elem_l.find(PATH_TRR_PATH)):
                    varStr = findVar(elem_l)
                    genStr = findGen(elem_l)
                    if object_ExP := ExP.fromElements(elem_l.find(RANGE_SN_PATH), elem_l.find(RANGE_ET_PATH), varStr, genStr):
                        po = PO(P=predicate_ExP, O=object_ExP)
                        for elemO in elem_l.findall(PATH_COND_PATH):
                            po.condition.add(elemO.text, elemO.get('value'))
                        mapping.addPO(po)
        mappings.append(mapping)
    return mappings


def mappings_from_str(xmlStr: str) -> Mappings | None:
    '''Returns all mappings from a string'''
    mappings = []
    parser = etree.XMLPullParser(events=("end",), tag=('mapping'), encoding='UTF-8', remove_blank_text=True)
    parser.feed(xmlStr)
    for _, elem in parser.read_events():
        if not str2bool(elem.get('skip', 'false')):
            mappings += mappingsFromNode(elem)
    return mappings


def mappings_from_file(fileName: str) -> Mappings | None:
    '''Returns all mappings from a file'''
    xmlStr = Path(fileName).read_text(encoding='UTF-8')
    return mappings_from_str(xmlStr)


############################################################################################################################

if __name__ == "__main__":
    args = sys.argv[1:]
    mappings = args[0] if len(args) == 1 else "defaultMapping.x3ml"
    for t in mappings_from_file(mappings):
        print(json.dumps(t.toDict(), indent=3))
