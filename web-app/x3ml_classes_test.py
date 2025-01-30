import unittest
import x3ml_classes as XC
import xml.etree.ElementTree as ET

def makeX3Base():
    x3 = XC.X3Base()
    x3.setAttr('A', 44)
    x3.setAttr('B', 'ZZ')
    return x3

def makeElem(name='test'):
    elem = ET.Element(name)
    elem.attrib = {'A': 'a', 'B': 2}
    return elem

def makeElementsPath(root:ET.Element,names:list)->ET.Element|None:
    '''Creates a nechain of Element '''
    if len(names)==0:
        return root
    else: 
        subElem = ET.SubElement(root,names.pop(0))
        return makeElementsPath(subElem,names)

class Test_X3ml_Classes(unittest.TestCase):

    def setUp(self):
        pass

    def test_t0000(self):
        '''Serializer: Ctor, JSON'''
        testee = XC.Serializer()
        testee.y = 5
        self.assertEqual(testee.toJSON(), '{\n  "y": 5\n}')

    def test_t0003(self):
        '''X3Base: Ctor, Attributes'''
        testee = makeX3Base()
        self.assertEqual(testee.getAttr('A'), 44)
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_t0004(self):
        '''X3Base: Ctor, Serial, Attributes'''
        testee = XC.X3Base(makeElem())
        self.assertEqual(testee.getAttr('A'), 'a')
        self.assertEqual(testee.getAttr('B'), 2)

    def test_t0005(self):
        '''X3Base: Ctor, De/Serial, Attributes'''
        elem = makeX3Base().serialize(ET.Element('test'))
        testee = XC.X3Base()
        testee.deserialize(elem)
        self.assertEqual(testee.getAttr('A'), 44)
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_t0006(self):
        '''X3Base 2: Ctor, De/Serial, Attributes'''
        elem = makeX3Base().serialize(ET.Element('test'))
        testee = XC.X3Base(elem)
        self.assertEqual(testee.getAttr('A'), 44)
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_t0007(self):
        '''SimpleText: Access,Serial'''
        testee = XC.SimpleText()
        self.assertEqual(testee.text, '')
        self.assertEqual(testee.alias, '')

        elem = ET.Element('test')
        elem.text = '\\lido:lido'
        testee.deserialize(elem)
        self.assertEqual(testee.text, '\\lido:lido')
        self.assertEqual(testee.alias, '\\lido')

    def test_t0008(self):
        '''SimpleText: Access, Serial, Str'''
        elem = ET.Element('test')
        elem.text = 'lido:event'

        testee = XC.SimpleText()
        testee.deserialize(elem)
        self.assertEqual(testee.text, 'lido:event')
        self.assertEqual(testee.alias, 'event')
        self.assertEqual(str(testee), 'SimpleText\tlido:event')

    def test_t0009(self):
        '''Source: Ctor, Access, Serial'''
        elem = ET.Element('test')
        makeElementsPath(elem,['source_info','source_schema']).text ='schema'

        testee = XC.Source()
        testee.deserialize(elem)
        self.assertIsNotNone(testee.source_schema)
        self.assertEqual(type(testee.source_schema).__name__, 'SimpleText')
        self.assertEqual(testee.source_schema.text, 'schema')

    def test_t0010(self):
        '''Source 2: Ctor, Access, Serial'''
        testee = XC.Source()
        testee.set('schema')
        elem = testee.serialize(ET.Element('test'))
        subElem = elem.findall('source_info/source_schema')
        self.assertEqual(len(subElem), 1)
        self.assertEqual(subElem[0].text, 'schema')


    def test_t0011(self):
        '''Target: Ctor, Access, Serial'''
        elem = ET.Element('test')
        makeElementsPath(elem,['target_info','target_schema']).text ='schema'
        
        testee = XC.Target()
        testee.deserialize(elem)
        self.assertIsNotNone(testee.target_schema)
        self.assertEqual(type(testee.target_schema).__name__, 'SimpleText')
        self.assertEqual(testee.target_schema.text, 'schema')

    def test_t0012(self):
        '''Target 2: Ctor, Access, Serial'''
        testee = XC.Target()
        testee.set('schema')
        elem = testee.serialize(ET.Element('test'))
        subElems = elem.findall('target_info/target_schema')
        self.assertEqual(len(subElems), 1)
        self.assertEqual(subElems[0].text, 'schema')

    def test_t0015(self):
        '''MappingInfo 2: Ctor,  Serial'''
        testee = XC.MappingInfo()
        elem = testee.serialize(ET.Element('test'))
        self.assertIsNotNone(elem.find('mapping_created_by_org'))
        self.assertIsNotNone(elem.find('mapping_created_by_org'))
        self.assertIsNotNone(elem.find('in_collaboration_with'))

    def test_t0016(self):
        '''Comment 2: Ctor,  Serial'''
        testee = XC.Comment()
        elem = testee.serialize(ET.Element('test'))
        self.assertIsNotNone(elem.find('rationale'))
        self.assertIsNotNone(elem.find('alternatives'))
        self.assertIsNotNone(elem.find('typical_mistakes'))
        self.assertIsNotNone(elem.find('local_habits'))
        self.assertIsNotNone(elem.find('link_to_cook_book'))
        self.assertIsNotNone(elem.find('example/example_source'))
        self.assertIsNotNone(elem.find('example/example_target'))

    def test_t0017(self):
        '''ExampleDataInfo: Ctor,  Serial'''
        testee = XC.ExampleDataInfo()
        elem = testee.serialize(ET.Element('test'))
        self.assertIsNotNone(elem.find('example_data_from'))
        self.assertIsNotNone(elem.find('example_data_contact_person'))
        self.assertIsNotNone(elem.find('example_data_source_record'))
        self.assertIsNotNone(elem.find('generator_policy_info'))
        self.assertIsNotNone(elem.find('example_data_target_record'))
        self.assertIsNotNone(elem.find('thesaurus_info'))

    def test_t0018(self):
        '''Info: Ctor'''
        testee = XC.Info()
        self.assertTrue(isinstance(testee.title,XC.SimpleText))
        self.assertTrue(isinstance(testee.general_description,XC.SimpleText))
        self.assertTrue(isinstance(testee.source,XC.Source))
        self.assertTrue(isinstance(testee.target,XC.Target))
        self.assertTrue(isinstance(testee.mapping_info,XC.MappingInfo))
        self.assertTrue(isinstance(testee.example_data_info,XC.ExampleDataInfo))

    def test_t0019(self):
        '''Info: Deserialize'''
        elem = ET.Element('test')
        makeElementsPath(elem,['title']).text = 'title'
        makeElementsPath(elem,['source','source_info','source_schema']).text ='sinfo'
        makeElementsPath(elem,['target','target_info','target_schema']).text ='tinfo'

        testee = XC.Info()
        testee.deserialize(elem)
        self.assertEqual(testee.title.text,'title')
        self.assertEqual(testee.sSchema,'sinfo')
        self.assertEqual(testee.tSchema,'tinfo')

    def test_t0020(self):
        '''Info: Serialize'''
        info = XC.Info()
        info.title.text= 'title'
        
        elem = info.serialize(ET.Element('test'))
        titleElem = elem.find('title')
        self.assertIsNotNone(titleElem)
        self.assertEqual(titleElem.text,'title')
        
    def test_t0021(self):
        '''Namespace: Ctor, Access'''
        testee = XC.Namespace()
        testee.set('crm','http://cidoc.com')
        self.assertEqual(testee.prefix,'crm')
        self.assertEqual(testee.uri,'http://cidoc.com')

    def test_t0022(self):
        '''Namespace: Serial'''
        namespace = XC.Namespace()
        namespace.set('crm','http://cidoc.com')

        testee = ET.Element('test')
        testee = namespace.serialize(testee)
        self.assertEqual(testee.attrib['prefix'],'crm')
        self.assertEqual(testee.attrib['uri'],'http://cidoc.com')

    def test_t0023(self):
        '''Namespace: Serial'''
        elem = ET.Element('test', attrib = {'prefix':'crm','uri':'http://cidoc.com'})
        
        testee = XC.Namespace()
        testee.deserialize(elem)

        self.assertEqual(testee.prefix,'crm')
        self.assertEqual(testee.uri,'http://cidoc.com')

    def test_t0024(self):
        '''Namespace: Eq'''
        ns1 = XC.Namespace()
        ns2 = XC.Namespace()
        
        ns1.set('A','B')
        ns2.set('A','C')
        self.assertTrue(ns1==ns2)

        ns1.set('A','C')
        ns2.set('C','C')
        self.assertFalse(ns1==ns2)

    def test_t0025(self):
        '''Domain: Ctor, Access'''
        testee = XC.Domain()
        self.assertEqual(testee.path,'')
        self.assertEqual(testee.entity,'')

        testee.set('ABC','XYZ')
        
        self.assertEqual(testee.path,'ABC')
        self.assertEqual(testee.entity,'XYZ')

    def test_t0026(self):
        '''Domain: Ctro, DeSerial'''
        elem = ET.Element('test')
        makeElementsPath(elem,['source_node']).text = 'ABC'
        makeElementsPath(elem,['target_node','entity','type']).text = 'XYZ'

        testee = XC.Domain(elem)
        
        self.assertEqual(testee.path,'ABC')
        self.assertEqual(testee.entity,'XYZ')

    def test_t0027(self):
        '''Domain: Serial'''
        testee = XC.Domain()
        testee.set('ABC','XYZ')
        elem = ET.Element('test')

        testee.serialize(elem)

        self.assertEqual(elem.find('source_node').text,'ABC')
        self.assertEqual(elem.find('target_node/entity/type').text,'XYZ')

    def test_t0028(self):
        '''NR: Ctor'''
        node = XC.SimpleText(text='ABC')
        relation = XC.SimpleText(text='XYZ')
        
        testee = XC.NR(node,relation)

        self.assertEqual(testee.node.text,'ABC')
        self.assertEqual(testee.relation.text,'XYZ')

    def test_t0029(self):
        '''NR: Serial'''
        elem = ET.Element('test')
        testee = XC.NR.create('ABC','XYZ')

        testee.serialize(elem)

        self.assertEqual(elem.find('node').text,'ABC')
        self.assertEqual(elem.find('relation').text,'XYZ')

    def test_t0030(self):
        '''NR: Deserial'''
        elem = ET.Element('test')
        makeElementsPath(elem,['node']).text = 'ABC'
        makeElementsPath(elem,['relation']).text = 'XYZ'
        testee = XC.NR.create()
        
        testee.deserialize(elem)

        self.assertEqual(testee.node.text,'ABC')
        self.assertEqual(testee.relation.text,'XYZ')

    def test_t0031(self):
        '''SourceRelation: Ctor'''
        testee = XC.SourceRelation.create('ABC')
        self.assertEqual(testee.relation.text,'ABC')

    def test_t0032(self):
        '''SourceRelation: Serial'''
        testee = XC.SourceRelation.create('ABC')
        testee.nodes.append(XC.NR.create('N0','R0'))
        testee.nodes.append(XC.NR.create('N1','R1'))
        elem = ET.Element('test')

        testee.serialize(elem)

        rElems = elem.findall('relation')
        nElems = elem.findall('node')
        self.assertEqual(len(nElems),2)
        self.assertEqual(len(rElems),3)
        self.assertEqual(rElems[0].text,'ABC')
        self.assertEqual(nElems[0].text,'N0')
        self.assertEqual(rElems[1].text,'R0')
        self.assertEqual(nElems[1].text,'N1')
        self.assertEqual(rElems[2].text,'R1')

    def test_t0033(self):
        '''SourceRelation: DeSerial'''
        elem = ET.Element('test')
        makeElementsPath(elem,['relation']).text = 'ABC'
        makeElementsPath(elem,['relation']).text = 'R0'
        makeElementsPath(elem,['relation']).text = 'R1'
        makeElementsPath(elem,['node']).text = 'N0'
        makeElementsPath(elem,['node']).text = 'N1'
        testee = XC.SourceRelation()
        
        testee.deserialize(elem)

        self.assertEqual(testee.relation.text,'ABC')
        self.assertEqual(len(testee.nodes),2)
        self.assertEqual(testee.nodes[0].node.text,'N0')
        self.assertEqual(testee.nodes[0].relation.text,'R0')
        self.assertEqual(testee.nodes[1].node.text,'N1')
        self.assertEqual(testee.nodes[1].relation.text,'R1')
 
if __name__ == '__main__':
    unittest.main()
