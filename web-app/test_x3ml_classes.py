import unittest
import x3ml_classes as XC
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

class MockOpTrue(XC.Or):
    '''Mock Operation True'''
    def validate(self, elem):
        return True

class MockOpFalse(XC.Or):
    '''Moc operation False'''
    def validate(self, elem):
        return False

def makeIfOr(trueFalse):
    tIf = XC.PredicateVariant()
    tIf.op = MockOpTrue() if trueFalse else MockOpFalse()
    return tIf


class Test_X3ml_Classes(unittest.TestCase):
    """Test suite for the X3ML classes in the x3ml_classes module."""

    def setUp(self):
        pass

    def test_Serializer(self):
        '''Serializer: Ctor, JSON'''
        testee = XC.Serializer()
        testee.y = 5
        self.assertEqual(testee.toJSON(), '{\n  "y": 5\n}')

    def test_X3Base_1(self):
        '''X3Base: Ctor, De/Serial, Attributes'''
        testee = XC.X3Base()
        testee.deserialize(XML('<test A="44" B="ZZ"/>'))
        self.assertEqual(testee.getAttr('A'), '44')
        self.assertEqual(testee.getAttr('B'), 'ZZ')
 
    def test_X3Base_2(self):
        '''X3Base: Ctor, Attributes'''
        testee = XC.X3Base(XML('<test A="44" B="ZZ"/>'))
        self.assertEqual(testee.getAttr('A'), '44')
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_SimpleText_1(self):
        '''SimpleText: Access,Serial'''
        testee = XC.SimpleText()
        self.assertEqual(testee.text, '')
        self.assertEqual(testee.alias(), '')

        elem = ElementPath('test', '\\lido:lido')

        testee.deserialize(elem)

        self.assertEqual(testee.text, '\\lido:lido')
        self.assertEqual(testee.alias(), '\\lido')

    def test_SimpleText_2(self):
        '''SimpleText: Access, Serial, Str'''
        elem = ElementPath('test','lido:event')
        testee = XC.SimpleText()

        testee.deserialize(elem)

        self.assertEqual(testee.text, 'lido:event')
        self.assertEqual(testee.alias(), 'event')
        self.assertEqual(str(testee), 'SimpleText\tlido:event')

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

        testee = XC.Domain(elem)

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

        testee = XC.NR(node, relation)

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
        testee = XC.SourceRelation.create('ABC')
        self.assertEqual(testee.relation.text, 'ABC')

    def test_SourceRelation_2(self):
        '''SourceRelation 2: Serial'''
        testee = XC.SourceRelation.create('ABC')
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

    def test_SourceRelation_3(self):
        '''SourceRelation 3: DeSerial'''
        elem = Element('test')
        SubElement(elem, 'relation').text = 'ABC'
        SubElement(elem, 'relation').text = 'R0'
        SubElement(elem, 'relation').text = 'R1'
        SubElement(elem, 'node').text = 'N0'
        SubElement(elem, 'node').text = 'N1'
        testee = XC.SourceRelation()

        testee.deserialize(elem)

        self.assertEqual(testee.relation.text, 'ABC')
        self.assertEqual(len(testee.nodes), 2)
        self.assertEqual(testee.nodes[0].node.text, 'N0')
        self.assertEqual(testee.nodes[0].relation.text, 'R0')
        self.assertEqual(testee.nodes[1].node.text, 'N1')
        self.assertEqual(testee.nodes[1].relation.text, 'R1')

    def test_Path_1(self):
        '''Path: Ctor'''
        testee = XC.Path()
        testee.set('ABC', 'xyz')
        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'xyz')

    def test_Path_2(self):
        '''Path: Serial'''
        testee = XC.Path()
        testee.set('ABC', 'xyz')
        testee.addComment('a comment')
        testee.addComment('a comment 2')
        elem = Element('test')

        testee.serialize(elem)

        self.assertEqual(elem.find('source_relation/relation').text, 'ABC')
        self.assertEqual(elem.find('target_relation/relationship').text, 'xyz')
        comments = elem.findall('comments/comment/rationale')
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].text, 'a comment')
        self.assertEqual(comments[1].text, 'a comment 2')

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

    def test_ComposedPredicate_1(self):
        '''ComposedPredicate: Ctor, Access'''
        testee = XC.ComposedPredicate(None, 'aTag')
        self.assertEqual(testee.tag, 'aTag')
        self.assertEqual(testee.xpath, '')

    def test_ComposedPredicate_2(self):
        '''ComposedPredicate: Serial'''
        testee = XC.ComposedPredicate()
        testee.predicates.append(XC.PredicateVariant())
        testee.predicates.append(XC.PredicateVariant())
        elem = Element('test')

        testee.serialize(elem)

        ifs = elem.findall('if/or')
        self.assertEqual(len(ifs), 2)
        # TODO

    def test_ComposedPredicate_3(self):
        '''ComposedPredicate: DeSerial'''
        elem = Element('test')
        SubElementPath(elem, 'if/or')
        SubElementPath(elem, 'if/and')
        testee = XC.ComposedPredicate()

        testee.deserialize(elem)

        self.assertEqual(len(testee.predicates), 2)
        self.assertIsInstance(testee.predicates[0], XC.PredicateVariant)
        self.assertIsInstance(testee.predicates[0].op, XC.Or)
        self.assertIsInstance(testee.predicates[1], XC.PredicateVariant)
        self.assertIsInstance(testee.predicates[1].op, XC.And)
        # TODO

    def test_OPS(self):
        '''Ops: Ctor'''
        self.assertEqual(XC.Or().tag, 'or')
        self.assertEqual(XC.And().tag, 'and')
        self.assertEqual(XC.Not().tag, 'not')
        self.assertEqual(XC.ExactMatch().tag, 'exact_match')
        self.assertEqual(XC.Broader().tag, 'broader')
        self.assertEqual(XC.Narrower().tag, 'narrower')
        self.assertEqual(XC.Equals().tag, 'equals')
        self.assertEqual(XC.Exists().tag, 'exists')

    def test_ConditionsType_1(self):
        '''ConditionsType: Ctor, Access'''
        testee = XC.PredicateVariant(None)
        self.assertIsInstance(testee.op, XC.Or)

    def test_ConditionsType_2(self):
        '''ConditionsType: Serial'''
        testee = XC.PredicateVariant(None)
        elem = Element('test')
        testee.serialize(elem)

        self.assertEqual(len(elem.findall('or')), 1)
        self.assertIsNotNone(elem.find('or').tag, 'or')

    def test_ConditionsType_3(self):
        '''ConditionsType: DeSerial'''
        elem = Element('test')
        SubElement(elem, 'or')
        testee = XC.PredicateVariant(None)

        testee.deserialize(elem)

        self.assertIsInstance(testee.op, XC.Or)
    
    def test_OR_1(self):
        elem = Element('test')
        testee = XC.Or()

        testee.predicates = [makeIfOr(False),makeIfOr(False)]
        self.assertFalse(testee.validate(elem))

        testee.predicates = [makeIfOr(False),makeIfOr(True)]
        self.assertTrue(testee.validate(elem))

        testee.predicates = [makeIfOr(True),makeIfOr(False)]
        self.assertTrue(testee.validate(elem))

        testee.predicates = [makeIfOr(True),makeIfOr(True)]
        self.assertTrue(testee.validate(elem))

    def test_OR_2(self):
        '''OR: serialize'''
        elem = Element('or')
        testee = XC.Or()
        if1 = testee.append(XC.PredicateVariant())
        if1.op = XC.Equals.byValues('xpath1','value1')
        if2 =testee.append(XC.PredicateVariant())
        if2.op = XC.Equals.byValues('xpath2','value2')
      
        testee.serialize(elem)
        subElems = elem.findall('if/equals')
        self.assertEqual(len(subElems),2)
        self.assertEqual(subElems[0].get('value'),'value1')
        self.assertEqual(subElems[0].text,'xpath1')
        self.assertEqual(subElems[1].get('value'),'value2')
        self.assertEqual(subElems[1].text,'xpath2')

    def test_OR_3(self):
        '''OR: deserialize'''
        data = '''<or>
                     <if><equals value="value1">xpath1</equals></if>
                     <if><equals value="value2">xpath2</equals></if>
                  </or>'''
        testee = XC.Or( XML(data))
        self.assertEqual(len(testee.predicates),2)
        for n in range(2):
            p = testee.predicates[n]
            self.assertIsInstance(p,XC.PredicateVariant)
            self.assertIsInstance(p.op,XC.Equals)
            self.assertEqual(len(p.op.predicates),0)
            self.assertEqual(p.op.value,f'value{n+1}')
            self.assertEqual(p.op.xpath,f'xpath{n+1}')
    
    def test_OR_4(self):
        '''OR: validate element'''
        rules = '''<or>
                     <if><equals value="valueÖ">a/b/c/text()</equals></if>
                     <if><equals value="value2">a/b/c/text()</equals></if>
                  </or>'''
        testee = XC.Or( XML(rules))

        self.assertIsInstance(testee,XC.Or)
        self.assertEqual(len(testee.predicates),2)
        
        elem =  XML('<x><a><b><c>valueÖ</c></b></a></x>')
        self.assertTrue(testee.validate(elem))
        elem =  XML('<x><a><b><c>value2</c></b></a></x>')
        self.assertTrue(testee.validate(elem))
        elem =  XML('<x><a><b><c>value3</c></b></a></x>')
        self.assertFalse(testee.validate(elem))

    def test_AND_1(self):
        '''And: validate dummy'''
        elem = Element('test')
        testee = XC.And()

        testee.predicates = [makeIfOr(False),makeIfOr(False)]
        self.assertFalse(testee.validate(elem))

        testee.predicates = [makeIfOr(False),makeIfOr(True)]
        self.assertFalse(testee.validate(elem))

        testee.predicates = [makeIfOr(True),makeIfOr(False)]
        self.assertFalse(testee.validate(elem))

        testee.predicates = [makeIfOr(True),makeIfOr(True)]
        self.assertTrue(testee.validate(elem))

    def test_AND_2(self):
        '''AND: validate element'''
        rules = '''<and>
                     <if><equals value="valueÖ">a/b/c/text()</equals></if>
                     <if><equals value="value2">a/b/d/text()</equals></if>
                  </and>'''
        testee = XC.And( XML(rules))

        self.assertIsInstance(testee,XC.And)
        self.assertEqual(len(testee.predicates),2)
        
        elem =  XML('<x><a><b> <c>valueÖ</c> <d>value2</d> </b></a></x>')
        self.assertTrue(testee.validate(elem))
        elem =  XML('<x><a><b> <d>value2</d> <c>valueÖ</c> </b></a></x>')
        self.assertTrue(testee.validate(elem))
        
        elem =  XML('<x><a><b> <c>value</c> <d>value2</d> </b></a></x>')
        self.assertFalse(testee.validate(elem))
        elem =  XML('<x><a><b> <c>valueÖ</c> <d>value</d> </b></a></x>')
        self.assertFalse(testee.validate(elem))
        elem =  XML('<x><a><b> <c>valueX</c> <d>valueY</d> </b></a></x>')
        self.assertFalse(testee.validate(elem))

    def test_AND_2(self):
        '''AND: validate element'''
        rules = '''<or>
                     <if><equals value="valueÖ">a/b/c/text()</equals></if>
                     <if><equals value="value2">a/b/d/text()</equals></if>
                  </or>'''
        testee = XC.And( XML(rules))

        self.assertIsInstance(testee,XC.And)
        self.assertEqual(len(testee.predicates),2)
        
        elem =  XML('<x><a><b> <c>valueÖ</c> <d>value2</d> </b></a></x>')
        self.assertTrue(testee.validate(elem))
        elem =  XML('<x><a><b> <c>value</c> <d>value2</d> </b></a></x>')
        self.assertFalse(testee.validate(elem))
        elem =  XML('<x><a><b> <c>valueÖ</c> <d>value</d> </b></a></x>')
        self.assertFalse(testee.validate(elem))
        elem =  XML('<x><a><b> <c>valueX</c> <d>valueY</d> </b></a></x>')
        self.assertFalse(testee.validate(elem))

    def test_IF_1(self):
        '''If: Ctor'''
        testee = XC.PredicateVariant()
        self.assertIsInstance(testee.op, XC.Or)

    def test_IF_2(self):
        '''If: logic'''
        testee = XC.PredicateVariant()
        self.assertFalse(testee.validate(None))
        elem = Element('test')
        testee.op = MockOpTrue()
        self.assertTrue(testee.validate(elem))
        testee.op = MockOpFalse()
        self.assertFalse(testee.validate(elem))


    def test_Link_1(self):
        '''Link: Ctor'''
        testee = XC.Link()
        self.assertIsInstance(testee.path, XC.Path)
        self.assertEqual(testee.path.path, '')
        self.assertEqual(testee.path.entity, '')
        self.assertEqual(testee.range.path, '')
        self.assertEqual(testee.range.entity, '')
        testee.set('aPath', 'aRS', 'anEntity')
        self.assertEqual(testee.path.path, 'aPath')
        self.assertEqual(testee.range.path, 'aPath')
        self.assertEqual(testee.path.entity, 'aRS')
        self.assertEqual(testee.range.entity, 'anEntity')

    def test_Link_2(self):
        '''Link: Serial'''
        testee = XC.Link()
        testee.set('aPath', 'aRS', 'anEntity')
        elem = Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('path/source_relation/relation').text, 'aPath')
        self.assertEqual(elem.find('path/target_relation/relationship').text, 'aRS')
        self.assertEqual(elem.find('range/source_node').text, 'aPath')
        self.assertEqual(elem.find('range/target_node/entity/type').text, 'anEntity')

    def test_Link_3(self):
        '''Link: DeSerial'''
        elem = Element('test')
        pathElem = SubElement(elem, 'path')
        SubElementPath(pathElem, 'source_relation/relation').text = 'aPath'
        SubElementPath(pathElem, 'target_relation/relationship').text = 'aRS'
        rangeElem = SubElement(elem, 'range')
        SubElement(rangeElem, 'source_node').text = 'aPath'
        SubElementPath(rangeElem, 'target_node/entity/type').text = 'anEntity'
        testee = XC.Link()

        testee.deserialize(elem)

        self.assertEqual(testee.path.path, 'aPath')
        self.assertEqual(testee.range.path, 'aPath')
        self.assertEqual(testee.path.entity, 'aRS')
        self.assertEqual(testee.range.entity, 'anEntity')

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

    def test_TargetRelation_3(self):
        '''TargetRelation: Serialize'''
        testee = XC.TargetRelation()
        testee.relationship.text = 'relationshipType'
        testee.condition = XC.PredicateVariant()
        extension = XC.TargetExtension(XC.Entity(), XC.Relationship())
        extension.entity.type = 'entityType'
        extension.relationship.text = 'intermediateRelationship'
        testee.extensions.append(extension)

        elem = testee.serialize(Element('test'))

        self.assertEqual(elem.find('relationship').text, 'relationshipType')
        self.assertIsNotNone(elem.find('if/or'))
        self.assertEqual(elem.find('entity/type').text, 'entityType')

    def test_TargetNode_1(self):
        '''TargetNode: Ctor, Access'''
        testee = XC.TargetNode()
        self.assertIsInstance(testee.entity, XC.Entity)
        self.assertEqual(len(testee.conditionIFs), 0)

    def test_TargetNode_2(self):
        '''TargetNode: Deserialize'''
        elem = ElementPath('test/entity/type','entityType')
        SubElement(elem, 'if')
        testee = XC.TargetNode()

        testee.deserialize(elem)

        self.assertEqual(testee.entity.type, 'entityType')
        self.assertEqual(len(testee.conditionIFs), 1)

    def test_TargetNode_3(self):
        '''TargetNode: Serialize'''
        testee = XC.TargetNode()
        testee.entity.type = 'entityType'
        testee.conditionIFs.append(XC.PredicateVariant())

        elem = testee.serialize(Element('test'))

        self.assertEqual(elem.find('entity/type').text, 'entityType')
        self.assertEqual(len(elem.findall('if')), 1)

    def test_TargetNode_4(self):
        '''TargetNode: Ctor'''
        testee = XC.TargetNode()
        self.assertIsInstance(testee.entity, XC.Entity)
        self.assertEqual(len(testee.conditionIFs), 0)


    def test_TargetNode_5(self):
        '''TargetNode: Serialize'''
        testee = XC.TargetNode()
        testee.entity.type = 'entityType'
        testee.conditionIFs.append(XC.PredicateVariant())

        elem = testee.serialize(Element('test'))

        self.assertEqual(elem.find('entity/type').text, 'entityType')
        self.assertEqual(len(elem.findall('if')), 1)

    def test_Mapping_1(self):
        '''Mapping: Ctor, Access'''
        testee = XC.Mapping()
        self.assertIsInstance(testee.domain, XC.Domain)
        self.assertEqual(len(testee.links), 0)

    def test_Mapping_2(self):
        '''Mapping: Deserialize'''
        elem = Element('test')
        domainElem = SubElement(elem, 'domain')
        SubElement(domainElem, 'source_node').text = 'domainPath'
        SubElementPath(domainElem, 'target_node/entity/type').text = 'domainEntity'
        linkElem = SubElement(elem, 'link')
        pathElem = SubElement(linkElem, 'path')
        SubElementPath(pathElem, 'source_relation/relation').text = 'linkPath'
        SubElementPath(pathElem, 'target_relation/relationship').text = 'linkRelationship'
        rangeElem = SubElement(linkElem, 'range')
        SubElement(rangeElem, 'source_node').text = 'linkPath'
        SubElementPath(rangeElem, 'target_node/entity/type').text = 'linkEntity'

        testee = XC.Mapping()
        testee.deserialize(elem)

        self.assertEqual(testee.domain.path, 'domainPath')
        self.assertEqual(testee.domain.entity, 'domainEntity')
        self.assertEqual(len(testee.links), 1)
        self.assertEqual(testee.links[0].path.path, 'linkPath')
        self.assertEqual(testee.links[0].path.entity, 'linkRelationship')
        self.assertEqual(testee.links[0].range.path, 'linkPath')
        self.assertEqual(testee.links[0].range.entity, 'linkEntity')

    def test_Mapping_3(self):
        '''Mapping: Serialize'''
        testee = XC.Mapping()
        testee.domain.set('domainPath', 'domainEntity')
        link = XC.Link()
        link.set('linkPath', 'linkRelationship', 'linkEntity')
        testee.links.append(link)

        elem = testee.serialize(Element('test'))

        self.assertEqual(elem.find('domain/source_node').text, 'domainPath')
        self.assertEqual(elem.find('domain/target_node/entity/type').text, 'domainEntity')
        elemLinks = elem.findall('link')
        self.assertEqual(len(elemLinks), 1)
        self.assertEqual(elemLinks[0].find('path/source_relation/relation').text, 'linkPath')
        self.assertEqual(elemLinks[0].find('path/target_relation/relationship').text, 'linkRelationship')
        self.assertEqual(elemLinks[0].find('range/source_node').text, 'linkPath')
        self.assertEqual(elemLinks[0].find('range/target_node/entity/type').text, 'linkEntity')

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

if __name__ == '__main__':
    unittest.main()
