import unittest
import rdflib
from getCidocInfo import graphFromFile, namespaces2dict, QNameInfo, getQNameInfos

class TestGetCidocInfo(unittest.TestCase):

    def setUp(self):
        self.file_path = 'CIDOC_CRM_v7.1.1.rdf'
        self.graph = graphFromFile(self.file_path)

    def test_graphFromFile(self):
        graph = graphFromFile(self.file_path)
        self.assertIsInstance(graph, rdflib.Graph)
        self.assertGreater(len(graph), 0)

    def test_namespaces2dict(self):
        namespaces = namespaces2dict(self.graph)
        self.assertIsInstance(namespaces, dict)
        self.assertIn('crm', namespaces)
        self.assertIn('skos', namespaces)

    def test_QNameInfo(self):
        info = QNameInfo('http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity')
        self.assertEqual(info.prefix, '')
        self.assertEqual(info.entity, 'http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity')
        
        info = QNameInfo('crm:E1')
        self.assertEqual(info.prefix, 'crm')
        self.assertEqual(info.entity, 'E1')
        self.assertEqual(str(info), 'crm:E1')

    def test_getQNameInfos(self):
        data = getQNameInfos(self.graph, source=self.file_path)
        self.assertIsInstance(data, dict)
        self.assertIn('source', data)
        self.assertIn('namespaces', data)
        self.assertIn('classes', data)
        self.assertIn('properties', data)
        self.assertEqual(data['source'], self.file_path)
        self.assertIsInstance(data['namespaces'], dict)
        self.assertIsInstance(data['classes'], list)
        self.assertIsInstance(data['properties'], list)

if __name__ == '__main__':
    unittest.main()