import unittest
import x3ml_classes as XC


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        pass

    def test_t0000_serial(self):
        testee = XC.Serializer()
        testee.y = 5
        self.assertEqual(testee.toJSON(), '{\n  "y": 5\n}') 

    def test_t0001_attr(self):
        testee = XC.Attribute('k')
        self.assertEqual(testee.key, 'k')
        self.assertEqual(testee.value, '')
        self.assertEqual(str(testee), 'k:')
        self.assertEqual(testee.toJSON(), '{\n  "key": "k",\n  "value": ""\n}') 

    def test_t0002_attr(self):
        testee = XC.Attribute('myKey', 'myValue')
        self.assertEqual(testee.key, 'myKey')
        self.assertEqual(testee.value, 'myValue')
        self.assertEqual(str(testee), 'myKey:myValue')
        self.assertEqual(testee.toJSON(), '{\n  "key": "myKey",\n  "value": "myValue"\n}') 



if __name__ == '__main__':
    unittest.main()
