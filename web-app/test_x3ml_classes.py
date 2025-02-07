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


def makeElementsPath(root: ET.Element, names: list) -> ET.Element | None:
    '''Creates a chain of Elements '''
    if len(names) == 0:
        return root
    else:
        subElem = ET.SubElement(root, names.pop(0))
        return makeElementsPath(subElem, names)


def makeElementsPathS(root: ET.Element, path: str) -> ET.Element | None:
    '''Creates a chain of Elements '''
    names = path.split('/') if len(path) else []
    return makeElementsPath(root, names)

class testOpTrue(XC.Or):

    def isValid(self, elem):
        return True


class testOpFalse(XC.Or):

    def isValid(self, elem):
        return False

def makeIfOr(trueFalse):
    tIf = XC.If()
    tIf.op = testOpTrue() if trueFalse else testOpFalse()
    return tIf


class Test_X3ml_Classes(unittest.TestCase):

    def setUp(self):
        pass

    def test_Serializer(self):
        '''Serializer: Ctor, JSON'''
        testee = XC.Serializer()
        testee.y = 5
        self.assertEqual(testee.toJSON(), '{\n  "y": 5\n}')

    def test_X3Base_1(self):
        '''X3Base: Ctor, Attributes'''
        testee = makeX3Base()
        self.assertEqual(testee.getAttr('A'), 44)
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_X3Base_2(self):
        '''X3Base: Ctor, Serial, Attributes'''
        testee = XC.X3Base(makeElem())
        self.assertEqual(testee.getAttr('A'), 'a')
        self.assertEqual(testee.getAttr('B'), 2)

    def test_X3Base_3(self):
        '''X3Base: Ctor, De/Serial, Attributes'''
        elem = makeX3Base().serialize(ET.Element('test'))
        testee = XC.X3Base()
        testee.deserialize(elem)
        self.assertEqual(testee.getAttr('A'), 44)
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_X3Base_4(self):
        '''X3Base: Ctor, De/Serial, Attributes'''
        elem = makeX3Base().serialize(ET.Element('test'))
        testee = XC.X3Base(elem)
        self.assertEqual(testee.getAttr('A'), 44)
        self.assertEqual(testee.getAttr('B'), 'ZZ')

    def test_SimpleText_1(self):
        '''SimpleText: Access,Serial'''
        testee = XC.SimpleText()
        self.assertEqual(testee.text, '')
        self.assertEqual(testee.alias(), '')

        elem = ET.Element('test')
        elem.text = '\\lido:lido'
        testee.deserialize(elem)
        self.assertEqual(testee.text, '\\lido:lido')
        self.assertEqual(testee.alias(), '\\lido')

    def test_SimpleText_2(self):
        '''SimpleText: Access, Serial, Str'''
        elem = ET.Element('test')
        elem.text = 'lido:event'

        testee = XC.SimpleText()
        testee.deserialize(elem)
        self.assertEqual(testee.text, 'lido:event')
        self.assertEqual(testee.alias(), 'event')
        self.assertEqual(str(testee), 'SimpleText\tlido:event')

    def test_Source_1(self):
        '''Source: Ctor, Access, Serial'''
        elem = ET.Element('test')
        makeElementsPath(elem, ['source_info', 'source_schema']).text = 'schema'

        testee = XC.Source()
        testee.deserialize(elem)
        self.assertIsNotNone(testee.source_schema)
        self.assertEqual(type(testee.source_schema).__name__, 'SimpleText')
        self.assertEqual(testee.source_schema.text, 'schema')

    def test_Source_2(self):
        '''Source: Ctor, Access, Serial'''
        testee = XC.Source()
        testee.set('schema')
        elem = testee.serialize(ET.Element('test'))
        subElem = elem.findall('source_info/source_schema')
        self.assertEqual(len(subElem), 1)
        self.assertEqual(subElem[0].text, 'schema')

    def test_Target_1(self):
        '''Target: Ctor, Access, Serial'''
        elem = ET.Element('test')
        makeElementsPath(elem, ['target_info', 'target_schema']).text = 'schema'

        testee = XC.Target()
        testee.deserialize(elem)
        self.assertIsNotNone(testee.target_schema)
        self.assertEqual(type(testee.target_schema).__name__, 'SimpleText')
        self.assertEqual(testee.target_schema.text, 'schema')

    def test_Target_2(self):
        '''Target: Ctor, Access, Serial'''
        testee = XC.Target()
        testee.set('schema')
        elem = testee.serialize(ET.Element('test'))
        subElems = elem.findall('target_info/target_schema')
        self.assertEqual(len(subElems), 1)
        self.assertEqual(subElems[0].text, 'schema')

    def test_MappingInfo_1(self):
        '''MappingInfo 2: Ctor,  Serial'''
        testee = XC.MappingInfo()
        elem = testee.serialize(ET.Element('test'))
        self.assertIsNotNone(elem.find('mapping_created_by_org'))
        self.assertIsNotNone(elem.find('mapping_created_by_org'))
        self.assertIsNotNone(elem.find('in_collaboration_with'))

        testee = XC.Comment()
    def test_Comment_1(self):
        '''Comment: Ctor,  Serial'''
        testee = XC.Comment()
        elem = testee.serialize(ET.Element('test'))
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
        elem = testee.serialize(ET.Element('test'))
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
        elem = ET.Element('test')
        makeElementsPath(elem, ['title']).text = 'title'
        makeElementsPath(elem, ['source', 'source_info', 'source_schema']).text = 'sinfo'
        makeElementsPath(elem, ['target', 'target_info', 'target_schema']).text = 'tinfo'

        testee = XC.Info()
        testee.deserialize(elem)
        self.assertEqual(testee.title.text, 'title')
        self.assertEqual(testee.sSchema, 'sinfo')
        self.assertEqual(testee.tSchema, 'tinfo')

    def test_Info_3(self):
        '''Info: Serialize'''
        info = XC.Info()
        info.title.text = 'title'

        elem = info.serialize(ET.Element('test'))
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

        testee = ET.Element('test')
        testee = namespace.serialize(testee)
        self.assertEqual(testee.attrib['prefix'], 'crm')
        self.assertEqual(testee.attrib['uri'], 'http://cidoc.com')

    def test_Namespace_3(self):
        '''Namespace: Serial'''
        elem = ET.Element('test', attrib={'prefix': 'crm', 'uri': 'http://cidoc.com'})

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
        '''Domain: Ctro, DeSerial'''
        elem = ET.Element('test')
        makeElementsPath(elem, ['source_node']).text = 'ABC'
        makeElementsPath(elem, ['target_node', 'entity', 'type']).text = 'XYZ'

        testee = XC.Domain(elem)

        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'XYZ')

    def test_Domain_3(self):
        '''Domain: Serial'''
        testee = XC.Domain()
        testee.set('ABC', 'XYZ')
        elem = ET.Element('test')

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
        elem = ET.Element('test')
        testee = XC.NR.create('ABC', 'XYZ')

        testee.serialize(elem)

        self.assertEqual(elem.find('node').text, 'ABC')
        self.assertEqual(elem.find('relation').text, 'XYZ')

    def test_NR_3(self):
        '''NR: Deserial'''
        elem = ET.Element('test')
        makeElementsPath(elem, ['node']).text = 'ABC'
        makeElementsPath(elem, ['relation']).text = 'XYZ'
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
        elem = ET.Element('test')

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
        elem = ET.Element('test')
        makeElementsPath(elem, ['relation']).text = 'ABC'
        makeElementsPath(elem, ['relation']).text = 'R0'
        makeElementsPath(elem, ['relation']).text = 'R1'
        makeElementsPath(elem, ['node']).text = 'N0'
        makeElementsPath(elem, ['node']).text = 'N1'
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
        elem = ET.Element('test')

        testee.serialize(elem)

        self.assertEqual(elem.find('source_relation/relation').text, 'ABC')
        self.assertEqual(elem.find('target_relation/relationship').text, 'xyz')
        comments = elem.findall('comments/comment/rationale')
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].text, 'a comment')
        self.assertEqual(comments[1].text, 'a comment 2')

    def test_Path_3(self):
        '''Path: DeSerial'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'source_relation/relation').text = 'ABC'
        makeElementsPathS(elem, 'target_relation/relationship').text = 'xyz'
        comsElem = makeElementsPathS(elem, 'comments')
        makeElementsPathS(comsElem, 'comment/rationale').text = 'comment 1'
        makeElementsPathS(comsElem, 'comment/rationale').text = 'comment 2'
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
        elem = ET.Element('test')

        testee.serialize(elem)

        self.assertEqual(elem.find('source_node').text, 'ABC')
        self.assertEqual(elem.find('target_node/entity/type').text, 'xyz')

    def test_Range_3(self):
        '''Range: DeSerial'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'source_node').text = 'ABC'
        makeElementsPathS(elem, 'target_node/entity/type').text = 'xyz'
        testee = XC.Range()

        testee.deserialize(elem)
        self.assertEqual(testee.path, 'ABC')
        self.assertEqual(testee.entity, 'xyz')

    def test_LogicalOp_1(self):
        '''LogicalOp: Ctor, Access'''
        testee = XC.LogicalOp(None, 'aTag')
        self.assertEqual(testee.tag, 'aTag')
        self.assertEqual(testee.xpath, '')

    def test_LogicalOp_2(self):
        '''LogicalOp: Serial'''
        testee = XC.LogicalOp()
        testee._ifs.append(XC.If())
        testee._ifs.append(XC.If())
        elem = ET.Element('test')

        testee.serialize(elem)

        _ifs = elem.findall('if/or')
        self.assertEqual(len(_ifs), 2)
        # TODO

    def test_LogicalOp_3(self):
        '''LogicalOp: DeSerial'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'if/or')
        makeElementsPathS(elem, 'if/and')
        testee = XC.LogicalOp()

        testee.deserialize(elem)

        self.assertEqual(len(testee._ifs), 2)
        self.assertIsInstance(testee._ifs[0], XC.If)
        self.assertIsInstance(testee._ifs[0].op, XC.Or)
        self.assertIsInstance(testee._ifs[1], XC.If)
        self.assertIsInstance(testee._ifs[1].op, XC.And)
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
        testee = XC.ConditionsType(None)
        self.assertIsInstance(testee.op, XC.Or)

    def test_ConditionsType_2(self):
        '''ConditionsType: Serial'''
        testee = XC.ConditionsType(None)
        elem = ET.Element('test')
        testee.serialize(elem)

        self.assertEqual(len(elem.findall('or')), 1)
        self.assertIsNotNone(elem.find('or').tag, 'or')

    def test_ConditionsType_3(self):
        '''ConditionsType: DeSerial'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'or')
        testee = XC.ConditionsType(None)

        testee.deserialize(elem)

        self.assertIsInstance(testee.op, XC.Or)
    
    def test_OR_1(self):
        elem = ET.Element('test')
        testee = XC.Or()

        testee._ifs = [makeIfOr(False),makeIfOr(False)]
        self.assertFalse(testee.isValid(elem))

        testee._ifs = [makeIfOr(False),makeIfOr(True)]
        self.assertTrue(testee.isValid(elem))

        testee._ifs = [makeIfOr(True),makeIfOr(False)]
        self.assertTrue(testee.isValid(elem))

        testee._ifs = [makeIfOr(True),makeIfOr(True)]
        self.assertTrue(testee.isValid(elem))

    def test_OR_2(self):
        '''OR: serialize'''
        elem = ET.Element('or')
        testee = XC.Or()
        if1 = testee.append(XC.If())
        op1 = if1.setOp(XC.Equals())
        op1.value ='value1'
        op1.xpath ='xpath1'
        if2 =testee.append(XC.If())
        op2 = if2.setOp(XC.Equals())
        op2.value ='value2'
        op2.xpath ='xpath2'
      
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
        testee = XC.Or( ET.XML(data))
        self.assertEqual(len(testee._ifs),2)
        for n in range(2):
            ifn = testee._ifs[n]
            self.assertIsInstance(ifn,XC.If)
            op = ifn.op
            self.assertIsInstance(op,XC.Equals)
            self.assertEqual(len(op._ifs),0)
            self.assertEqual(op.value,f'value{n+1}')
            self.assertEqual(op.xpath,f'xpath{n+1}')
    
    def test_OR_4(self):
        '''OR: validate element'''
        data = '''<or>
                     <if><equals value="valueÖ">a/b/c/text()</equals></if>
                     <if><equals value="value2">a/b/c/text()</equals></if>
                  </or>'''
        testee = XC.Or( ET.XML(data))

        self.assertIsInstance(testee,XC.Or)
        self.assertEqual(len(testee._ifs),2)
        
        elem =  ET.XML('<x><a><b><c>valueÖ</c></b></a></x>')
        self.assertTrue(testee.isValid(elem))
        elem =  ET.XML('<x><a><b><c>value2</c></b></a></x>')
        self.assertTrue(testee.isValid(elem))
        elem =  ET.XML('<x><a><b><c>value3</c></b></a></x>')
        self.assertFalse(testee.isValid(elem))

    def test_AND_1(self):
        '''And: validate dummy'''
        elem = ET.Element('test')
        testee = XC.And()

        testee._ifs = [makeIfOr(False),makeIfOr(False)]
        self.assertFalse(testee.isValid(elem))

        testee._ifs = [makeIfOr(False),makeIfOr(True)]
        self.assertFalse(testee.isValid(elem))

        testee._ifs = [makeIfOr(True),makeIfOr(False)]
        self.assertFalse(testee.isValid(elem))

        testee._ifs = [makeIfOr(True),makeIfOr(True)]
        self.assertTrue(testee.isValid(elem))

    def test_AND_2(self):
        '''AND: validate element'''
        data = '''<or>
                     <if><equals value="valueÖ">a/b/c/text()</equals></if>
                     <if><equals value="value2">a/b/d/text()</equals></if>
                  </or>'''
        testee = XC.And( ET.XML(data))

        self.assertIsInstance(testee,XC.And)
        self.assertEqual(len(testee._ifs),2)
        
        elem =  ET.XML('<x><a><b> <c>valueÖ</c> <d>value2</d> </b></a></x>')
        self.assertTrue(testee.isValid(elem))
        elem =  ET.XML('<x><a><b> <c>value</c> <d>value2</d> </b></a></x>')
        self.assertFalse(testee.isValid(elem))
        elem =  ET.XML('<x><a><b> <c>valueÖ</c> <d>value</d> </b></a></x>')
        self.assertFalse(testee.isValid(elem))
        elem =  ET.XML('<x><a><b> <c>valueX</c> <d>valueY</d> </b></a></x>')
        self.assertFalse(testee.isValid(elem))

    def test_IF_1(self):
        '''If: Ctor'''
        testee = XC.If()
        self.assertIsInstance(testee.op, XC.Or)

    def test_IF_2(self):
        '''If: logic'''
        testee = XC.If()
        self.assertFalse(testee.isValid(None))
        elem = ET.Element('test')
        testee.op = testOpTrue()
        self.assertTrue(testee.isValid(elem))
        testee.op = testOpFalse()
        self.assertFalse(testee.isValid(elem))


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
        elem = ET.Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('path/source_relation/relation').text, 'aPath')
        self.assertEqual(elem.find('path/target_relation/relationship').text, 'aRS')
        self.assertEqual(elem.find('range/source_node').text, 'aPath')
        self.assertEqual(elem.find('range/target_node/entity/type').text, 'anEntity')

    def test_Link_3(self):
        '''Link: DeSerial'''
        elem = ET.Element('test')
        pathElem = ET.SubElement(elem, 'path')
        makeElementsPathS(pathElem, 'source_relation/relation').text = 'aPath'
        makeElementsPathS(pathElem, 'target_relation/relationship').text = 'aRS'
        rangeElem = ET.SubElement(elem, 'range')
        makeElementsPathS(rangeElem, 'source_node').text = 'aPath'
        makeElementsPathS(rangeElem, 'target_node/entity/type').text = 'anEntity'
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
        elem = ET.Element('test')
        makeElementsPathS(elem, 'type').text = 'entityType'
        instance_info_elem = makeElementsPathS(elem, 'instance_info')
        makeElementsPathS(instance_info_elem, 'constant')

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

        elem = ET.Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('type').text, 'entityType')
        self.assertEqual(len(elem.findall('instance_info')), 1)
        self.assertIsNotNone(elem.find('instance_info/constant'))

    def test_TargetExtenion_1(self):
        '''TargetExtenion: Ctor, Access'''
        entity = XC.Entity()
        relationship = XC.Relationship()
        testee = XC.TargetExtenion(entity, relationship)
        self.assertIsInstance(testee.entity, XC.Entity)
        self.assertIsInstance(testee.relationship, XC.Relationship)

    def test_TargetExtenion_2(self):
        '''TargetExtenion: Serialize'''
        entity = XC.Entity()
        entity.type = 'entityType'
        relationship = XC.Relationship()
        relationship.text = 'relationshipType'
        testee = XC.TargetExtenion(entity, relationship)

        elem = ET.Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('entity/type').text, 'entityType')
        self.assertEqual(elem.find('relationship').text, 'relationshipType')

    def test_TargetExtenion_3(self):
        '''TargetExtenion: Deserialize'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'entity/type').text = 'entityType'
        makeElementsPathS(elem, 'relationship').text = 'relationshipType'
                
        testee = XC.TargetExtenion(XC.Entity(), XC.Relationship())
        testee.deserialize(elem)
                
        self.assertEqual(testee.entity.type, 'entityType')
        self.assertEqual(testee.relationship.text, 'relationshipType')

    def test_TargetRelationType_1(self):
        '''TargetRelationType: Ctor, Access'''
        testee = XC.TargetRelationType()
        self.assertEqual(testee.relationship.text, '')
        self.assertEqual(len(testee.ifs), 0)
        self.assertEqual(len(testee.extensions), 0)

    def test_TargetRelationType_2(self):
        '''TargetRelationType: Deserialize'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'relationship').text = 'relationshipType'
        makeElementsPathS(elem, 'if')
        makeElementsPathS(elem, 'entity/type').text = 'entityType'
        makeElementsPathS(elem, 'relationship').text = 'intermediateRelationship'

        testee = XC.TargetRelationType()
        testee.deserialize(elem)

        #self.assertEqual(testee.relationship.text, 'relationshipType')
        self.assertEqual(len(testee.ifs), 1)
        self.assertEqual(len(testee.extensions), 1)
        self.assertEqual(testee.extensions[0].entity.type, 'entityType')
        #self.assertEqual(testee.iterMediates[0].relationship.text, 'intermediateRelationship')

    def test_TargetRelationType_3(self):
        '''TargetRelationType: Serialize'''
        testee = XC.TargetRelationType()
        testee.relationship.text = 'relationshipType'
        testee.ifs.append(XC.If())
        intermediate = XC.TargetExtenion(XC.Entity(), XC.Relationship())
        intermediate.entity.type = 'entityType'
        intermediate.relationship.text = 'intermediateRelationship'
        testee.extensions.append(intermediate)

        elem = testee.serialize(ET.Element('test'))

        self.assertEqual(elem.find('relationship').text, 'relationshipType')
        self.assertEqual(len(elem.findall('if')), 1)
        self.assertEqual(elem.find('entity/type').text, 'entityType')
        #self.assertEqual(elem.find('relationship').text, 'intermediateRelationship')

    def test_RangeTargetNodeType_1(self):
        '''RangeTargetNodeType: Ctor, Access'''
        testee = XC.RangeTargetNodeType()
        self.assertIsInstance(testee.entity, XC.Entity)
        self.assertEqual(len(testee.ifs), 0)

    def test_RangeTargetNodeType_2(self):
        '''RangeTargetNodeType: Deserialize'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'entity/type').text = 'entityType'
        makeElementsPathS(elem, 'if')
        testee = XC.RangeTargetNodeType()

        testee.deserialize(elem)

        self.assertEqual(testee.entity.type, 'entityType')
        self.assertEqual(len(testee.ifs), 1)

    def test_RangeTargetNodeType_3(self):
        '''RangeTargetNodeType: Serialize'''
        testee = XC.RangeTargetNodeType()
        testee.entity.type = 'entityType'
        testee.ifs.append(XC.If())

        elem = testee.serialize(ET.Element('test'))

        self.assertEqual(elem.find('entity/type').text, 'entityType')
        self.assertEqual(len(elem.findall('if')), 1)

    def test_RangeTargetNodeType_4(self):
        '''RangeTargetNodeType: Ctor'''
        testee = XC.RangeTargetNodeType()
        self.assertIsInstance(testee.entity, XC.Entity)
        self.assertEqual(len(testee.ifs), 0)

    def test_RangeTargetNodeType_5(self):
        '''RangeTargetNodeType: Deserialize'''
        elem = ET.Element('test')
        makeElementsPathS(elem, 'entity/type').text = 'entityType'
        makeElementsPathS(elem, 'if')
        testee = XC.RangeTargetNodeType()

        testee.deserialize(elem)

        self.assertEqual(testee.entity.type, 'entityType')
        self.assertEqual(len(testee.ifs), 1)

    def test_RangeTargetNodeType_6(self):
        '''RangeTargetNodeType: Serialize'''
        testee = XC.RangeTargetNodeType()
        testee.entity.type = 'entityType'
        testee.ifs.append(XC.If())

        elem = testee.serialize(ET.Element('test'))

        self.assertEqual(elem.find('entity/type').text, 'entityType')
        self.assertEqual(len(elem.findall('if')), 1)

    def test_Mapping_1(self):
        '''Mapping: Ctor, Access'''
        testee = XC.Mapping()
        self.assertIsInstance(testee.domain, XC.Domain)
        self.assertEqual(len(testee.links), 0)

    def test_Mapping_2(self):
        '''Mapping: Deserialize'''
        elem = ET.Element('test')
        domainElem = makeElementsPathS(elem, 'domain')
        makeElementsPathS(domainElem, 'source_node').text = 'domainPath'
        makeElementsPathS(domainElem, 'target_node/entity/type').text = 'domainEntity'
        linkElem = makeElementsPathS(elem, 'link')
        pathElem = makeElementsPathS(linkElem, 'path')
        makeElementsPathS(pathElem, 'source_relation/relation').text = 'linkPath'
        makeElementsPathS(pathElem, 'target_relation/relationship').text = 'linkRelationship'
        rangeElem = makeElementsPathS(linkElem, 'range')
        makeElementsPathS(rangeElem, 'source_node').text = 'linkPath'
        makeElementsPathS(rangeElem, 'target_node/entity/type').text = 'linkEntity'

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

        elem = testee.serialize(ET.Element('test'))

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
        elem = ET.Element('test')
        makeElementsPathS(elem, 'info/title').text = 'infoTitle'
        makeElementsPathS(elem, 'namespaces/namespace').attrib = {'prefix': 'nsPrefix', 'uri': 'nsUri'}
        domainElem = makeElementsPathS(elem, 'mappings/mapping/domain')
        makeElementsPathS(domainElem, 'source_node').text = 'domainPath'
        makeElementsPathS(domainElem, 'target_node/entity/type').text = 'domainEntity'

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

        elem = ET.Element('test')
        testee.serialize(elem)

        self.assertEqual(elem.find('info/title').text, 'infoTitle')
        self.assertEqual(elem.find('namespaces/namespace').attrib['prefix'], 'nsPrefix')
        self.assertEqual(elem.find('namespaces/namespace').attrib['uri'], 'nsUri')
        self.assertEqual(elem.find('mappings/mapping/domain/source_node').text, 'domainPath')
        self.assertEqual(elem.find('mappings/mapping/domain/target_node/entity/type').text, 'domainEntity')

if __name__ == '__main__':
    unittest.main()
