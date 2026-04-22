import unittest
import rdflib
from libs.getCidocInfo import createGraph,  QNameInfo, readGraph


class TestGetCidocInfo(unittest.TestCase):

    def setUp(self):
        self.file_path = 'CIDOC_CRM_v7.1.1.rdf'

    def test_QNameInfo(self):
        info = QNameInfo('http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity')
        self.assertEqual(info.prefix, '')
        self.assertEqual(
            info.entity, 'http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity')

        info = QNameInfo('crm:E1')
        self.assertEqual(info.prefix, 'crm')
        self.assertEqual(info.entity, 'E1')
        self.assertEqual(str(info), 'crm:E1')

    def test_getQNameInfos(self):
        graph = createGraph()
        graph.parse(self.file_path)
        namespaces = {}
        classes = set()
        properties = set()
        readGraph(graph, properties, classes, namespaces)        

        self.assertIsInstance(namespaces, dict)
        self.assertIsInstance(classes, set)
        self.assertIsInstance(properties, set)


if __name__ == '__main__':
    unittest.main()
