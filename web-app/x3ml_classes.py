from xml.etree.ElementTree import Element, ElementTree, indent, SubElement, parse
import json

class Predicate():
    def validate(self,elem):
        return False

class Serializer:
    '''Provides super classes with JSON serialization'''
    def toJSON(self, indent=2):
        return json.dumps(self, default=lambda o: o.__dict__,  sort_keys=True, indent=int(indent))


def NN(elem: Element):
    '''Returns True if elem is not None'''
    return not elem is None

def getText(elem: Element | None) -> str:
    '''Returns the text of the element or an empty string'''
    if NN(elem):
        return str(elem.text)
    return ''


class X3Base(Serializer):
    '''Base class for X3ML classes'''
    counter = 0

    def __init__(self):
        self.attributes = {}
        X3Base.counter += 1

    def __del__(self):
        X3Base.counter -= 1

    def __str__(self):
        return f"{ self.__class__.__name__}"

    def getAttr(self, name):
        return self.attributes[name]

    def setAttr(self, name, value):
        self.attributes[name] = value

    def deserialize(self, elem: Element):
        if NN(elem):
            self.attributes = elem.attrib
        return self

    def serialize(self, elem: Element) -> Element:
        if NN(elem):
            elem.attrib = self.attributes
        return elem


class SimpleText(X3Base):
    '''Model class for simple text elements'''
    def __init__(self, elem: Element | None = None, **kw):
        super().__init__()
        self.text = kw.get('text', '')
        self.deserialize(elem)

    def alias(self):
        return self.text.replace('lido:', '')
    
    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            if NN(elem.text):
                self.text = elem.text
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            elem.text = self.text
        return elem

    def __str__(self):
        return f"{ self.__class__.__name__}\t{self.text}"

    @staticmethod
    def create(s: str = ''):
        return SimpleText(text=s)


class Source(X3Base):
    '''Model class for source schema elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.source_schema = SimpleText()
        self.deserialize(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.source_schema = SimpleText(elem.find('source_info/source_schema'))
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            subElem = SubElement(elem, 'source_info')
            self.source_schema.serialize(SubElement(subElem, 'source_schema'))
        return elem

    def set(self, schema):
        self.source_schema.text = schema


class Target(X3Base):
    '''Model class for target schema elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.target_schema = SimpleText()
        self.deserialize(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.target_schema = SimpleText(elem.find('target_info/target_schema'))
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            subElem = SubElement(elem, 'target_info')
            self.target_schema.serialize(SubElement(subElem, 'target_schema'))
        return elem

    def set(self, schema):
        self.target_schema.text = schema


class MappingInfo():
    '''Model class for mapping info elements'''
    def __init__(self, elem: Element | None = None):
        pass

    def deserialize(self, elem: Element):
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            SubElement(elem, 'mapping_created_by_org')
            SubElement(elem, 'mapping_created_by_person')
            SubElement(elem, 'in_collaboration_with')
        return elem


class Comment(X3Base):
    '''Model class for comment elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.rationale = SimpleText()
        self.deserialize(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.rationale = SimpleText(elem.find('rationale'))
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.rationale.serialize(SubElement(elem, 'rationale'))
            SubElement(elem, 'alternatives')
            SubElement(elem, 'typical_mistakes')
            SubElement(elem, 'local_habits')
            SubElement(elem, 'link_to_cook_book')
            ex = SubElement(elem, 'example')
            SubElement(ex, 'example_source')
            SubElement(ex, 'example_target')
        return elem

    @staticmethod
    def create(s):
        t = Comment()
        t.rationale = SimpleText.create(s)
        return t


class ExampleDataInfo():
    '''Model class for example data elements'''
    def __init__(self, elem: Element | None = None):
        pass

    def deserialize(self, elem: Element):
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            SubElement(elem, 'example_data_from')
            SubElement(elem, 'example_data_contact_person')
            SubElement(elem, 'example_data_source_record')
            SubElement(elem, 'generator_policy_info')
            SubElement(elem, 'example_data_target_record')
            SubElement(elem, 'thesaurus_info')
        return elem


class Info(X3Base):
    '''Model class for info elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.title = SimpleText()
        self.general_description = SimpleText()
        self.source = Source()
        self.target = Target()
        self.mapping_info = MappingInfo()
        self.example_data_info = ExampleDataInfo()
        self.deserialize(elem)

    @property
    def sSchema(self): return self.source.source_schema.text

    @sSchema.setter
    def sSchema(self, value): self.source.source_schema.text = value

    @property
    def tSchema(self): return self.target.target_schema.text

    @tSchema.setter
    def tSchema(self, value): self.target.target_schema.text = value

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.title = SimpleText(elem.find('title'))
            self.general_description = SimpleText(elem.find('general_description'))
            self.source = Source(elem.find('source'))
            self.target = Target(elem.find('target'))
            self.mapping_info = MappingInfo(elem.find('mapping_info'))
            self.example_data_info = ExampleDataInfo(elem.find('example_data_info'))
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.title.serialize(SubElement(elem, 'title'))
            self.general_description.serialize(
                SubElement(elem, 'general_description'))
            self.source.serialize(SubElement(elem, 'source'))
            self.target.serialize(SubElement(elem, 'target'))
            self.mapping_info.serialize(SubElement(elem, 'mapping_info'))
            self.example_data_info.serialize(SubElement(elem, 'example_data_info'))
        return elem


class Namespace(X3Base):
    '''Model class for namespace elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        super().deserialize(elem)

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

    def set(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri
        return self

class Domain(X3Base):
    '''Model class for domain elements''' 
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.sourceNode = SourceNode()
        self.targetNode = TargetNode()
        self.comments = []
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

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.sourceNode = SourceNode(elem.find('source_node'))
            self.targetNode = TargetNode(elem.find('target_node'))
            self.comments = [Comment(x) for x in elem.findall('comments/comment')]
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.sourceNode.serialize(SubElement(elem, 'source_node'))
            self.targetNode.serialize(SubElement(elem, 'target_node'))
            if self.comments:
                cs = SubElement(elem, 'comments')
                for x in self.comments:
                    x.serialize(SubElement(cs, 'comment'))
        return elem


class NR(X3Base):
    '''Model class for node-relation pair elements'''
    def __init__(self, node: SimpleText, relation: SimpleText) -> None:
        self.node = node
        self.relation = relation

    def serialize(self, elem: Element):
        if NN(elem):
            self.node.serialize(SubElement(elem, 'node'))
            self.relation.serialize(SubElement(elem, 'relation'))
        return self

    def deserialize(self, elem: Element):
        if NN(elem):
            self.node = SimpleText(elem.find('node'))
            self.relation = SimpleText(elem.find('relation'))
        return elem

    @staticmethod
    def create(node: str = '', relation: str = ''):
        return NR(SimpleText(text=node), SimpleText(text=relation))


class SourceRelation(X3Base):
    '''Model class for source relation elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.relation = SimpleText()
        self.nodes = []
        self.deserialize(elem)

    @property
    def path(self): return self.relation.text

    @path.setter
    def path(self, value):  self.relation.text = value

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            rs = elem.findall('relation')
            ns = elem.findall('node')
            self.relation = SimpleText(rs.pop(0))
            self.nodes = [NR(SimpleText(n), SimpleText(r)) for n, r in zip(ns, rs)]
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.relation.serialize(SubElement(elem, 'relation'))
            for ns in self.nodes:
                ns.relation.serialize(SubElement(elem, 'relation'))
                ns.node.serialize(SubElement(elem, 'node'))
        return elem

    @staticmethod
    def create(s: str = ''):
        sr = SourceRelation()
        sr.relation = SimpleText.create(s)
        return sr


class Path(X3Base,Predicate):
    '''Model class for path elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.sourceRelation = SourceRelation()
        self.targetRelation = TargetRelation()
        self.comments = []
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

    def validate(self,elem):
        return self.targetRelation.validate(elem)

    def addComment(self, s):
        self.comments.append(Comment.create(s))

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.sourceRelation = SourceRelation(elem.find('source_relation'))
            self.targetRelation = TargetRelation(elem.find('target_relation'))
            self.comments = [Comment(x) for x in elem.findall('comments/comment')]
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.sourceRelation.serialize(SubElement(elem, 'source_relation'))
            self.targetRelation.serialize(SubElement(elem, 'target_relation'))
            if self.comments:
                cs = SubElement(elem, 'comments')
                for x in self.comments:
                    x.serialize(SubElement(cs, 'comment'))
        return elem

class Range(X3Base):
    '''Model class for range elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.sourceNode = SourceNode()
        self.targetNode = TargetNode()
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

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.sourceNode = SourceNode(elem.find('source_node'))
            self.targetNode = TargetNode(elem.find('target_node'))
        return self
    
    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.sourceNode.serialize(SubElement(elem, 'source_node'))
            self.targetNode.serialize(SubElement(elem, 'target_node'))
        return elem


class Link(X3Base,Predicate):
    '''Model class for link elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.setAttr('skip', 'false')
        self.path = Path()
        self.range = Range()
        self.deserialize(elem)

    @property
    def skip(self): return self.getAttr('skip')

    @skip.setter
    def skip(self, value):  self.setAttr('skip', value)

    def set(self, path, relationship, entity):
        self.path.set(path, relationship)
        self.range.set(path, entity)

    def validate(self,elem):
        return self.path.validate(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.path = Path(elem.find('path'))
            self.range = Range(elem.find('range'))
        return self
    
    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.path.serialize(SubElement(elem, 'path'))
            self.range.serialize(SubElement(elem, 'range'))
        return elem


class Mapping(X3Base):
    '''Model class for mapping elements'''
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.setAttr('skip', 'false')
        self.domain = Domain()
        self.links = []
        self.deserialize(elem)

    @property
    def skip(self): return self.getAttr('skip')

    @skip.setter
    def skip(self, value):  self.setAttr('skip', value)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.domain = Domain(elem.find('domain'))
            self.links = [Link(x) for x in elem.findall('link')]
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.domain.serialize(SubElement(elem, 'domain'))
            for link in self.links:
                link.serialize(SubElement(elem, 'link'))
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
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.namespaces = []
        self.mappings = []
        self.info = Info()
        self.deserialize(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.info = Info(elem.find('info'))
            self.namespaces = [Namespace(x) for x in elem.findall('./namespaces/namespace')]
            self.mappings = [Mapping(x) for x in elem.findall('./mappings/mapping')]
        return self
    
    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.info.serialize(SubElement(elem, 'info'))
            nss = SubElement(elem, 'namespaces')
            for m in self.namespaces:
                m.serialize(SubElement(nss, 'namespace'))
            mss = SubElement(elem, 'mappings')
            for m in self.mappings:
                m.serialize(SubElement(mss, 'mapping'))
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
    def __init__(self, elem: Element | None = None):
        super().__init__()
        self.mode = ''
        self.deserialize(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            if not elem.find('constant') is None:
                self.mode = 'constant'
            if not elem.find('language') is None:
                self.mode = 'language'
            if not elem.find('description') is None:
                self.mode = 'description'
        return self
    
    def serialize(self, elem: Element):
        if NN(elem):
            match self.mode:
                case 'constant':
                    SubElement(elem, 'constant')
                case 'language':
                    SubElement(elem, 'language')
                case 'description':
                    SubElement(elem, 'description')
        return elem


class Relationship(SimpleText):
    '''Model class for relationship elements'''
    pass


class Entity(X3Base):
    '''Model class for entity elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__()
        self.type = ''
        self.instance_info = []
        self.instance_generator = []
        self.label_generator = []
        self.additional = []
        self.deserialize(elem)

    def deserialize(self, elem: Element | None):
        if NN(elem):
            super().deserialize(elem)
            self.type = getText(elem.find('type'))
            self.instance_info = [InstanceInfo(x) for x in elem.findall('instance_info')]
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            t = SubElement(elem, 'type')
            t.text = self.type
            for x in self.instance_info:
                x.serialize(SubElement(elem, 'instance_info'))
        return elem

class TargetExtension(Serializer):
    '''Model class for TargetExtenion elements'''
    def __init__(self, entity: Entity, relationShip: Relationship) -> None:
        self.entity = entity
        self.relationship = relationShip

    def deserialize(self, elem: Element):
        if NN(elem):
            self.entity = Entity(elem.find('entity'))
            self.relationship = Relationship(elem.find('relationship'))
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            self.entity.serialize(SubElement(elem, 'entity'))
            self.relationship.serialize(SubElement(elem, 'relationship'))
        return elem

class TargetRelation(X3Base,Predicate):
    '''Model class for target relation type elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__()
        self.condition = PredicateVariant()
        self.relationship = Relationship(None)
        self.extensions = []
        self.deserialize(elem)

    @property
    def entity(self): return self.relationship.text

    @property
    def ifops(self): return self.condition.op.ifs

    @property
    def N(self): return len(self.ifops)

    @entity.setter
    def entity(self, value):  self.relationship.text = value

    def delOp(self,n):
        if n in range(0,self.N):
            self.ifops.pop(n)

    def setOp(self,n,op):
        if n in range(0,self.N):
            self.ifops[n] = op

    def appendOp(self,op):
        self.ifops.append(op) 
  

    def validate(self,elem): 
        return self.condition.validate(elem)

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.relationship.serialize(SubElement(elem, 'relationship'))
            self.condition.serialize(SubElement(elem, 'if'))
            for x in self.extensions:
                x.entity.serialize(SubElement(elem, 'entity'))
                x.relationship.serialize(SubElement(elem, 'relationship'))
        return elem

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.condition = PredicateVariant(elem.find('if'))
            rsElems = elem.findall('relationship')
            if len(rsElems) > 0:
                self.relationship = Relationship(rsElems.pop())
                enElems = elem.findall('entity')
                if len(enElems) == len(rsElems):
                    self.extensions = [TargetExtension(Entity(e), Relationship(r)) for e, r in zip(enElems, rsElems)]
        return self

class TargetNode(X3Base):
    '''Model class for target node elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__()
        self.entity = Entity()
        self.condition = PredicateVariant()
        self.deserialize(elem)

    def deserialize(self, elem: Element):
        if NN(elem):
            super().deserialize(elem)
            self.entity = Entity(elem.find('entity'))
            self.condition = PredicateVariant(elem.find('if'))
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            self.entity.serialize(SubElement(elem, 'entity'))
            self.condition.serialize(SubElement(elem, 'if'))
        return elem


class SourceNode(SimpleText):
    '''Model class for source node elements'''
    pass


class ComposedPredicate(X3Base,Predicate):
    '''Model class for logical operation elements'''
    def __init__(self, elem: Element | None = None, tag: str = '') -> None:
        X3Base.__init__(self)
        self.tag = tag
        self.xpath = ''
        self.value=''
        self.predicates = []
        self.deserialize(elem)

    @classmethod
    def byValues(cls, xp, val):
        t = cls(None)
        if isinstance(xp,str) and isinstance(val,str):
            t.xpath = xp
            t.value = val
        return t
    
    def append(self, objIf):
        if isinstance(objIf,PredicateVariant):
            self.predicates.append(objIf)
            return objIf
    
    def reset(self):
        self.xpath = ''
        self.value = ''
        self.predicates = []

    def deserialize(self, elem: Element | None):
        if NN(elem):
            X3Base.deserialize(self,elem)
            self.reset()
            if children := elem.findall('if'):
                self.predicates = [PredicateVariant(x) for x in children]
            else:
                self.xpath = elem.text
                self.value = elem.get('value','')
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            X3Base.serialize(self,elem)
            if self.predicates:
                for x in self.predicates:
                    x.serialize(SubElement(elem, 'if'))
            else:
                if self.xpath: elem.text = self.xpath
                if self.value: elem.set('value',self.value)
        return elem
    
    def validPath(self,elem):
        if NN(elem):
            if self.xpath.endswith('/text()'):
                correctedPath = self.xpath.replace('/text()', '')
                pathValues = [x.text for x in elem.findall(correctedPath)]
                return self.value in pathValues
            elif self.xpath == 'lido:type':
                return elem.get('type','') == self.value #TODO Tests
            else:
                return True
        return False

    def validate(self,elem):
        return self.validPath(elem)


class Not(ComposedPredicate):
    '''Model class for not elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'not')


class And (ComposedPredicate):
    '''Model class for and elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'and')

    def validate(self,elem):
        if NN(elem):
            if self.predicates:
                return all([x.validate(elem) for x in self.predicates])
            return self.validPath(elem)
        return False

class Or(ComposedPredicate):
    '''Model class for or elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'or')

    def validate(self,elem):
        if NN(elem):
            if self.predicates:
                validFlags = [x.validate(elem) for x in self.predicates]
                return any(validFlags)
            return self.validPath(elem)
        return False

class ExactMatch(ComposedPredicate):
    '''Model class for exact-match elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'exact_match')


class Broader(ComposedPredicate):
    '''Model class for broader elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'broader')


class Narrower(ComposedPredicate):
    '''Model class for narrower elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'narrower')


class Equals(ComposedPredicate):
    '''Model class for equals elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'equals')


class Exists(ComposedPredicate):
    '''Model class for exists elements'''
    def __init__(self, elem: Element | None = None) -> None:
        super().__init__(elem, 'exists')


class PredicateVariant(X3Base, Predicate):
    '''Model class for conditions type elements'''
    def __init__(self, elem: Element | None = None, **kw) -> None:
        X3Base.__init__(self)
        self.predicate = Or()
        if NN(elem):
            self.deserialize(elem)

    @classmethod
    def withOp(cls, predicate):
        t = cls(None)
        if isinstance(predicate,Predicate):
            t.predicate = predicate
        return t

    @property
    def op(self): return self.predicate

    @op.setter
    def op(self, value):
        if isinstance(value, ComposedPredicate):
            self.predicate = value

    def deserialize(self, elem: Element | None):
        if NN(elem):
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
        return self

    def serialize(self, elem: Element):
        if NN(elem):
            super().serialize(elem)
            if self.op:
                self.op.serialize(SubElement(elem, self.op.tag))
        return elem

    def validate(self, elem):
        if NN(self.op) and NN(elem):
            return self.op.validate(elem)
        return False
        

def loadX3ml(filePath='defaultMapping.x3ml'):
    '''Loads an X3ML model from a file'''
    model = X3ml()
    tree = parse(filePath)
    model.deserialize(tree.getroot())
    return model


def storeX3ml(model: X3ml, filePath='download.x3ml'):
    '''Stores an X3ML model to a file'''
    root = model.serialize(Element('x3ml'))
    indent(root)
    tree = ElementTree(root)
    tree.write(filePath, encoding='utf-8', xml_declaration=True)
    return filePath


if __name__ == "__main__":
    loadX3ml()
