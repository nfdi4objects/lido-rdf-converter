import unittest
from generator import Arg, Custom, Generator, load_policy, save_policy
import tempfile
import os

import xml.etree.ElementTree as ET

class TestGenerator(unittest.TestCase):
    def test_arg_serialization(self):
        arg = Arg(name="test_name", type="test_type")
        elem = ET.Element("arg")
        arg.to_xml(elem)
        
        deserialized = Arg.from_xml(elem)
        self.assertEqual(arg.name, deserialized.name)
        self.assertEqual(arg.type, deserialized.type)

    def test_custom_serialization(self):
        custom = Custom(
            class_name="TestClass",
            args=[Arg("arg1", "type1"), Arg("arg2", "type2")]
        )
        elem = ET.Element("custom")
        custom.to_xml(elem)
        
        deserialized = Custom.from_xml(elem)
        self.assertEqual(custom.class_name, deserialized.class_name)
        self.assertEqual(len(custom.args), len(deserialized.args))
        self.assertEqual(custom.args[0].name, deserialized.args[0].name)

    def test_generator_serialization(self):
        generator = Generator(
            pattern="test_pattern",
            custom=Custom(class_name="TestClass", args=[Arg("arg1", "type1")]),
            description="Test description",
            name="test_name",
            prefix="test_prefix",
            shorten="test_shorten",
            type="test_type"
        )
        elem = ET.Element("generator")
        generator.to_xml(elem)
        
        deserialized = Generator.from_xml(elem)
        self.assertEqual(generator.pattern, deserialized.pattern)
        self.assertEqual(generator.description, deserialized.description)
        self.assertEqual(generator.name, deserialized.name)

    def test_policy_save_load(self):
        generators = [
            Generator(name="gen1", pattern="pattern1"),
            Generator(name="gen2", pattern="pattern2")
        ]
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            save_policy(tmp.name, generators)
            loaded = load_policy(tmp.name)
            
        self.assertEqual(len(generators), len(loaded))
        self.assertEqual(generators[0].name, loaded[0].name)
        self.assertEqual(generators[1].pattern, loaded[1].pattern)
        
        os.unlink(tmp.name)

if __name__ == '__main__':
    unittest.main()