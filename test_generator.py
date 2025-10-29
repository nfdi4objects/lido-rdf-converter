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
        self.assertIsNot(arg, deserialized)
        self.assertEqual(arg, deserialized)

    def test_custom_serialization(self):
        custom = Custom(
            class_name="TestClass",
            args=[Arg("arg1", "type1"), Arg("arg2", "type2")]
        )
        elem = ET.Element("custom")
        custom.to_xml(elem)
        deserialized = Custom.from_xml(elem)
        self.assertIsNot(custom, deserialized)
        self.assertEqual(custom, deserialized)

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
        self.assertIsNot(generator, deserialized)
        self.assertEqual(generator, deserialized)

    def test_policy_save_load(self):
        generators = [
            Generator(name="gen1", pattern="pattern1"),
            Generator(name="gen2", pattern="pattern2")
        ]

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            save_policy(tmp.name, generators)
            loaded = load_policy(tmp.name)

        self.assertIsNot(generators, loaded)
        self.assertEqual(generators, loaded)

        os.unlink(tmp.name)

    def test_arg_clone(self):
        arg = Arg(name="orig_name", type="orig_type")
        cloned = Arg.clone(arg)
        self.assertIsNot(arg, cloned)
        self.assertEqual(arg, cloned)

    def test_custom_clone(self):
        custom = Custom(class_name="OrigClass", args=[Arg("a1", "t1"), Arg("a2", "t2")])
        cloned = Custom.clone(custom)
        self.assertIsNot(custom, cloned)
        self.assertEqual(custom, cloned)

    def test_generator_clone(self):
        gen = Generator(
            pattern="pat",
            custom=Custom(class_name="C", args=[Arg("x", "tx")]),
            description="desc",
            name="gname",
            prefix="pf",
            shorten="sh",
            type="tt"
        )
        cloned = Generator.clone(gen)
        self.assertIsNot(gen, cloned)
        self.assertEqual(gen, cloned)

if __name__ == '__main__':
    unittest.main()
