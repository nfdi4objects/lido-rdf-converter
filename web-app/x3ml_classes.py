import xml.etree.ElementTree as ET

def NN(elem:ET.Element): 
    return  not elem is None

def getText(elem:ET.Element|None) ->str:
    if NN(elem):
        return str(elem.text)
    return '' 

class Attribute():
    def __init__(self, key:str, value:str=''):
        self.key = key
        self.value = value
        
    def __str__(self):
        return f"{self.key}:{self.value}"
    
def njoin(v,sep='\n'):
    return sep.join(filter(None,v))

def toStrV(v,indent=0):
    return njoin([x.toStr(indent) for x in v])

Attributes = list[Attribute]

class X3Base():
    counter = 0
    def __init__(self,elem:ET.Element|None=None):
        self.attributes = []
        if NN(elem): self.deserialize(elem)
        X3Base.counter += 1

    def __del__(self):
        X3Base.counter -= 1

    def toStr(self, indent=0):
        return f"{'   '*indent}{self}"

    def __str__(self):
        return f"{ self.__class__.__name__}"
   
        
    def getAttr(self, name=None):
        if name:
            return next((x.value for x in self.attributes if x.key == name), '')
        else:
            return njoin([x.value for x in self.attributes],',')

    def setAttr(self, name,value):
        if a := next(x for x in self.attributes if x.key == name):
            a.value = value

    def deserialize(self, elem:ET.Element):
        for k,v in elem.attrib.items():
            self.attributes.append(Attribute(k,v))
        return self

    def serialize(self, elem:ET.Element):
        for attr in self.attributes:
            if attr.value:
                elem.attrib[attr.key] = attr.value
        return elem

class Namespace(X3Base):
    def __init__(self,elem:ET.Element|None = None):
        super().__init__(elem)
        self.attributes = [Attribute('prefix'),Attribute('uri')]

    def prefix(self): 
        return self.getAttr('prefix')

    def uri(self): 
        return self.getAttr('uri')

    def __eq__(self, other): 
        return self.prefix()==other.prefix()

    def toStr(self, indent = 0): 
        return f"{super().toStr(indent)}: {self.getAttr()}"
    
    def set(self, p,u):
        self.setAttr('prefix',p)
        self.setAttr('uri',u)
        return self
 
class Domain(X3Base):
    def __init__(self, elem: ET.Element|None=None):
        super().__init__(elem)
        self.sourceNode = SourceNode()
        self.targetNode = DomainTargetNodeType()
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.sourceNode = SourceNode(elem.find('source_node'))
        self.targetNode = DomainTargetNodeType(elem.find('target_node'))

    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.sourceNode.serialize(ET.SubElement(elem,'source_node'))
        self.targetNode.serialize(ET.SubElement(elem,'target_node'))

    def toStr(self, indent = 0):
        me = f"{super().toStr(indent)}: { self.getAttr()}"
        s_s = self.sourceNode.toStr(indent+1)
        t_s = self.targetNode.toStr(indent+1)
        return njoin([ me,s_s,t_s])

class NR():
    def __init__(self, node:str, relation:str) ->None:
        self.node = node
        self.relation = relation

class SourceRelation(X3Base):
    def __init__(self, elem : ET.Element|None = None):
        super().__init__(elem)
        self.relation = ''
        self.nodes = []
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        gt = lambda x: getText(x)
        rs = elem.findall('relation')
        ns = elem.findall('node')

        self.relation = gt(rs.pop(0))
        self.nodes = [(NR(gt(n),gt(r))) for n,r in zip(ns,rs)]

    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        elem.text =self.relation
        for ns in self.nodes:
            r =ET.SubElement(elem,'relation')
            r.text = ns.relation
            n =ET.SubElement(elem,'node')
            n.text = ns.node
        return elem

    def toStr(self, indent = 0):
        return f"{super().toStr(indent)} : {self.relation}"
  
class Path(X3Base):
    def __init__(self, elem : ET.Element|None = None):
        super().__init__(elem)
        self.sourceRelation = SourceRelation()
        self.targetRelation = TargetRelationType()
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.sourceRelation = SourceRelation(elem.find('source_relation'))
        self.targetRelation = TargetRelationType(elem.find('target_relation'))
 
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.sourceRelation.serialize(ET.SubElement(elem,'source_relation'))
        self.targetRelation.serialize(ET.SubElement(elem,'target_relation'))
        return elem

    def toStr(self, indent = 0):
        me = super().toStr(indent)
        s_s = self.sourceRelation.toStr(indent+1)
        t_s = self.targetRelation.toStr(indent+1)
        return njoin([me, s_s, t_s])

class Range(X3Base):
    def __init__(self, elem : ET.Element|None = None):
        super().__init__(elem)
        self.sourceNode = SourceNode()
        self.targetNode = TargetNode()
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.sourceNode = SourceNode(elem.find('source_node'))
        self.targetNode = TargetNode(elem.find('target_node'))

    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.sourceNode.serialize(ET.SubElement(elem,'source_node'))
        self.targetNode.serialize(ET.SubElement(elem,'target_node'))
        return elem

    def toStr(self, indent = 0):
        me = super().toStr(indent)
        s_s = self.sourceNode.toStr(indent+1)
        t_s = self.targetNode.toStr(indent+1)
        return njoin([me, s_s, t_s])

class Link(X3Base):
    def __init__(self, elem : ET.Element|None = None):
        super().__init__(elem)
        self.path = Path()
        self.range = Range()
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.path = Path(elem.find('path'))
        self.range = Range(elem.find('range'))
 
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.path.serialize(ET.SubElement(elem,'path'))
        self.range.serialize(ET.SubElement(elem,'range'))
        return elem

    def toStr(self, indent = 0):
        me = f"{super().toStr(indent)}: {self.getAttr()}"
        p_s = self.path.toStr(indent+1)
        r_s = self.range.toStr(indent+1)
        return njoin([me, p_s, r_s])
 
class Mapping(X3Base):
    def __init__(self, elem : ET.Element|None = None):
        super().__init__(elem)
        self.domain = Domain()
        self.links = []
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.domain = Domain(elem.find('domain'))
        self.links = [Link(x) for x in elem.findall('link')]
        return self
 
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.domain.serialize(ET.SubElement(elem,'domain'))
        for link in self.links:
            link.serialize(ET.SubElement(elem,'link'))
        return elem

    def toStr(self, indent = 0):
        me = f"{super().toStr(indent)}: {self.getAttr()}"
        d_s = self.domain.toStr(indent+1)
        l_s = toStrV(self.links, indent+1)
        return njoin([me, d_s, l_s])
    
    def label(self, n=0):
        return f"Mapping {n}: Domain={self.domain.sourceNode.text}"


class X3ml(X3Base):
    def __init__(self, elem: ET.Element|None = None):
        super().__init__(elem)
        self.namespaces = []
        self.mappings = []
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.namespaces = [Namespace(x) for x in elem.findall('./namespaces/namespace') ]
        self.mappings = [Mapping(x) for x in elem.findall('./mappings/mapping') ]
 
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        nss = ET.SubElement(elem,'namespaces')
        for m in self.namespaces:
            m.serialize(ET.SubElement(nss,'namespace'))
        mss = ET.SubElement(elem,'mappings')
        for m in self.mappings:
            m.serialize(ET.SubElement(mss,'mapping'))
        return elem

    def toStr(self, indent=0):
        me = super().toStr(indent)
        n_s = toStrV(self.namespaces, indent+1)
        m_s = toStrV(self.mappings, indent+1)
        return njoin([me,n_s,m_s])

class LabelGenerator(X3Base):
    def __init__(self,val=''):
        super().__init__()
        self.value:str = val

class Instance_Generator(X3Base):
    def __init__(self,val=''):
        super().__init__()
        self.value:str = val

class InstanceInfo(X3Base):
    def __init__(self,elem: ET.Element|None = None):
        super().__init__(elem)
        self.mode = ''
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        if not elem.find('constant') is None:
            self.mode = 'constant'
        if not elem.find('language') is None:
            self.mode = 'language'
        if not elem.find('description') is None:
            self.mode = 'description'
 
class Relationship():
    def __init__(self,elem : ET.Element|None) -> None:
        self.value = getText(elem)

    def serialize(self, elem:ET.Element):
        elem.text = self.value

class Entity(X3Base):
    def __init__(self,elem : ET.Element|None = None) -> None:
        super().__init__()
        self.value = ''
        self.instance_info = []
        self.instance_generator = []
        self.label_generator = []
        self.additional = []
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element|None):
        super().deserialize(elem)
        if elem:
            self.value = getText(elem.find('type'))
            self.instance_info = [InstanceInfo(x) for x in elem.findall('instance_info')]

    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        t = ET.SubElement(elem,'type')
        t.text = self.value
        for x in self.instance_info:
            x.serialize(ET.SubElement(elem,'instance_info'))

    def toStr(self, indent = 0):
        return f"{super().toStr(indent)} : { self.value }"

 
class Additional():
    '''Holds a pair of Entity and Relationship'''
    def __init__(self, entity:Entity, relationShip:Relationship) -> None:
        self.entity = entity
        self.relationship = relationShip

class TargetRelationType(X3Base):
    def __init__(self,elem : ET.Element|None = None) -> None:
        super().__init__(elem)
        self.ifs = []
        self.relationship = Relationship(None)
        self.iterMediates = []
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.ifs = [If(x) for x in elem.findall('if')]
        rss = elem.findall('relationship')
        self.relationship = Relationship(rss.pop())
        ets =  elem.findall('entity')
        self.iterMediates = [Additional(Entity(e),Relationship(r)) for e,r in zip(ets,rss)]
  
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.relationship.serialize(ET.SubElement(elem,'relationship'))
        for x in self.ifs:
            x.serialize(ET.SubElement(elem,'if'))
        for x in self.iterMediates:
            x.entity.serialize(ET.SubElement(elem,'entity'))
            x.relationship.serialize(ET.SubElement(elem,'relationship'))
   
    def toStr(self, indent = 0):
        return f"{super().toStr(indent)} : {self.relationship.value}"
  
class RangeTargetNodeType(X3Base):
    def __init__(self,elem : ET.Element|None = None) -> None:
        super().__init__(elem)
        self.entity = Entity()
        self.ifs = []
        if NN(elem):  self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.entity = Entity(elem.find('entity'))
        self.ifs = [If(x) for x in elem.findall('if')]
 
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        self.entity.serialize(ET.SubElement(elem,'entity'))
        for x in self.ifs:
            x.serialize(ET.SubElement(elem,'if'))

    def toStr(self, indent = 0):
        l = [ super().toStr(indent),self.entity.toStr(indent+1)]
        if w:= njoin([x.toStr(indent+1) for x in self.ifs]):
            l.append(w)
        return njoin(l)

class TargetNode(RangeTargetNodeType):
    pass

class DomainTargetNodeType(RangeTargetNodeType):
    pass

class SourceNode(X3Base):
    def __init__(self,elem : ET.Element|None = None):
        super().__init__(elem)
        self.text = ''
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element):
        super().deserialize(elem)
        self.text = getText(elem)
     
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        elem.text = self.text

    def toStr(self, indent = 0):
        return f"{super().toStr(indent)} : {self.text}"


class LogicalOp (X3Base):
    def __init__(self, elem : ET.Element|None=None, tag:str='') -> None:
        super().__init__()
        self.tag = tag
        self.xpath = ''
        self._ifs = []
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element|None):
        super().deserialize(elem)
        self._ifs =  [If(x) for x in elem.findall('if')]
        self.xpath = getText(elem)

    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        elem.text = self.xpath
        for x in self._ifs:
            x.serialize(ET.SubElement(elem,'if'))

class Not(LogicalOp): pass

class And (LogicalOp): pass

class Or(LogicalOp): pass

class ExactMatch(LogicalOp): pass

class Broader(LogicalOp): pass

class Narrower(LogicalOp): pass

class Equals(LogicalOp): pass

class Exists(LogicalOp): pass

class ConditionsType(X3Base):
    def __init__(self,elem: ET.Element|None=None) -> None:
        super().__init__(elem)
        self.text = ''
        self.op = Or()
        if NN(elem): self.deserialize(elem)

    def deserialize(self, elem:ET.Element|None):
        super().deserialize(elem)
        def choice(tag,cls):
            st = elem.find(tag)
            if not st is None:
                self.op = cls(st,tag)

        self.text = getText(elem)
        self.op = None
        choice('or',Or)
        choice('and',And)
        choice('not',Not)
        choice('narrower',Narrower)
        choice('broader',Broader)
        choice('exist',Exists)
        choice('equals',Equals)
        choice('exact_match',ExactMatch)
    
    def serialize(self, elem:ET.Element):
        super().serialize(elem)
        elem.text = self.text
        if self.op:
            self.op.serialize(ET.SubElement(elem,self.op.tag))


class If(ConditionsType): pass

def loadX3ml(filePath='test.x3ml'):
    model = X3ml()
    tree = ET.parse(filePath)
    model.deserialize(tree.getroot())
    return model

def storeX3ml(model:X3ml, filePath='download.x3ml'):
    root = model.serialize(ET.Element('x3ml') )
    ET.indent(root)
    tree = ET.ElementTree(root)
    tree.write(filePath)
    
if __name__ == "__main__":
    loadX3ml()
   



