import x3ml_classes as XC 
import xml.etree.ElementTree as ET

import unittest

class TestStringMethods(unittest.TestCase):

    model = XC.X3ml()
    tree = ET.parse(filePath)
    model.deserialize(tree.getroot())

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()