import unittest
import libs.x3ml_classes as XC
from xml.etree.ElementTree import Element, XML, SubElement

def SubElementList(root: Element, names: list) -> Element | None:
    '''Creates a chain of Elements '''
    if len(names) == 0:
        return root
    else:
        subElem = SubElement(root, names.pop(0))
        return SubElementList(subElem, names)

def SubElementPath(root: Element, path: str) -> Element | None:
    '''Creates a chain of Elements '''
    names = path.split('/')
    return SubElementList(root, names)

def ElementPath(path,endText=''):
    '''Returns an element chain and set the end element text'''
    names = path.split('/') 
    elem = Element(names.pop(0))
    SubElementList(elem,names).text=endText
    return elem

class Test_X3ml_Classes(unittest.TestCase):
    """Test suite for the X3ML classes in the x3ml_classes module."""

    def setUp(self):
        pass

    def test_X3Base_1(self):
        '''X3Base: Ctor, De/Serial, Attributes'''
        testee = XC.X3Base()
        testee.deserialize(XML('<test A="44" B="ZZ"/>'))
        self.assertEqual(testee.attributes['A'], '44')
        self.assertEqual(testee.attributes['B'], 'ZZ')
 
    def test_X3Base_2(self):
        '''X3Base: Ctor, Attributes'''
        testee = XC.X3Base()
        testee.deserialize(XML('<test A="44" B="ZZ"/>'))
        self.assertEqual(testee.attributes['A'], '44')
        self.assertEqual(testee.attributes['B'], 'ZZ')

    def test_SimpleText_1(self):
        '''SimpleText: Access,Serial'''
        testee = XC.SimpleText()
        self.assertEqual(testee.text, '')

        elem = ElementPath('test', '\\lido:lido')

        testee.deserialize(elem)

        self.assertEqual(testee.text, '\\lido:lido')

    def test_SimpleText_2(self):
        '''SimpleText: Access, Serial, Str'''
        elem = ElementPath('test','lido:event')
        testee = XC.SimpleText()
        testee.deserialize(elem)
        self.assertEqual(testee.text, 'lido:event')

    def test_Source_1(self):
        '''Source: Ctor, Access, Serial'''
        elem = ElementPath('test/source_info/source_schema','schema')
        testee = XC.Source()

        testee.deserialize(elem)

        self.assertIsNotNone(testee.source_schema)
        self.assertEqual(type(testee.source_schema).__name__, 'SimpleText')
        self.assertEqual(testee.source_schema.text, 'schema')

    def test_Source_2(self):
        '''Source: Ctor, Access, Serial'''
        testee = XC.Source()
        testee.set('schema')
        
        elem = testee.serialize(Element('test'))

        subElem = elem.findall('source_info/source_schema')
        self.assertEqual(len(subElem), 1)
        self.assertEqual(subElem[0].text, 'schema')

    def test_Target_1(self):
        '''Target: Ctor, Access, Serial'''
        elem = ElementPath('test/target_info/target_schema','schema')
        testee = XC.Target()

        testee.deserialize(elem)

        self.assertIsNotNone(testee.target_schema)
        self.assertEqual(type(testee.target_schema).__name__, 'SimpleText')
        self.assertEqual(testee.target_schema.text, 'schema')

    def test_Target_2(self):
        '''Target: Ctor, Access, Serial'''
        testee = XC.Target()
        testee.set('schema')
       
        elem = testee.serialize(Element('test'))
       
        subElems = elem.findall('target_info/target_schema')
        self.assertEqual(len(subElems), 1)
        self.assertEqual(subElems[0].text, 'schema')

    def test_MappingInfo_1(self):
        '''MappingInfo 2: Ctor,  Serial'''
        testee = XC.MappingInfo()
        
        elem = testee.serialize(Element('test'))
        
        self.assertIsNotNone(elem.find('mapping_created_by_org'))
        self.assertIsNotNone(elem.find('in_collaboration_with'))

        testee = XC.Comment()
    def test_Comment_1(self):
        '''Comment: Ctor,  Serial'''
        testee = XC.Comment()
        
        elem = testee.serialize(Element('test'))
        
        self.assertIsNotNone(elem.find('rationale'))
        self.assertIsNotNone(elem.find('alternatives'))
        self.assertIsNotNone(elem.find('typical_mistakes'))
        self.assertIsNotNone(elem.find('local_habits'))
        self.assertIsNotNone(elem.find('link_to_cook_book'))
        self.assertIsNotNone(elem.find('example/example_source'))
        self.assertIsNotNone(elem.find('example/example_target'))

    def test_ExampleDataInfo(self):
        '''ExampleDataInfo: Ctor,  Serial'''
        testee = XC.ExampleDataInfo()
        
        elem = testee.serialize(Element('test'))
        
        self.assertIsNotNone(elem.find('example_data_from'))
        self.assertIsNotNone(elem.find('example_data_contact_person'))
        self.assertIsNotNone(elem.find('example_data_source_record'))
        self.assertIsNotNone(elem.find('generator_policy_info'))
        self.assertIsNotNone(elem.find('example_data_target_record'))
        self.assertIsNotNone(elem.find('thesaurus_info'))

    def test_Info_1(self):
        '''Info: Ctor'''
        testee = XC.Info()
        self.assertTrue(isinstance(testee.title, XC.SimpleText))
        self.assertTrue(isinstance(testee.general_description, XC.SimpleText))
        self.assertTrue(isinstance(testee.source, XC.Source))
        self.assertTrue(isinstance(testee.target, XC.Target))
        self.assertTrue(isinstance(testee.mapping_info, XC.MappingInfo))
        self.assertTrue(isinstance(testee.example_data_info, XC.ExampleDataInfo))

    def test_Info2(self):
        '''Info: Deserialize'''
        elem = ElementPath('test/title','title')
        SubElementPath(elem, 'source/source_info/source_schema').text = 'sinfo'
        SubElementPath(elem, 'target/target_info/target_schema').text = 'tinfo'

        testee = XC.Info()
        testee.deserialize(elem)
        self.assertEqual(testee.title.text, 'title')
        self.assertEqual(testee.sSchema, 'sinfo')
        self.assertEqual(testee.tSchema, 'tinfo')

    def test_Info_3(self):
        '''Info: Serialize'''
        info = XC.Info()
        info.title.text = 'title'

        elem = info.serialize(Element('test'))

        titleElem = elem.find('title')
        self.assertIsNotNone(titleElem)
        self.assertEqual(titleElem.text, 'title')

    def test_Namespace_1(self):
        '''Namespace: Ctor, Access'''
        testee = XC.Namespace()
        testee.set('crm', 'http://cidoc.com')

        self.assertEqual(testee.prefix, 'crm')
        self.assertEqual(testee.uri, 'http://cidoc.com')

    def test_Namespace_2(self):
        '''Namespace: Serial'''
        namespace = XC.Namespace()
        namespace.set('crm', 'http://cidoc.com')
        testee = Element('test')

        testee = namespace.serialize(testee)

        self.assertEqual(testee.attrib['prefix'], 'crm')
        self.assertEqual(testee.attrib['uri'], 'http://cidoc.com')

    def test_Namespace_3(self):
        '''Namespace: Serial'''
        elem = Element('test', attrib={'prefix': 'crm', 'uri': 'http://cidoc.com'})

        testee = XC.Namespace()
        testee.deserialize(elem)

        self.assertEqual(testee.prefix, 'crm')
        self.assertEqual(testee.uri, 'http://cidoc.com')

    def test_Namespace_4(self):
        '''Namespace: Eq'''
        ns1 = XC.Namespace()
        ns2 = XC.Namespace()

        ns1.set('A', 'B')
        ns2.set('A', 'C')
        self.assertTrue(ns1 == ns2)

        ns1.set('A', 'C')
        ns2.set('C', 'C')
        self.assertFalse(ns1 == ns2)

    def test_Domain_1(self):
        '''Domain: Ctor, Access'''
        testee = XC.Domain()
        self.assertEqual(testee.path, '')
        self.assertEqual(testee.entity, '')

        testee.set('ABC', 'XYZ')

        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'XYZ')

    def test_Domain_2(self):
        '''Domain: Ctor, DeSerial'''
        elem = ElementPath('test/source_node','ABC')
        SubElementPath(elem, 'target_node/entity/type').text = 'XYZ'

        testee = XC.Domain.from_serial(elem)

        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'XYZ')

    def test_Domain_3(self):
        '''Domain: Serial'''
        testee = XC.Domain()
        testee.set('ABC', 'XYZ')
        elem = Element('test')

        testee.serialize(elem)

        self.assertEqual(elem.find('source_node').text, 'ABC')
        self.assertEqual(elem.find('target_node/entity/type').text, 'XYZ')

    def test_NR_1(self):
        '''NR: Ctor'''
        node = XC.SimpleText(text='ABC')
        relation = XC.SimpleText(text='XYZ')

        testee = XC.NR(relation=relation, node=node)

        self.assertEqual(testee.node.text, 'ABC')
        self.assertEqual(testee.relation.text, 'XYZ')

    def test_NR_2(self):
        '''NR: Serial'''
        elem = Element('test')
        testee = XC.NR.create('ABC', 'XYZ')

        testee.serialize(elem)

        self.assertEqual(elem.find('node').text, 'ABC')
        self.assertEqual(elem.find('relation').text, 'XYZ')

    def test_NR_3(self):
        '''NR: Deserial'''
        elem = Element('test')
        SubElement(elem, 'node').text = 'ABC'
        SubElement(elem, 'relation').text = 'XYZ'
        testee = XC.NR.create()

        testee.deserialize(elem)

        self.assertEqual(testee.node.text, 'ABC')
        self.assertEqual(testee.relation.text, 'XYZ')

    def test_SourceRelation_1(self):
        '''SourceRelation 1: Ctor'''
        testee = XC.SourceRelation(relation=XC.SimpleText(text='ABC'))
        self.assertEqual(testee.relation.text, 'ABC')

    def test_SourceRelation_2(self):
        '''SourceRelation 2: Serial'''
        testee = XC.SourceRelation(relation=XC.SimpleText(text='ABC'))
        testee.nodes.append(XC.NR.create('N0', 'R0'))
        testee.nodes.append(XC.NR.create('N1', 'R1'))
        elem = Element('test')

        testee.serialize(elem)

        rElems = elem.findall('relation')
        nElems = elem.findall('node')
        self.assertEqual(len(nElems), 2)
        self.assertEqual(len(rElems), 3)
        self.assertEqual(rElems[0].text, 'ABC')
        self.assertEqual(nElems[0].text, 'N0')
        self.assertEqual(rElems[1].text, 'R0')
        self.assertEqual(nElems[1].text, 'N1')
        self.assertEqual(rElems[2].text, 'R1')

    
    def test_Path_3(self):
        '''Path: DeSerial'''
        elem = Element('test')
        SubElementPath(elem, 'source_relation/relation').text = 'ABC'
        SubElementPath(elem, 'target_relation/relationship').text = 'xyz'
        comsElem = SubElement(elem, 'comments')
        SubElementPath(comsElem, 'comment/rationale').text = 'comment 1'
        SubElementPath(comsElem, 'comment/rationale').text = 'comment 2'
        testee = XC.Path()

        testee.deserialize(elem)
        self.assertEqual(testee.sourceRelation.path, 'ABC')
        self.assertEqual(testee.targetRelation.entity, 'xyz')
        self.assertEqual(len(testee.comments), 2)
        self.assertEqual(testee.comments[0].rationale.text, 'comment 1')
        self.assertEqual(testee.comments[1].rationale.text, 'comment 2')

    def test_Range_1(self):
        '''Range: Ctor, Access'''
        testee = XC.Range()
        testee.set('ABC', 'xyz')
        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'xyz')

    def test_Range_2(self):
        '''Range: Serial'''
        testee = XC.Range()
        testee.set('ABC', 'xyz')
        elem = Element('test')

        testee.serialize(elem)

        self.assertEqual(elem.find('source_node').text, 'ABC')
        self.assertEqual(elem.find('target_node/entity/type').text, 'xyz')

    def test_Range_3(self):
        '''Range: DeSerial'''
        elem = Element('test')
        SubElement(elem, 'source_node').text = 'ABC'
        SubElementPath(elem, 'target_node/entity/type').text = 'xyz'
        testee = XC.Range()

        testee.deserialize(elem)
        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'xyz')
    
    
    def test_Entity_1(self):
        '''Entity: Ctor, Access'''
        testee = XC.Entity()
        self.assertEqual(testee.type, '')
        self.assertEqual(len(testee.instance_info), 0)

    def test_Entity_2(self):
        '''Entity: Deserialize'''
        elem = Element('test')
        SubElement(elem, 'type').text = 'entityType'
        instance_info_elem = SubElementPath(elem, 'instance_info')
        SubElementPath(instance_info_elem, 'constant')

        testee = XC.Entity()
        testee.deserialize(elem)

        self.assertEqual(testee.type, 'entityType')
        self.assertEqual(len(testee.instance_info), 1)
        self.assertEqual(testee.instance_info[0].mode, 'constant')

    def test_Entity_3(self):
        '''Entity: Serialize'''
        testee = XC.Entity()
        testee.type = 'entityType'
        instance_info = XC.InstanceInfo()
        instance_info.mode = 'constant'
        testee.instance_info.append(instance_info)

        elem = Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('type').text, 'entityType')
        self.assertEqual(len(elem.findall('instance_info')), 1)
        self.assertIsNotNone(elem.find('instance_info/constant'))

    def test_TargetExtension_1(self):
        '''TargetExtension: Ctor, Access'''
        entity = XC.Entity()
        relationship = XC.Relationship()
        testee = XC.TargetExtension(entity, relationship)
        self.assertIsInstance(testee.entity, XC.Entity)
        self.assertIsInstance(testee.relationship, XC.Relationship)

    def test_TargetExtension_2(self):
        '''TargetExtension: Serialize'''
        entity = XC.Entity()
        entity.type = 'entityType'
        relationship = XC.Relationship()
        relationship.text = 'relationshipType'
        testee = XC.TargetExtension(entity, relationship)

        elem = Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('entity/type').text, 'entityType')
        self.assertEqual(elem.find('relationship').text, 'relationshipType')

    def test_TargetExtension_3(self):
        '''TargetExtension: Deserialize'''
        elem = Element('test')
        SubElementPath(elem, 'entity/type').text = 'entityType'
        SubElement(elem, 'relationship').text = 'relationshipType'
                
        testee = XC.TargetExtension(XC.Entity(), XC.Relationship())
        testee.deserialize(elem)
                
        self.assertEqual(testee.entity.type, 'entityType')
        self.assertEqual(testee.relationship.text, 'relationshipType')

    def test_TargetRelation_1(self):
        '''TargetRelation: Ctor, Access'''
        testee = XC.TargetRelation()
        self.assertEqual(testee.relationship.text, '')
        self.assertEqual(len(testee.extensions), 0)

    def test_TargetRelation_2(self):
        '''TargetRelation: Deserialize'''
        elem = Element('test')
        SubElement(elem, 'relationship').text = 'relationshipType'
        SubElementPath(elem, 'if/op')
        SubElementPath(elem, 'entity/type').text = 'entityType'
        SubElement(elem, 'relationship').text = 'intermediateRelationship'

        testee = XC.TargetRelation()
        testee.deserialize(elem)

        self.assertEqual(len(testee.extensions), 1)
        self.assertEqual(testee.extensions[0].entity.type, 'entityType')


    def test_TargetNode_1(self):
        '''TargetNode: Ctor, Access'''
        testee = XC.TargetNode()
        self.assertIsInstance(testee.entity, XC.Entity)
 

    def test_TargetNode_2(self):
        '''TargetNode: Deserialize'''
        elem = ElementPath('test/entity/type','entityType')
        SubElement(elem, 'if')
        testee = XC.TargetNode().deserialize(elem)
        self.assertEqual(testee.entity.type, 'entityType')
 
  
    def test_Mapping_1(self):
        '''Mapping: Ctor, Access'''
        testee = XC.Mapping()
        self.assertIsInstance(testee.domain, XC.Domain)
        self.assertEqual(len(testee.links), 0)

 
    def test_X3ml_1(self):
        '''X3ml: Ctor, Access'''
        testee = XC.X3ml()
        self.assertIsInstance(testee.info, XC.Info)
        self.assertEqual(len(testee.namespaces), 0)
        self.assertEqual(len(testee.mappings), 0)

    def test_X3ml_2(self):
        '''X3ml: Deserialize'''
        elem = Element('test')
        SubElementPath(elem, 'info/title').text = 'infoTitle'
        SubElementPath(elem, 'namespaces/namespace').attrib = {'prefix': 'nsPrefix', 'uri': 'nsUri'}
        domainElem = SubElementPath(elem, 'mappings/mapping/domain')
        SubElement(domainElem, 'source_node').text = 'domainPath'
        SubElementPath(domainElem, 'target_node/entity/type').text = 'domainEntity'

        testee = XC.X3ml()
        testee.deserialize(elem)

        self.assertEqual(testee.info.title.text, 'infoTitle')
        self.assertEqual(len(testee.namespaces), 1)
        self.assertEqual(testee.namespaces[0].prefix, 'nsPrefix')
        self.assertEqual(testee.namespaces[0].uri, 'nsUri')
        self.assertEqual(len(testee.mappings), 1)
        self.assertEqual(testee.mappings[0].domain.path, 'domainPath')
        self.assertEqual(testee.mappings[0].domain.entity, 'domainEntity')

    def test_X3ml_3(self):
        '''X3ml: Serialize'''
        testee = XC.X3ml()
        testee.info.title.text = 'infoTitle'
        ns = XC.Namespace()
        ns.set('nsPrefix', 'nsUri')
        testee.namespaces.append(ns)
        mapping = XC.Mapping()
        mapping.domain.set('domainPath', 'domainEntity')
        testee.mappings.append(mapping)

        elem = Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('info/title').text, 'infoTitle')
        self.assertEqual(elem.find('namespaces/namespace').attrib['prefix'], 'nsPrefix')
        self.assertEqual(elem.find('namespaces/namespace').attrib['uri'], 'nsUri')
        self.assertEqual(elem.find('mappings/mapping/domain/source_node').text, 'domainPath')
        self.assertEqual(elem.find('mappings/mapping/domain/target_node/entity/type').text, 'domainEntity')

        def test_Predicate_1(self):
            '''Predicate: Ctor, Access'''
            testee = XC.Predicate()
            self.assertEqual(testee.xpath, '')
            self.assertEqual(testee.value, '')
            self.assertEqual(testee.tag, '')

        def test_Predicate_2(self):
            '''Predicate: Deserialize'''
            elem = Element('test', attrib={'value': 'testValue'})
            elem.text = 'testXpath'
            testee = XC.Predicate()
            
            testee.deserialize(elem)
            
            self.assertEqual(testee.xpath, 'testXpath')
            self.assertEqual(testee.value, 'testValue')

        def test_Predicate_3(self):
            '''Predicate: Serialize'''
            testee = XC.Predicate()
            testee.xpath = 'testXpath'
            testee.value = 'testValue'
            elem = Element('test')
            
            testee.serialize(elem)
            
            self.assertEqual(elem.text, 'testXpath')
            self.assertEqual(elem.attrib['value'], 'testValue')

        def test_Equals_1(self):
            '''Equals: Ctor, Post Init'''
            testee = XC.Equals()
            self.assertEqual(testee.tag, 'equals')

        def test_Equals_2(self):
            '''Equals: Serialize'''
            testee = XC.Equals()
            testee.xpath = 'someXpath'
            testee.value = 'someValue'
            elem = Element('equals')
            
            testee.serialize(elem)
            
            self.assertEqual(elem.text, 'someXpath')
            self.assertEqual(elem.attrib['value'], 'someValue')
            self.assertEqual(testee.tag, 'equals')

if __name__ == '__main__':
    unittest.main()
