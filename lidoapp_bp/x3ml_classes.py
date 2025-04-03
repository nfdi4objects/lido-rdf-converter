from xml.etree.ElementTree import Element, ElementTree, indent, SubElement, parse,tostring
import json

class Predicate():
    ''' Base precidate class'''

    def validate(self,elem):
        '''Validate interface'''
        return False

class JSON_Serializer:
    ''' Base class for JSON serialization'''
    def toJSON(self, indent=2):
        return json.dumps(self, default=lambda o: o.__dict__,  sort_keys=True, indent=int(indent))

def NN(elem: Element):
    ''' None none: returns True if elem is not None '''
    return not elem is None

def getText(elem: Element | None) -> str:
    ''' Returns the text of an element if exits (else an empty string)'''
    if NN(elem):
        return str(elem.text)
    return ''

class X3Base(JSON_Serializer):
    ''' Base for X3ML classes, handles attributes (dicts)'''

    counter = 0
    ''' Class counter'''

    def __init__(self):
        ''' Creates an XBase object with attributes'''
        self.attributes = {} 
        X3Base.counter += 1

    def __del__(self):
        X3Base.counter -= 1

    def __getitem__(self,key):
        '''Enables attribute access by key'''
        return self.attributes[key]
    
    def __setitem__(self, key, value):
        '''Enables attribute access by key'''
        self.attributes[key] = value

    def __str__(self):
        '''Returns a simple string conversion'''
        return f"{ self.__class__.__name__}"

    def deserialize(self, elem: Element):
        '''De-serializes this object from a XML element. Returns self.'''
        if NN(elem):
            self.attributes = elem.attrib
        return self

    def serialize(self, elem: Element) -> Element:
        '''Serializes this object into a XML element. Returns the element.'''
        if NN(elem):
            elem.attrib = self.attributes
        return elem

    def to_str(self):
        return tostring(self.serialize(Element('x3ml')))

    @classmethod
    def from_serial(cls, elem: Element,*args,**kw):
        '''Constructs an object from an XML element'''
        obj = cls(*args,**kw)
        if NN(elem):
            obj.deserialize(elem)
        return obj

class SimpleText(X3Base):
    '''Class for simple text elements'''
    def __init__(self, text=""):
        super().__init__()
        self.text = text

    def alias(self):
        '''Returns an alias of the text'''
        return self.text.replace('lido:', '')
    
    def deserialize(self, elem: Element):
        super().deserialize(elem)
        if NN(elem.text):
            self.text = elem.text
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        elem.text = self.text
        return elem

    def __str__(self):
        return f"{ self.__class__.__name__}\t{self.text}"

class Source(X3Base):
    '''Class for source-schema elements'''
    def __init__(self,text:str = ''):
        super().__init__()
        self.source_schema = SimpleText(text)

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.source_schema = SimpleText.from_serial(elem.find('source_info/source_schema'))
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        subElem = SubElement(elem, 'source_info')
        self.source_schema.serialize(SubElement(subElem, 'source_schema'))
        return elem

    def set(self, schema):
        self.source_schema.text = schema

class Target(X3Base):
    '''Class for target-schema elements'''
    def __init__(self, text:str = ''):
        super().__init__()
        self.target_schema = SimpleText(text)

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.target_schema = SimpleText.from_serial(elem.find('target_info/target_schema'))
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        subElem = SubElement(elem, 'target_info')
        self.target_schema.serialize(SubElement(subElem, 'target_schema'))
        return elem

    def set(self, schema):
        self.target_schema.text = schema

class MappingInfo(X3Base):
    '''Class for mapping-info elements'''
    def __init__(self):
        pass

    def deserialize(self, elem: Element):
        return self

    def serialize(self, elem: Element):
        SubElement(elem, 'mapping_created_by_org')
        SubElement(elem, 'mapping_created_by_person')
        SubElement(elem, 'in_collaboration_with')
        return elem

class Comment(X3Base):
    '''Class for comment elements'''
    def __init__(self, text:str=''):
        super().__init__()
        self.rationale = SimpleText(text)

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.rationale = SimpleText.from_serial(elem.find('rationale'))
        return self

    def serialize(self, elem: Element):
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

class ExampleDataInfo(X3Base):
    '''Class for example-data elements'''
    def __init__(self):
        pass

    def serialize(self, elem: Element):
        SubElement(elem, 'example_data_from')
        SubElement(elem, 'example_data_contact_person')
        SubElement(elem, 'example_data_source_record')
        SubElement(elem, 'generator_policy_info')
        SubElement(elem, 'example_data_target_record')
        SubElement(elem, 'thesaurus_info')
        return elem

class Info(X3Base):
    '''Class for info-elements'''
    def __init__(self):
        super().__init__()
        self.title = SimpleText()
        self.general_description = SimpleText()
        self.source = Source()
        self.target = Target()
        self.mapping_info = MappingInfo()
        self.example_data_info = ExampleDataInfo()

    @property
    def sSchema(self): return self.source.source_schema.text

    @sSchema.setter
    def sSchema(self, value): self.source.source_schema.text = value

    @property
    def tSchema(self): return self.target.target_schema.text

    @tSchema.setter
    def tSchema(self, value): self.target.target_schema.text = value

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.title = SimpleText.from_serial(elem.find('title'))
        self.general_description = SimpleText.from_serial(elem.find('general_description'))
        self.source = Source.from_serial(elem.find('source'))
        self.target = Target.from_serial(elem.find('target'))
        self.mapping_info = MappingInfo.from_serial(elem.find('mapping_info'))
        self.example_data_info = ExampleDataInfo.from_serial(elem.find('example_data_info'))
        return self

    def serialize(self, elem: Element):
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
    '''Class for namespace elements'''
    def __init__(self):
        super().__init__()

    @property
    def prefix(self): return self['prefix']

    @prefix.setter
    def prefix(self, value): self['prefix']= value

    @property
    def uri(self): return self['uri']

    @uri.setter
    def uri(self, value): self['uri']= value

    def __eq__(self, other):
        return self.prefix == other.prefix

    def set(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri
        return self

class Domain(X3Base):
    '''Class for domain elements''' 
    def __init__(self):
        super().__init__()
        self.sourceNode = SourceNode()
        self.targetNode = TargetNode()
        self.comments = []

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
        super().deserialize(elem)
        self.sourceNode = SourceNode.from_serial(elem.find('source_node'))
        self.targetNode = TargetNode.from_serial(elem.find('target_node'))
        self.comments = [Comment.from_serial(x) for x in elem.findall('comments/comment')]
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        self.sourceNode.serialize(SubElement(elem, 'source_node'))
        self.targetNode.serialize(SubElement(elem, 'target_node'))
        if self.comments:
            cs = SubElement(elem, 'comments')
            for x in self.comments:
                x.serialize(SubElement(cs, 'comment'))
        return elem


class NR(X3Base):
    '''Class for node-relation pair elements'''
    def __init__(self, node: SimpleText, relation: SimpleText) -> None:
        self.node = node
        self.relation = relation

    def serialize(self, elem: Element):
        self.node.serialize(SubElement(elem, 'node'))
        self.relation.serialize(SubElement(elem, 'relation'))
        return self

    def deserialize(self, elem: Element):
        self.node = SimpleText.from_serial(elem.find('node'))
        self.relation = SimpleText.from_serial(elem.find('relation'))
        return elem

    @classmethod
    def create(cls,node: str = '', relation: str = ''):
        return cls(SimpleText(node), SimpleText(relation))


class SourceRelation(X3Base):
    '''Class for source relation elements'''
    def __init__(self,text:str=''):
        super().__init__()
        self.relation = SimpleText(text)
        self.nodes = []

    @property
    def path(self): return self.relation.text

    @path.setter
    def path(self, value): self.relation.text = value

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        rs = elem.findall('relation')
        ns = elem.findall('node')
        self.relation = SimpleText.from_serial(rs.pop(0))
        self.nodes = [NR(SimpleText.from_serial(n), SimpleText.from_serial(r)) for n, r in zip(ns, rs)]
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        self.relation.serialize(SubElement(elem, 'relation'))
        for ns in self.nodes:
            ns.relation.serialize(SubElement(elem, 'relation'))
            ns.node.serialize(SubElement(elem, 'node'))
        return elem

class Path(X3Base,Predicate):
    '''Class for path elements'''
    def __init__(self):
        X3Base.__init__(self)
        self.sourceRelation = SourceRelation()
        self.targetRelation = TargetRelation()
        self.comments = []

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
        self.comments.append(Comment(s))

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.sourceRelation = SourceRelation.from_serial(elem.find('source_relation'))
        self.targetRelation = TargetRelation.from_serial(elem.find('target_relation'))
        self.comments = [Comment.from_serial(x) for x in elem.findall('comments/comment')]
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        self.sourceRelation.serialize(SubElement(elem, 'source_relation'))
        self.targetRelation.serialize(SubElement(elem, 'target_relation'))
        if self.comments:
            cs = SubElement(elem, 'comments')
            for x in self.comments:
                x.serialize(SubElement(cs, 'comment'))
        return elem

class Range(X3Base):
    '''Class for range elements'''
    def __init__(self):
        super().__init__()
        self.sourceNode = SourceNode()
        self.targetNode = TargetNode(enable=True)

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
        super().deserialize(elem)
        self.sourceNode = SourceNode.from_serial(elem.find('source_node'))
        self.targetNode = TargetNode.from_serial(elem.find('target_node'))
        return self
    
    def serialize(self, elem: Element):
        super().serialize(elem)
        self.sourceNode.serialize(SubElement(elem, 'source_node'))
        self.targetNode.serialize(SubElement(elem, 'target_node'))
        return elem

class Link(X3Base,Predicate):
    '''Class for link elements'''
    def __init__(self):
        X3Base.__init__(self)
        self['skip'] ='false'
        self.path = Path()
        self.range = Range()

    def set(self, path, relationship, entity):
        self.path.set(path, relationship)
        self.range.set(path, entity)

    def validate(self,elem):
        return self.path.validate(elem)

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.path = Path.from_serial(elem.find('path'))
        self.range = Range.from_serial(elem.find('range'))
        return self
    
    def serialize(self, elem: Element):
        super().serialize(elem)
        self.path.serialize(SubElement(elem, 'path'))
        self.range.serialize(SubElement(elem, 'range'))
        return elem


class Mapping(X3Base):
    '''Class for mapping elements'''
    def __init__(self):
        super().__init__()
        self['skip']= 'false'
        self.domain = Domain()
        self.links = []

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.domain = Domain.from_serial(elem.find('domain'))
        self.links = [Link.from_serial(x) for x in elem.findall('link')]
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        self.domain.serialize(SubElement(elem, 'domain'))
        for link in self.links:
            link.serialize(SubElement(elem, 'link'))
        return elem

    def label(self, n=0):
        return f"Mapping {n}: Domain={self.domain.sourceNode.text}"

class X3ml(X3Base):
    '''Class for X3ML elements'''
    def __init__(self):
        super().__init__()
        self.namespaces = []
        self.mappings = []
        self.info = Info()

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.info = Info.from_serial(elem.find('info'))
        self.namespaces = [Namespace.from_serial(x) for x in elem.findall('./namespaces/namespace')]
        self.mappings = [Mapping.from_serial(x) for x in elem.findall('./mappings/mapping')]
        return self
    
    def serialize(self, elem: Element):
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
    '''Class for label generator elements'''
    def __init__(self, val=''):
        super().__init__()
        self.value: str = val


class Instance_Generator(X3Base):
    '''Class for instance generator elements'''
    def __init__(self, val=''):
        super().__init__()
        self.value: str = val


class InstanceInfo(X3Base):
    '''Class for instance info elements'''
    def __init__(self):
        super().__init__()
        self.mode = ''
 
    def deserialize(self, elem: Element):
        if not elem.find('constant') is None:
            self.mode = 'constant'
        if not elem.find('language') is None:
            self.mode = 'language'
        if not elem.find('description') is None:
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


class Relationship(SimpleText):
    '''Class for relationship elements'''
    pass


class Entity(X3Base):
    '''Class for entity elements'''
    def __init__(self) -> None:
        super().__init__()
        self.type = ''
        self.instance_info = []
        self.instance_generator = []
        self.label_generator = []
        self.additional = []

    def deserialize(self, elem: Element | None):
        super().deserialize(elem)
        self.type = getText(elem.find('type'))
        self.instance_info = [InstanceInfo.from_serial(x) for x in elem.findall('instance_info')]
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        t = SubElement(elem, 'type')
        t.text = self.type
        for x in self.instance_info:
            x.serialize(SubElement(elem, 'instance_info'))
        return elem

class TargetExtension(JSON_Serializer):
    '''Class for TargetExtenion elements'''
    def __init__(self, entity: Entity, relationShip: Relationship) -> None:
        self.entity = entity
        self.relationship = relationShip

    def deserialize(self, elem: Element):
        self.entity = Entity.from_serial(elem.find('entity'))
        self.relationship = Relationship.from_serial(elem.find('relationship'))
        return self

    def serialize(self, elem: Element):
        self.entity.serialize(SubElement(elem, 'entity'))
        self.relationship.serialize(SubElement(elem, 'relationship'))
        return elem

class TargetRelation(X3Base,Predicate):
    '''Class for target relation type elements'''
    def __init__(self) -> None:
        X3Base.__init__(self)
        self.condition = PredicateVariant()
        self.relationship = Relationship()
        self.extensions = []

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
        super().serialize(elem)
        self.relationship.serialize(SubElement(elem, 'relationship'))
        self.condition.serialize(SubElement(elem, 'if'))
        for x in self.extensions:
            x.entity.serialize(SubElement(elem, 'entity'))
            x.relationship.serialize(SubElement(elem, 'relationship'))
        return elem

    def deserialize(self, elem: Element):
        super().deserialize(elem)
        self.condition = PredicateVariant.from_serial(elem.find('if'))
        rsElems = elem.findall('relationship')
        if len(rsElems) > 0:
            self.relationship = Relationship.from_serial(rsElems.pop())
            enElems = elem.findall('entity')
            if len(enElems) == len(rsElems):
                self.extensions = [TargetExtension(Entity.from_serial(e), Relationship.from_serial(r)) for e, r in zip(enElems, rsElems)]
        return self

class TargetNode(X3Base):
    '''Class for target node elements'''
    def __init__(self, **kw) -> None:
        super().__init__()
        self.entity = Entity()
        self.condition = PredicateVariant()
        self.enableC = kw.get('enable', True)

    def deserialize(self, elem: Element,**kw):
        super().deserialize(elem)
        self.entity = Entity.from_serial(elem.find('entity'))
        if bool(self.enableC):
            self.condition = PredicateVariant.from_serial(elem.find('if'))
        else:
            self.condition = PredicateVariant()
        return self

    def serialize(self, elem: Element):
        super().serialize(elem)
        self.entity.serialize(SubElement(elem, 'entity'))
        self.condition.serialize(SubElement(elem, 'if'))
        return elem


class SourceNode(SimpleText):
    '''Class for source node elements'''
    pass


class ComposedPredicate(X3Base,Predicate):
    '''Class for logical operation elements'''
    def __init__(self, tag: str = '') -> None:
        X3Base.__init__(self)
        self.tag = tag
        self.xpath = ''
        self.value=''
        self.predicates = []

    @classmethod
    def byValues(cls, xp, val):
        t = cls()
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
        X3Base.deserialize(self,elem)
        self.reset()
        if children := elem.findall('if'):
            self.predicates = [PredicateVariant.from_serial(x) for x in children]
        else:
            self.xpath = elem.text
            self.value = elem.get('value','')
        return self

    def serialize(self, elem: Element):
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
    '''Class for not elements'''
    def __init__(self) -> None:
        super().__init__('not')


class And (ComposedPredicate):
    '''Class for and elements'''
    def __init__(self) -> None:
        super().__init__('and')

    def validate(self,elem):
        if NN(elem):
            if self.predicates:
                return all([x.validate(elem) for x in self.predicates])
            return self.validPath(elem)
        return False

class Or(ComposedPredicate):
    '''Class for or elements'''
    def __init__(self) -> None:
        super().__init__('or')

    def validate(self,elem):
        if NN(elem):
            if self.predicates:
                validFlags = [x.validate(elem) for x in self.predicates]
                return any(validFlags)
            return self.validPath(elem)
        return False

class ExactMatch(ComposedPredicate):
    '''Class for exact-match elements'''
    def __init__(self) -> None:
        super().__init__('exact_match')


class Broader(ComposedPredicate):
    '''Class for broader elements'''
    def __init__(self) -> None:
        super().__init__('broader')


class Narrower(ComposedPredicate):
    '''Class for narrower elements'''
    def __init__(self) -> None:
        super().__init__('narrower')


class Equals(ComposedPredicate):
    '''Class for equals elements'''
    def __init__(self) -> None:
        super().__init__('equals')


class Exists(ComposedPredicate):
    '''Class for exists elements'''
    def __init__(self) -> None:
        super().__init__('exists')


class PredicateVariant(X3Base, Predicate):
    '''Class for conditions type elements'''
    def __init__(self, **kw) -> None:
        X3Base.__init__(self)
        self.predicate = Or()

    @classmethod
    def from_op(cls, predicate):
        obj = cls()
        if isinstance(predicate,Predicate):
            obj.predicate = predicate
        return obj

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
                    self.op = cls.from_serial(st)

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
    tree = parse(filePath)
    return X3ml.from_serial(tree.getroot())

def storeX3ml(model: X3ml, filePath='download.x3ml'):
    '''Stores an X3ML model to a file'''
    root = model.serialize(Element('x3ml'))
    indent(root)
    tree = ElementTree(root)
    tree.write(filePath, encoding='utf-8', xml_declaration=True)
    return filePath

if __name__ == "__main__":
    loadX3ml()
