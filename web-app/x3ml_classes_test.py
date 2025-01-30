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

def makeElementsPath(root:ET.Element,elems:list)->ET.Element|None:
    if len(elems)==0:
        return root
    else: 
        s = ET.SubElement(root,elems.pop(0))
        return makeElementsPath(s,elems)

class Test_X3ml_Classes(unittest.TestCase):

    def setUp(self):
        pass

    def test_t0000(self):
        '''Serializer: Ctor, JSON'''
        testee = XC.Serializer()
        testee.y = 5
        self.assertEqual(testee.toJSON(), '{\n  "y": 5\n}')

    def test_t0001(self):
        '''Attribute: Ctor, Access, JSON'''
        testee = XC.Attribute('k')
        self.assertEqual(testee.key, 'k')
        self.assertEqual(testee.value, '')
        self.assertEqual(str(testee), 'k:')
        self.assertEqual(testee.toJSON(), '{\n  "key": "k",\n  "value": ""\n}')

    def test_t0002(self):
        '''Attribute 2: Ctor, Access, JSON'''
        testee = XC.Attribute('myKey', 'myValue')
        self.assertEqual(testee.key, 'myKey')
        self.assertEqual(testee.value, 'myValue')
        self.assertEqual(str(testee), 'myKey:myValue')
        self.assertEqual(
            testee.toJSON(), '{\n  "key": "myKey",\n  "value": "myValue"\n}')

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
        self.assertEqual(testee.prefix(),'crm')
        self.assertEqual(testee.uri(),'http://cidoc.com')

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

        self.assertEqual(testee.prefix(),'crm')
        self.assertEqual(testee.uri(),'http://cidoc.com')

if __name__ == '__main__':
    unittest.main()
