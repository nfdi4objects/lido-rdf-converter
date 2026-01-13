from xml.etree.ElementTree import Element, ElementTree, indent, SubElement, parse, tostring
from dataclasses import dataclass, field
from typing import  List
from libs.json_serializer import to_json, from_json

class JSON_Serializer:
    '''Base class for JSON serialization'''
    def toJSON(self):
        return to_json(self)

    @classmethod
    def fromJSON(cls, data):
        return from_json(data, cls)

def NN(elem: Element) -> bool:
    '''None none: returns True if elem is not None'''
    return not elem is None

def getText(elem: Element | None) -> str:
    '''Returns the text of an element if exists (else an empty string)'''
    if NN(elem):
        return str(elem.text)
    return ''

@dataclass
class X3Base(JSON_Serializer):
    '''Base for X3ML classes, handles attributes (dicts)'''
    attributes: dict = field(default_factory=dict)
    
    def __str__(self):
        return f"{self.__dict__}"

    def deserialize(self, elem: Element):
        if NN(elem):
            self.attributes = elem.attrib
        return self

    def serialize(self, elem: Element) -> Element:
        if NN(elem):
            elem.attrib = self.attributes
        return elem

    def __eq__(self, value):
        return self.__dict__ == value.__dict__
    
    @classmethod
    def from_serial(cls, elem: Element, *args, **kw):
        obj = cls(*args, **kw)
        if NN(elem):
            obj.deserialize(elem)
        return obj

@dataclass
class Predicate(X3Base):
    '''Class for logical operation elements'''
    tag: str = ''
    xpath: str = ''
    value: str = ''
 
    def deserialize(self, elem: Element | None):
        X3Base.deserialize(self, elem)
        self.xpath = elem.text or ''
        self.value = elem.get('value', '')
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        elem.text = self.xpath
        elem.set('value', self.value)
        return elem


@dataclass
class Equals(Predicate):
    '''Class for equals elements'''
    def __post_init__(self):
        self.tag = 'equals'


@dataclass
class SimpleText(X3Base):
    '''Class for simple text elements'''
    text: str = ''

    def alias(self):
        return self.text.replace('lido:', '')

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        if NN(elem.text):
            self.text = elem.text
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        elem.text = self.text
        return elem
@dataclass
class Source(X3Base):
    '''Class for source-schema elements'''
    source_schema: SimpleText = field(default_factory=SimpleText)

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.source_schema = SimpleText.from_serial(elem.find('source_info/source_schema'))
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        subElem = SubElement(elem, 'source_info')
        self.source_schema.serialize(SubElement(subElem, 'source_schema'))
        return elem

    def set(self, schema):
        self.source_schema.text = schema

@dataclass
class Target(X3Base):
    '''Class for target-schema elements'''
    target_schema: SimpleText = field(default_factory=SimpleText)

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.target_schema = SimpleText.from_serial(elem.find('target_info/target_schema'))
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        subElem = SubElement(elem, 'target_info')
        self.target_schema.serialize(SubElement(subElem, 'target_schema'))
        return elem

    def set(self, schema):
        self.target_schema.text = schema

@dataclass
class MappingInfo(X3Base):
    '''Class for mapping-info elements'''

    def deserialize(self, elem: Element):
        return self

    def serialize(self, elem: Element):
        SubElement(elem, 'mapping_created_by_org')
        SubElement(elem, 'mapping_created_by_person')
        SubElement(elem, 'in_collaboration_with')
        return elem

@dataclass
class Comment(X3Base):
    '''Class for comment elements'''
    rationale: SimpleText = field(default_factory=SimpleText)

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.rationale = SimpleText.from_serial(elem.find('rationale'))
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.rationale.serialize(SubElement(elem, 'rationale'))
        SubElement(elem, 'alternatives')
        SubElement(elem, 'typical_mistakes')
        SubElement(elem, 'local_habits')
        SubElement(elem, 'link_to_cook_book')
        elem_ex = SubElement(elem, 'example')
        SubElement(elem_ex, 'example_source')
        SubElement(elem_ex, 'example_target')
        return elem

@dataclass
class ExampleDataInfo(X3Base):
    '''Class for example-data elements'''

    def serialize(self, elem: Element):
        SubElement(elem, 'example_data_from')
        SubElement(elem, 'example_data_contact_person')
        SubElement(elem, 'example_data_source_record')
        SubElement(elem, 'generator_policy_info')
        SubElement(elem, 'example_data_target_record')
        SubElement(elem, 'thesaurus_info')
        return elem

@dataclass
class Info(X3Base):
    '''Class for info-elements'''
    title: SimpleText = field(default_factory=SimpleText)
    general_description: SimpleText = field(default_factory=SimpleText)
    source: Source = field(default_factory=Source)
    target: Target = field(default_factory=Target)
    mapping_info: MappingInfo = field(default_factory=MappingInfo)
    example_data_info: ExampleDataInfo = field(default_factory=ExampleDataInfo)

    @property
    def sSchema(self):
        return self.source.source_schema.text

    @sSchema.setter
    def sSchema(self, value):
        self.source.source_schema.text = value

    @property
    def tSchema(self):
        return self.target.target_schema.text

    @tSchema.setter
    def tSchema(self, value):
        self.target.target_schema.text = value

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.title = SimpleText.from_serial(elem.find('title'))
        self.general_description = SimpleText.from_serial(elem.find('general_description'))
        self.source = Source.from_serial(elem.find('source'))
        self.target = Target.from_serial(elem.find('target'))
        self.mapping_info = MappingInfo.from_serial(elem.find('mapping_info'))
        self.example_data_info = ExampleDataInfo.from_serial(elem.find('example_data_info'))
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.title.serialize(SubElement(elem, 'title'))
        self.general_description.serialize(SubElement(elem, 'general_description'))
        self.source.serialize(SubElement(elem, 'source'))
        self.target.serialize(SubElement(elem, 'target'))
        self.mapping_info.serialize(SubElement(elem, 'mapping_info'))
        self.example_data_info.serialize(SubElement(elem, 'example_data_info'))
        return elem

@dataclass
class Namespace(X3Base):
    '''Class for namespace elements'''
    def __post_init__(self):
        self.attributes.setdefault('prefix', '')
        self.attributes.setdefault('uri', '')


    @property
    def prefix(self):
        return self.attributes['prefix']

    @prefix.setter
    def prefix(self, value):
        self.attributes['prefix'] = value

    @property
    def uri(self):
        return self.attributes['uri']

    @uri.setter
    def uri(self, value):
        self.attributes['uri'] = value

    def __eq__(self, other):
        return self.prefix == other.prefix

    def set(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri
        return self

@dataclass
class InstanceInfo(X3Base):
    '''Class for instance info elements'''
    mode: str = ''

    def deserialize(self, elem: Element):
        if NN(elem.find('constant')):
            self.mode = 'constant'
        if NN(elem.find('language')):
            self.mode = 'language'
        if NN(elem.find('description')):
            self.mode = 'description'
        return self

    def serialize(self, elem: Element):
        match self.mode:
            case 'constant':
                SubElement(elem, 'constant')
            case 'language':
                SubElement(elem, 'language')
            case 'description':
                SubElement(elem, 'description')
        return elem

@dataclass
class Entity(X3Base):
    '''Class for entity elements'''
    type: str = ''
    instance_info: List[InstanceInfo] = field(default_factory=list)
    instance_generator: List = field(default_factory=list)
    label_generator: List = field(default_factory=list)
    additional: List = field(default_factory=list)

    def deserialize(self, elem: Element | None):
        X3Base.deserialize(self, elem)
        self.type = getText(elem.find('type'))
        self.instance_info = [InstanceInfo.from_serial(x) for x in elem.findall('instance_info')]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        t = SubElement(elem, 'type')
        t.text = self.type
        for x in self.instance_info:
            x.serialize(SubElement(elem, 'instance_info'))
        return elem

@dataclass
class TargetNode(X3Base):
    '''Class for target node elements'''
    entity: Entity = field(default_factory=Entity)
    conditions: List[Equals] = field(default_factory=list)
    enableC: bool = True

    def deserialize(self, elem: Element, **kw):
        X3Base.deserialize(self, elem)
        self.entity = Entity.from_serial(elem.find('entity'))
        self.conditions = [Equals.from_serial(x) for x in elem.findall('if/or/if/equals')]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.entity.serialize(SubElement(elem, 'entity'))
        for cond in self.conditions:
            e = SubElement(SubElement(SubElement(SubElement(elem, 'if'), 'or'), 'if'), 'equals')
            cond.serialize(e)
        return elem

@dataclass
class Domain(X3Base):
    '''Class for domain elements'''
    sourceNode: SimpleText = field(default_factory=SimpleText)
    targetNode: TargetNode = field(default_factory=TargetNode)
    comments: List[Comment] = field(default_factory=list)

    @property
    def path(self):
        return self.sourceNode.text

    @path.setter
    def path(self, value):
        self.sourceNode.text = value

    @property
    def entity(self):
        return self.targetNode.entity.type

    @entity.setter
    def entity(self, value):
        self.targetNode.entity.type = value

    def set(self, path, entity):
        self.path = path
        self.entity = entity

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.sourceNode = SimpleText.from_serial(elem.find('source_node'))
        self.targetNode = TargetNode.from_serial(elem.find('target_node'))
        self.comments = [Comment.from_serial(x) for x in elem.findall('comments/comment')]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.sourceNode.serialize(SubElement(elem, 'source_node'))
        self.targetNode.serialize(SubElement(elem, 'target_node'))
        if self.comments:
            cs = SubElement(elem, 'comments')
            for x in self.comments:
                x.serialize(SubElement(cs, 'comment'))
        return elem

@dataclass
class NR(X3Base):
    '''Class for node-relation pair elements'''
    node: SimpleText = field(default_factory=SimpleText)
    relation: SimpleText = field(default_factory=SimpleText)

    def serialize(self, elem: Element):
        self.node.serialize(SubElement(elem, 'node'))
        self.relation.serialize(SubElement(elem, 'relation'))
        return self

    def deserialize(self, elem: Element):
        self.node = SimpleText.from_serial(elem.find('node'))
        self.relation = SimpleText.from_serial(elem.find('relation'))
        return elem

    @classmethod
    def create(cls, node: str = '', relation: str = ''):
        return cls(node=SimpleText(text=node), relation=SimpleText(text=relation))

@dataclass
class SourceRelation(X3Base):
    '''Class for source relation elements'''
    relation: SimpleText = field(default_factory=SimpleText)
    nodes: List[NR] = field(default_factory=list)

    @property
    def path(self):
        return self.relation.text

    @path.setter
    def path(self, value):
        self.relation.text = value

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        rs = elem.findall('relation')
        ns = elem.findall('node')
        self.relation = SimpleText.from_serial(rs.pop(0))
        self.nodes = [NR(SimpleText.from_serial(n), SimpleText.from_serial(r)) for n, r in zip(ns, rs)]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.relation.serialize(SubElement(elem, 'relation'))
        for ns in self.nodes:
            ns.relation.serialize(SubElement(elem, 'relation'))
            ns.node.serialize(SubElement(elem, 'node'))
        return elem

@dataclass
class Relationship(SimpleText):
    '''Class for relationship elements'''
    pass

@dataclass
class TargetExtension:
    '''Class for TargetExtension elements'''
    entity: Entity = field(default_factory=Entity)
    relationship: Relationship = field(default_factory=Relationship)

    def deserialize(self, elem: Element):
        self.entity = Entity.from_serial(elem.find('entity'))
        self.relationship = Relationship.from_serial(elem.find('relationship'))
        return self

    def serialize(self, elem: Element):
        self.entity.serialize(SubElement(elem, 'entity'))
        self.relationship.serialize(SubElement(elem, 'relationship'))
        return elem

@dataclass
class TargetRelation(X3Base):
    '''Class for target relation type elements'''
    conditions: List[Equals] = field(default_factory=list)
    relationship: Relationship = field(default_factory=Relationship)
    extensions: List[TargetExtension] = field(default_factory=list)

    @property
    def entity(self):
        return self.relationship.text

    @entity.setter
    def entity(self, value):
        self.relationship.text = value

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        
        for cond in self.conditions:
            e = SubElement(SubElement(SubElement(SubElement(elem, 'if'), 'or'), 'if'), 'equals')
            cond.serialize(e)

        self.relationship.serialize(SubElement(elem, 'relationship'))

        for x in self.extensions:
            x.entity.serialize(SubElement(elem, 'entity'))
            x.relationship.serialize(SubElement(elem, 'relationship'))
        return elem

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
  
        self.conditions = [Equals.from_serial(x) for x in elem.findall('if/or/if/equals')]
        rsElems = elem.findall('relationship')
        if len(rsElems) > 0:
            self.relationship = Relationship.from_serial(rsElems.pop())
            enElems = elem.findall('entity')
            if len(enElems) == len(rsElems):
                self.extensions = [TargetExtension(Entity.from_serial(e), Relationship.from_serial(r)) for e, r in zip(enElems, rsElems)]
        return self

@dataclass
class Path(X3Base):
    '''Class for path elements'''
    sourceRelation: SourceRelation = field(default_factory=SourceRelation)
    targetRelation: TargetRelation = field(default_factory=TargetRelation)
    comments: List[Comment] = field(default_factory=list)

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.sourceRelation = SourceRelation.from_serial(elem.find('source_relation'))
        self.targetRelation = TargetRelation.from_serial(elem.find('target_relation'))
        self.comments = [Comment.from_serial(x) for x in elem.findall('comments/comment')]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.sourceRelation.serialize(SubElement(elem, 'source_relation'))
        self.targetRelation.serialize(SubElement(elem, 'target_relation'))
        if self.comments:
            cs = SubElement(elem, 'comments')
            for x in self.comments:
                x.serialize(SubElement(cs, 'comment'))
        return elem

@dataclass
class Range(X3Base):
    '''Class for range elements'''
    sourceNode: SimpleText = field(default_factory=SimpleText)
    targetNode: TargetNode = field(default_factory=lambda: TargetNode(enableC=True))

    @property
    def path(self):
        return self.sourceNode.text

    @path.setter
    def path(self, value):
        self.sourceNode.text = value

    @property
    def entity(self):
        return self.targetNode.entity.type

    @entity.setter
    def entity(self, value):
        self.targetNode.entity.type = value

    def set(self, path, entity):
        self.path = path
        self.entity = entity

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.sourceNode = SimpleText.from_serial(elem.find('source_node'))
        self.targetNode = TargetNode.from_serial(elem.find('target_node'))
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.sourceNode.serialize(SubElement(elem, 'source_node'))
        self.targetNode.serialize(SubElement(elem, 'target_node'))
        return elem

@dataclass
class Link(X3Base):
    '''Class for link elements'''
    path: Path = field(default_factory=Path)
    range: Range = field(default_factory=Range)
    
    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.path = Path.from_serial(elem.find('path'))
        self.range = Range.from_serial(elem.find('range'))
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.path.serialize(SubElement(elem, 'path'))
        self.range.serialize(SubElement(elem, 'range'))
        return elem

@dataclass
class Mapping(X3Base):
    '''Class for mapping elements'''
    domain: Domain = field(default_factory=Domain)
    links: List[Link] = field(default_factory=list)

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.domain = Domain.from_serial(elem.find('domain'))
        self.links = [Link.from_serial(x) for x in elem.findall('link')]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.domain.serialize(SubElement(elem, 'domain'))
        for link in self.links:
            link.serialize(SubElement(elem, 'link'))
        return elem

    def label(self, n=0):
        return f"Mapping {n}: Domain={self.domain.sourceNode.text}"

@dataclass
class X3ml(X3Base):
    '''Class for X3ML elements'''
    namespaces: List[Namespace] = field(default_factory=list)
    mappings: List[Mapping] = field(default_factory=list)
    info: Info = field(default_factory=Info)

    def deserialize(self, elem: Element):
        X3Base.deserialize(self, elem)
        self.info = Info.from_serial(elem.find('info'))
        self.namespaces = [Namespace.from_serial(x) for x in elem.findall('./namespaces/namespace')]
        self.mappings = [Mapping.from_serial(x) for x in elem.findall('./mappings/mapping')]
        return self

    def serialize(self, elem: Element):
        X3Base.serialize(self, elem)
        self.info.serialize(SubElement(elem, 'info'))
        
        nss = SubElement(elem, 'namespaces')
        for m in self.namespaces:
            m.serialize(SubElement(nss, 'namespace'))
            
        mss = SubElement(elem, 'mappings')
        for m in self.mappings:
            m.serialize(SubElement(mss, 'mapping'))
        
        return elem

    def to_str(self, space="  "):
        elem = self.serialize(Element('x3ml'))
        indent(elem, space=space)
        return tostring(elem).decode('utf-8')


@dataclass
class LabelGenerator(X3Base):
    '''Class for label generator elements'''
    value: str = ''

@dataclass
class Instance_Generator(X3Base):
    '''Class for instance generator elements'''
    value: str = ''

def loadX3ml(filePath='../defaultMapping.x3ml'):
    '''Loads an X3ML model from a file'''
    tree = parse(filePath)
    return X3ml.from_serial(tree.getroot())

def storeX3ml(model: X3ml, filePath='download.x3ml'):
    '''Stores an X3ML model to a file'''
    root = model.serialize(Element('x3ml'))
    indent(root,space='    ')
    tree = ElementTree(root)
    tree.write(filePath, encoding='utf-8', xml_declaration=True)
    return filePath

if __name__ == "__main__":
    loadX3ml()
