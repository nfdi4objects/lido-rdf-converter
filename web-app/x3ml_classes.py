import xml.etree.ElementTree as ET
import json


class Serializer:
    '''Provides super classes with JSON serialization'''
    def toJSON(self, indent=2):
        return json.dumps(self, default=lambda o: o.__dict__,  sort_keys=True, indent=int(indent))


def NN(elem: ET.Element):
    '''Returns True if elem is not None'''
    return not elem is None

def getText(elem: ET.Element | None) -> str:
    '''Returns the text of the element or an empty string'''
    if NN(elem):
        return str(elem.text)
    return ''


class X3Base(Serializer):
    '''Base class for X3ML classes'''
    counter = 0

    def __init__(self, elem: ET.Element = None):
        self.attributes = {}
        if NN(elem):
            self.deserialize(elem)
        X3Base.counter += 1

    def __del__(self):
        X3Base.counter -= 1

    def __str__(self):
        return f"{ self.__class__.__name__}"

    def getAttr(self, name):
        return self.attributes[name]

    def setAttr(self, name, value):
        self.attributes[name] = value

    def deserialize(self, elem: ET.Element):
        self.attributes = elem.attrib
        return self

    def serialize(self, elem: ET.Element):
        elem.attrib = self.attributes
        return elem


class SimpleText(X3Base):
    '''Model class for simple text elements'''
    def __init__(self, elem: ET.Element | None = None, **kw):
        super().__init__(elem=None)
        self.text = kw.get('text', '')
        if NN(elem):
            self.deserialize(elem)
    def alias(self):
        return self.text.replace('lido:', '')
    
    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        if NN(elem.text):
            self.text = elem.text

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        elem.text = self.text

    def __str__(self):
        return f"{ self.__class__.__name__}\t{self.text}"

    @staticmethod
    def create(s: str = ''):
        return SimpleText(text=s)


class Source(X3Base):
    '''Model class for source schema elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.source_schema = SimpleText()
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.source_schema = SimpleText(elem.find('source_info/source_schema'))
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        subElem = ET.SubElement(elem, 'source_info')
        self.source_schema.serialize(ET.SubElement(subElem, 'source_schema'))
        return elem

    def set(self, schema):
        self.source_schema.text = schema


class Target(X3Base):
    '''Model class for target schema elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.target_schema = SimpleText()
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.target_schema = SimpleText(elem.find('target_info/target_schema'))
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        subElem = ET.SubElement(elem, 'target_info')
        self.target_schema.serialize(ET.SubElement(subElem, 'target_schema'))
        return elem

    def set(self, schema):
        self.target_schema.text = schema


class MappingInfo(X3Base):
    '''Model class for mapping info elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        ET.SubElement(elem, 'mapping_created_by_org')
        ET.SubElement(elem, 'mapping_created_by_person')
        ET.SubElement(elem, 'in_collaboration_with')
        return elem


class Comment(X3Base):
    '''Model class for comment elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.rationale = SimpleText()
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.rationale = SimpleText(elem.find('rationale'))
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.rationale.serialize(ET.SubElement(elem, 'rationale'))
        ET.SubElement(elem, 'alternatives')
        ET.SubElement(elem, 'typical_mistakes')
        ET.SubElement(elem, 'local_habits')
        ET.SubElement(elem, 'link_to_cook_book')
        ex = ET.SubElement(elem, 'example')
        ET.SubElement(ex, 'example_source')
        ET.SubElement(ex, 'example_target')
        return elem

    @staticmethod
    def create(s):
        t = Comment()
        t.rationale = SimpleText.create(s)
        return t


class ExampleDataInfo(X3Base):
    '''Model class for example data elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        ET.SubElement(elem, 'example_data_from')
        ET.SubElement(elem, 'example_data_contact_person')
        ET.SubElement(elem, 'example_data_source_record')
        ET.SubElement(elem, 'generator_policy_info')
        ET.SubElement(elem, 'example_data_target_record')
        ET.SubElement(elem, 'thesaurus_info')
        return elem


class Info(X3Base):
    '''Model class for info elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.title = SimpleText()
        self.general_description = SimpleText()
        self.source = Source()
        self.target = Target()
        self.mapping_info = MappingInfo()
        self.example_data_info = ExampleDataInfo()
        if NN(elem):
            self.deserialize(elem)

    @property
    def sSchema(self): return self.source.source_schema.text

    @sSchema.setter
    def sSchema(self, value): self.source.source_schema.text = value

    @property
    def tSchema(self): return self.target.target_schema.text

    @tSchema.setter
    def tSchema(self, value): self.target.target_schema.text = value

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.title = SimpleText(elem.find('title'))
        self.general_description = SimpleText(elem.find('general_description'))
        self.source = Source(elem.find('source'))
        self.target = Target(elem.find('target'))
        self.mapping_info = MappingInfo(elem.find('mapping_info'))
        self.example_data_info = ExampleDataInfo(elem.find('example_data_info'))
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.title.serialize(ET.SubElement(elem, 'title'))
        self.general_description.serialize(
            ET.SubElement(elem, 'general_description'))
        self.source.serialize(ET.SubElement(elem, 'source'))
        self.target.serialize(ET.SubElement(elem, 'target'))
        self.mapping_info.serialize(ET.SubElement(elem, 'mapping_info'))
        self.example_data_info.serialize(ET.SubElement(elem, 'example_data_info'))
        return elem


class Namespace(X3Base):
    '''Model class for namespace elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)

    @property
    def prefix(self): return self.getAttr('prefix')

    @prefix.setter
    def prefix(self, value): self.setAttr('prefix', value)

    @property
    def uri(self): return self.getAttr('uri')

    @uri.setter
    def uri(self, value): self.setAttr('uri', value)

    def __eq__(self, other):
        return self.prefix == other.prefix

    def set(self, p, u):
        self.prefix = p
        self.uri = u
        return self


class Domain(X3Base):
    '''Model class for domain elements''' 
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.sourceNode = SourceNode()
        self.targetNode = DomainTargetNodeType()
        self.comments = []
        if NN(elem):
            self.deserialize(elem)

    @property
    def path(self): return self.sourceNode.text

    @path.setter
    def path(self, value):  self.sourceNode.text = value

    @property
    def entity(self): return self.targetNode.entity.type

    @entity.setter
    def entity(self, value):  self.targetNode.entity.type = value

    def set(self, path, entity):
        self.path = path
        self.entity = entity

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.sourceNode = SourceNode(elem.find('source_node'))
        self.targetNode = DomainTargetNodeType(elem.find('target_node'))
        self.comments = [Comment(x) for x in elem.findall('comments/comment')]

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.sourceNode.serialize(ET.SubElement(elem, 'source_node'))
        self.targetNode.serialize(ET.SubElement(elem, 'target_node'))
        if self.comments:
            cs = ET.SubElement(elem, 'comments')
            for x in self.comments:
                x.serialize(ET.SubElement(cs, 'comment'))


class NR(X3Base):
    '''Model class for node-relation pair elements'''
    def __init__(self, node: SimpleText, relation: SimpleText) -> None:
        self.node = node
        self.relation = relation

    def serialize(self, elem: ET.Element):
        self.node.serialize(ET.SubElement(elem, 'node'))
        self.relation.serialize(ET.SubElement(elem, 'relation'))
        return elem

    def deserialize(self, elem: ET.Element):
        self.node = SimpleText(elem.find('node'))
        self.relation = SimpleText(elem.find('relation'))
        return elem

    @staticmethod
    def create(node: str = '', relation: str = ''):
        return NR(SimpleText(text=node), SimpleText(text=relation))


class SourceRelation(X3Base):
    '''Model class for source relation elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.relation = SimpleText()
        self.nodes = []
        if NN(elem):
            self.deserialize(elem)

    @property
    def path(self): return self.relation.text

    @path.setter
    def path(self, value):  self.relation.text = value

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        rs = elem.findall('relation')
        ns = elem.findall('node')
        self.relation = SimpleText(rs.pop(0))
        self.nodes = [NR(SimpleText(n), SimpleText(r)) for n, r in zip(ns, rs)]
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.relation.serialize(ET.SubElement(elem, 'relation'))
        for ns in self.nodes:
            ns.relation.serialize(ET.SubElement(elem, 'relation'))
            ns.node.serialize(ET.SubElement(elem, 'node'))
        return elem

    @staticmethod
    def create(s: str = ''):
        sr = SourceRelation()
        sr.relation = SimpleText.create(s)
        return sr


class Path(X3Base):
    '''Model class for path elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.sourceRelation = SourceRelation()
        self.targetRelation = TargetRelationType()
        self.comments = []
        if NN(elem):
            self.deserialize(elem)

    @property
    def path(self): return self.sourceRelation.path

    @path.setter
    def path(self, value):  self.sourceRelation.path = value

    @property
    def entity(self): return self.targetRelation.entity

    @entity.setter
    def entity(self, value):  self.targetRelation.entity = value

    def set(self, path, relationship):
        self.path = path
        self.entity = relationship

    def addComment(self, s):
        self.comments.append(Comment.create(s))

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.sourceRelation = SourceRelation(elem.find('source_relation'))
        self.targetRelation = TargetRelationType(elem.find('target_relation'))
        self.comments = [Comment(x) for x in elem.findall('comments/comment')]
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.sourceRelation.serialize(ET.SubElement(elem, 'source_relation'))
        self.targetRelation.serialize(ET.SubElement(elem, 'target_relation'))
        if self.comments:
            cs = ET.SubElement(elem, 'comments')
            for x in self.comments:
                x.serialize(ET.SubElement(cs, 'comment'))
        return elem


class Range(X3Base):
    '''Model class for range elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.sourceNode = SourceNode()
        self.targetNode = TargetNode()
        if NN(elem):
            self.deserialize(elem)

    @property
    def path(self): return self.sourceNode.text

    @path.setter
    def path(self, value):  self.sourceNode.text = value

    @property
    def entity(self): return self.targetNode.entity.type

    @entity.setter
    def entity(self, value):  self.targetNode.entity.type = value

    def set(self, path, entity):
        self.path = path
        self.entity = entity

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.sourceNode = SourceNode(elem.find('source_node'))
        self.targetNode = TargetNode(elem.find('target_node'))

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.sourceNode.serialize(ET.SubElement(elem, 'source_node'))
        self.targetNode.serialize(ET.SubElement(elem, 'target_node'))
        return elem


class Link(X3Base):
    '''Model class for link elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.setAttr('skip', 'false')
        self.path = Path()
        self.range = Range()
        if NN(elem):
            self.deserialize(elem)

    @property
    def skip(self): return self.getAttr('skip')

    @skip.setter
    def skip(self, value):  self.setAttr('skip', value)

    def set(self, path, relationship, entity):
        self.path.set(path, relationship)
        self.range.set(path, entity)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.path = Path(elem.find('path'))
        self.range = Range(elem.find('range'))

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.path.serialize(ET.SubElement(elem, 'path'))
        self.range.serialize(ET.SubElement(elem, 'range'))
        return elem


class Mapping(X3Base):
    '''Model class for mapping elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.setAttr('skip', 'false')
        self.domain = Domain()
        self.links = []
        if NN(elem):
            self.deserialize(elem)

    @property
    def skip(self): return self.getAttr('skip')

    @skip.setter
    def skip(self, value):  self.setAttr('skip', value)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.domain = Domain(elem.find('domain'))
        self.links = [Link(x) for x in elem.findall('link')]
        return self

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.domain.serialize(ET.SubElement(elem, 'domain'))
        for link in self.links:
            link.serialize(ET.SubElement(elem, 'link'))
        return elem

    def label(self, n=0):
        return f"Mapping {n}: Domain={self.domain.sourceNode.text}"
    @staticmethod
    def create():
        m = Mapping()
        m.domain.path = '//lido:lido'
        return m


class X3ml(X3Base):
    '''Model class for X3ML elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.namespaces = []
        self.mappings = []
        self.info = Info()
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.info = Info(elem.find('info'))
        self.namespaces = [Namespace(x) for x in elem.findall('./namespaces/namespace')]
        self.mappings = [Mapping(x) for x in elem.findall('./mappings/mapping')]

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.info.serialize(ET.SubElement(elem, 'info'))
        nss = ET.SubElement(elem, 'namespaces')
        for m in self.namespaces:
            m.serialize(ET.SubElement(nss, 'namespace'))
        mss = ET.SubElement(elem, 'mappings')
        for m in self.mappings:
            m.serialize(ET.SubElement(mss, 'mapping'))
        return elem


class LabelGenerator(X3Base):
    '''Model class for label generator elements'''
    def __init__(self, val=''):
        super().__init__()
        self.value: str = val


class Instance_Generator(X3Base):
    '''Model class for instance generator elements'''
    def __init__(self, val=''):
        super().__init__()
        self.value: str = val


class InstanceInfo(X3Base):
    '''Model class for instance info elements'''
    def __init__(self, elem: ET.Element | None = None):
        super().__init__(elem)
        self.mode = ''
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element):
        if not elem.find('constant') is None:
            self.mode = 'constant'
        if not elem.find('language') is None:
            self.mode = 'language'
        if not elem.find('description') is None:
            self.mode = 'description'

    def serialize(self, elem: ET.Element):
        match self.mode:
            case 'constant':
                ET.SubElement(elem, 'constant')
            case 'language':
                ET.SubElement(elem, 'language')
            case 'description':
                ET.SubElement(elem, 'description')
        return elem


class Relationship(SimpleText):
    '''Model class for relationship elements'''
    pass


class Entity(X3Base):
    '''Model class for entity elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem)
        self.type = ''
        self.instance_info = []
        self.instance_generator = []
        self.label_generator = []
        self.additional = []
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element | None):
        super().deserialize(elem)
        if NN(elem):
            self.type = getText(elem.find('type'))
            self.instance_info = [InstanceInfo(x) for x in elem.findall('instance_info')]

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        t = ET.SubElement(elem, 'type')
        t.text = self.type
        for x in self.instance_info:
            x.serialize(ET.SubElement(elem, 'instance_info'))


class TargetExtenion(Serializer):
    '''Model class for TargetExtenion elements'''
    def __init__(self, entity: Entity, relationShip: Relationship) -> None:
        self.entity = entity
        self.relationship = relationShip

    def serialize(self, elem: ET.Element):
        self.entity.serialize(ET.SubElement(elem, 'entity'))
        self.relationship.serialize(ET.SubElement(elem, 'relationship'))
        return elem

    def deserialize(self, elem: ET.Element):
        self.entity = Entity(elem.find('entity'))
        self.relationship = Relationship(elem.find('relationship'))
        return elem


class TargetRelationType(X3Base):
    '''Model class for target relation type elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem)
        self.ifs = []
        self.relationship = Relationship(None)
        self.extensions = []
        if NN(elem):
            self.deserialize(elem)

    @property
    def entity(self): return self.relationship.text

    @entity.setter
    def entity(self, value):  self.relationship.text = value

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.relationship.serialize(ET.SubElement(elem, 'relationship'))
        for x in self.ifs:
            x.serialize(ET.SubElement(elem, 'if'))
        for x in self.extensions:
            x.entity.serialize(ET.SubElement(elem, 'entity'))
            x.relationship.serialize(ET.SubElement(elem, 'relationship'))
        return elem

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.ifs = [If(x) for x in elem.findall('if')]
        rsElems = elem.findall('relationship')
        if len(rsElems) > 0:
            self.relationship = Relationship(rsElems.pop())
            enElems = elem.findall('entity')
            if len(enElems) == len(rsElems):
                self.extensions = [TargetExtenion(Entity(e), Relationship(r)) for e, r in zip(enElems, rsElems)]
        return elem


class RangeTargetNodeType(X3Base):
    '''Model class for range target node type elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem)
        self.entity = Entity()
        self.ifs = []
        if NN(elem):
            self.deserialize(elem)

    def deserialize(self, elem: ET.Element):
        super().deserialize(elem)
        self.entity = Entity(elem.find('entity'))
        self.ifs = [If(x) for x in elem.findall('if')]
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        self.entity.serialize(ET.SubElement(elem, 'entity'))
        for x in self.ifs:
            x.serialize(ET.SubElement(elem, 'if'))
        return elem


class TargetNode(RangeTargetNodeType):
    '''Model class for target node elements'''
    pass


class DomainTargetNodeType(RangeTargetNodeType):
    '''Model class for domain target node type elements'''
    pass


class SourceNode(SimpleText):
    '''Model class for source node elements'''
    pass


class LogicalOp (X3Base):
    '''Model class for logical operation elements'''
    def __init__(self, elem: ET.Element | None = None, tag: str = '') -> None:
        super().__init__(elem)
        self.tag = tag
        self.xpath = ''
        self.value=''
        self._ifs = []
        if NN(elem):
            self.deserialize(elem)

    def append(self, objIf):
        if isinstance(objIf,If):
            self._ifs.append(objIf)
            return objIf
    
    def reset(self):
        self.xpath = ''
        self.value = ''
        self._ifs = []

    def deserialize(self, elem: ET.Element | None):
        super().deserialize(elem)
        self.reset()
        if children := elem.findall('if'):
            self._ifs = [If(x) for x in children]
        else:
            self.xpath = elem.text
            self.value = elem.get('value','')
        return elem

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        if self._ifs:
            for x in self._ifs:
                x.serialize(ET.SubElement(elem, 'if'))
        else:
            if self.xpath: elem.text = self.xpath
            if self.value: elem.set('value',self.value)
        return elem
    
    def validPath(self,elem):
        if NN(elem):
            if self.xpath and self.value:
                pathValues = [x.text for x in elem.findall(self.xpath)]
                return self.value in pathValues
        return False

    def isValid(self,elem):
        return self.validPath(elem)


class Not(LogicalOp):
    '''Model class for not elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'not')


class And (LogicalOp):
    '''Model class for and elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'and')

    def isValid(self,elem):
        if NN(elem):
            if self._ifs:
                return all([x.isValid(elem) for x in self._ifs])
            return self.validPath(elem)
        return False

class Or(LogicalOp):
    '''Model class for or elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'or')

    def isValid(self,elem):
        if NN(elem):
            if self._ifs:
                return any([x.isValid(elem) for x in self._ifs])
            return self.validPath(elem)
        return False

class ExactMatch(LogicalOp):
    '''Model class for exact-match elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'exact_match')


class Broader(LogicalOp):
    '''Model class for broader elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'broader')


class Narrower(LogicalOp):
    '''Model class for narrower elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'narrower')


class Equals(LogicalOp):
    '''Model class for equals elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'equals')


class Exists(LogicalOp):
    '''Model class for exists elements'''
    def __init__(self, elem: ET.Element | None = None) -> None:
        super().__init__(elem, 'exists')


class ConditionsType(X3Base):
    '''Model class for conditions type elements'''
    def __init__(self, elem: ET.Element | None = None, **kw) -> None:
        super().__init__(elem)
        self.op = Or()
        if NN(elem):
            self.deserialize(elem)

    def setOp(self, op):
        if isinstance(op,LogicalOp):
            self.op = op
            return op
        
    def deserialize(self, elem: ET.Element | None):
        super().deserialize(elem)

        def choice(tag, cls):
            st = elem.find(tag)
            if NN(st):
                self.op = cls(st)

        self.op = None
        choice('or', Or)
        choice('and', And)
        choice('not', Not)
        choice('narrower', Narrower)
        choice('broader', Broader)
        choice('exists', Exists)
        choice('equals', Equals)
        choice('exact_match', ExactMatch)

    def serialize(self, elem: ET.Element):
        super().serialize(elem)
        if self.op:
            self.op.serialize(ET.SubElement(elem, self.op.tag))

    def isValid(self,elem):
        if NN(self.op) and NN(elem):
            return self.op.isValid(elem)
        return False
        


class If(ConditionsType):
    '''Model class for If elements'''
    pass


def loadX3ml(filePath='defaultMapping.x3ml'):
    '''Loads an X3ML model from a file'''
    model = X3ml()
    tree = ET.parse(filePath)
    model.deserialize(tree.getroot())
    return model


def storeX3ml(model: X3ml, filePath='download.x3ml'):
    '''Stores an X3ML model to a file'''
    root = model.serialize(ET.Element('x3ml'))
    ET.indent(root)
    tree = ET.ElementTree(root)
    tree.write(filePath, encoding='utf-8', xml_declaration=True)
    return filePath


if __name__ == "__main__":
    loadX3ml()
