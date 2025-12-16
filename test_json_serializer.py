import unittest
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Any
import enum
from json_serializer import from_json, to_json
import x3ml_classes as xc
from xml.etree.ElementTree import Element, SubElement


class Color(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass
class Person:
    name: str
    age: int


@dataclass
class Team:
    leader: Person
    members: List[Person]
    scores: Dict[str, int]


class CustomClass:
    def __init__(self, x: int, y: str):
        self.x = x
        self.y = y


def st(str, lang=''):
    r = xc.SimpleText(text=str)
    if lang:
        r.attributes['lang'] = lang
    return r


def create_NR(n: int = 1):
    return xc.NR(node=st(f'node{n}'), relation=st(f'relation{n}'))


def create_NR_list(n: int = 3):
    return [create_NR(i) for i in range(1, n+1)]


def create_domain(s1='d1'):
    return xc.Domain(sourceNode=st(s1), targetNode=xc.TargetNode())

def create_TargetNode(s1='t1'):
    return xc.TargetNode(entity=xc.Entity(), conditions=[], enableC=True)

def create_SourceRelation(s1='s1'):
    return xc.SourceRelation(
        relation=st(s1),
        attributes={"source_attr": "value1"}
    )
    
def create_TragetRelation(s1='t1'):
    return xc.TargetRelation(
        attributes={"target_attr": "value2"}
    )

def create_Path(s1='p1'):
    path = xc.Path(
        sourceRelation=create_SourceRelation('sr1'),
        targetRelation=create_TragetRelation('tr1'),
        comments=[],
        attributes={"path_attr": "value3"}
    )
    return path

def create_link(s1='p1'):
    link = xc.Link(
        path=create_Path('p1'),
        range=xc.Range(sourceNode=st(s1),targetNode=create_TargetNode())
    )
    return link


class TestFromJson(unittest.TestCase):

    def test_primitives_none(self):
        self.assertIsNone(from_json(None, type(None)))

    def test_primitives_str(self):
        self.assertEqual(from_json("hello", str), "hello")

    def test_primitives_int(self):
        self.assertEqual(from_json(42, int), 42)

    def test_primitives_float(self):
        self.assertEqual(from_json(3.14, float), 3.14)

    def test_primitives_bool(self):
        self.assertTrue(from_json(True, bool))
        self.assertFalse(from_json(False, bool))

    def test_any_type(self):
        self.assertEqual(from_json({"key": "value"}, Any), {"key": "value"})

    def test_enum(self):
        result = from_json("red", Color)
        self.assertEqual(result, Color.RED)

    def test_list_of_ints(self):
        result = from_json([1, 2, 3], List[int])
        self.assertEqual(result, [1, 2, 3])

    def test_list_of_strings(self):
        result = from_json(["a", "b"], List[str])
        self.assertEqual(result, ["a", "b"])

    def test_tuple_fixed(self):
        result = from_json([1, "hello"], Tuple[int, str])
        self.assertEqual(result, (1, "hello"))

    def test_tuple_variable(self):
        result = from_json([1, 2, 3], Tuple[int, ...])
        self.assertEqual(result, (1, 2, 3))

    def test_set(self):
        result = from_json([1, 2, 3], Set[int])
        self.assertEqual(result, {1, 2, 3})

    def test_dict(self):
        result = from_json({"a": 1, "b": 2}, Dict[str, int])
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_simple_dataclass(self):
        data = {"name": "Alice", "age": 30}
        result = from_json(data, Person)
        self.assertEqual(result.name, "Alice")
        self.assertEqual(result.age, 30)

    def test_nested_dataclass(self):
        data = {
            "leader": {"name": "Bob", "age": 40},
            "members": [{"name": "Alice", "age": 30}, {"name": "Charlie", "age": 25}],
            "scores": {"round1": 100, "round2": 95}
        }
        result = from_json(data, Team)
        self.assertEqual(result.leader.name, "Bob")
        self.assertEqual(len(result.members), 2)
        self.assertEqual(result.members[0].name, "Alice")
        self.assertEqual(result.scores["round1"], 100)

    def test_dataclass_missing_optional_field(self):
        @dataclass
        class WithDefault:
            x: int = 10
            y: str = "default"

        data = {"x": 20}
        result = from_json(data, WithDefault)
        self.assertEqual(result.x, 20)

    def test_regular_class_with_constructor(self):
        data = {"x": 5, "y": "test"}
        result = from_json(data, CustomClass)
        self.assertEqual(result.x, 5)
        self.assertEqual(result.y, "test")

    def test_roundtrip_simple(self):
        original = Person("Diana", 28)
        json_data = to_json(original)
        reconstructed = from_json(json_data, Person)
        self.assertEqual(reconstructed.name, "Diana")
        self.assertEqual(reconstructed.age, 28)

    def test_roundtrip_complex(self):
        leader = Person("Eve", 45)
        members = [Person("Frank", 35), Person("Grace", 32)]
        original = Team(leader, members, {"task1": 80, "task2": 90})
        json_data = to_json(original)
        reconstructed = from_json(json_data, Team)
        self.assertEqual(reconstructed.leader.name, "Eve")
        self.assertEqual(len(reconstructed.members), 2)
        self.assertEqual(reconstructed.scores["task1"], 80)

    def test_invalid_dataclass_data_type(self):
        with self.assertRaises(TypeError):
            from_json("not a dict", Person)

    def test_list_of_dataclasses(self):
        data = [
            {"name": "Henry", "age": 50},
            {"name": "Iris", "age": 48}
        ]
        result = from_json(data, List[Person])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Henry")

 ######################################################################################

    def test_x3base_base(self):
        data = {
            "attributes": {
                "id": "node1",
                "type": "example"
            }
        }
        result = from_json(data, xc.X3Base)
        self.assertIsInstance(result, xc.X3Base)
        self.assertEqual(result.attributes["id"], "node1")
        self.assertEqual(result.attributes["type"], "example")

    def test_x3base_json_loop(self):
        original = xc.X3Base(attributes={"key": "value"})
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.X3Base)
        self.assertIsInstance(reconstructed, xc.X3Base)
        self.assertEqual(reconstructed.attributes["key"], "value")

    def test_X3Base_deserialize(self):
        elem = Element('x3base', attrib={'id': 'node2', 'category': 'test'})
        x3base_instance = xc.X3Base().deserialize(elem)
        self.assertIsInstance(x3base_instance, xc.X3Base)
        self.assertEqual(x3base_instance.attributes['id'], 'node2')
        self.assertEqual(x3base_instance.attributes['category'], 'test')

    def test_X3Base_serialize_loop(self):
        original = xc.X3Base(attributes={"serialize_key": "serialize_value"})
        elem = original.serialize(Element('x3base'))
        reconstructed = xc.X3Base().deserialize(elem)
        self.assertIsInstance(reconstructed, xc.X3Base)
        self.assertEqual(original, reconstructed)

 ######################################################################################

    def test_predicate_base(self):
        data = {
            "tag": "exists",
            "value": '42',
            "xpath": '---'
        }
        result = from_json(data, xc.Predicate)
        self.assertIsInstance(result, xc.Predicate)
        self.assertEqual(result.tag, "exists")
        self.assertEqual(result.value, '42')
        self.assertEqual(result.xpath, '---')

    def test_equals_json_loop(self):
        original = xc.Equals(value='100', xpath='/some/path')
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.Equals)
        self.assertIsInstance(reconstructed, xc.Equals)
        self.assertEqual(reconstructed.tag, "equals")
        self.assertEqual(reconstructed.value, '100')
        self.assertEqual(reconstructed.xpath, '/some/path')

 ######################################################################################

    def test_simpletext_base(self):
        data = {
            "attributes": {
                "lang": "en"
            },
            "text": "Hello World"
        }
        result = from_json(data, xc.SimpleText)
        self.assertIsInstance(result, xc.SimpleText)
        self.assertEqual(result.attributes["lang"], "en")
        self.assertEqual(result.text, "Hello World")

    def test_simpletext_json_loop(self):
        original = xc.SimpleText(text='Sample Text')
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.SimpleText)
        self.assertIsInstance(reconstructed, xc.SimpleText)
        self.assertEqual(reconstructed.text, 'Sample Text')

    def test_simpletext_loop(self):
        original = xc.SimpleText(text='http://example.com', attributes={'description': 'An example source'})
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.SimpleText)
        self.assertIsInstance(reconstructed, xc.SimpleText)
        self.assertEqual(reconstructed.text, 'http://example.com')
        self.assertEqual(reconstructed.attributes['description'], 'An example source')

    def test_simpletext_serialize_deserialize(self):
        original = xc.SimpleText(text='Deserialize Test', attributes={'key': 'value'})
        elem = original.serialize(Element('simpletext'))
        reconstructed = xc.SimpleText.from_serial(elem)
        self.assertIsInstance(reconstructed, xc.SimpleText)
        self.assertEqual(reconstructed, original)

    ######################################################################################

    def test_Source_base(self):
        data = {
            "attributes": {
                "id": "source1"
            },
            "source_schema": {
                "attributes": {
                    "type": "url"
                },
                "text": "http://example.com"
            }
        }
        result = from_json(data, xc.Source)
        self.assertIsInstance(result, xc.Source)
        self.assertEqual(result.attributes["id"], "source1")
        self.assertIsInstance(result.source_schema, xc.SimpleText)
        self.assertEqual(result.source_schema.text, "http://example.com")
        self.assertEqual(result.source_schema.attributes["type"], "url")

    def test_Source_json_loop(self):
        original = xc.Source(
            attributes={"id": "source2"},
            source_schema=xc.SimpleText(
                text='http://nested.com',
                attributes={'note': 'Nested source node'}
            )
        )
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.Source)
        self.assertIsInstance(reconstructed, xc.Source)
        self.assertEqual(reconstructed.attributes["id"], "source2")
        self.assertIsInstance(reconstructed.source_schema, xc.SimpleText)
        self.assertEqual(reconstructed.source_schema.text, 'http://nested.com')
        self.assertEqual(reconstructed.source_schema.attributes['note'], 'Nested source node')

    def test_Source_loop(self):
        original = xc.Source(
            attributes={"id": "source3"},
            source_schema=xc.SimpleText(
                text='http://loop.com',
                attributes={'info': 'Loop test'}
            )
        )
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.Source)
        self.assertIsInstance(reconstructed, xc.Source)
        self.assertEqual(reconstructed.attributes["id"], "source3")
        self.assertIsInstance(reconstructed.source_schema, xc.SimpleText)
        self.assertEqual(reconstructed.source_schema.text, 'http://loop.com')
        self.assertEqual(reconstructed.source_schema.attributes['info'], 'Loop test')

    ######################################################################################
    def test_Target_loop(self):
        original = xc.Target(
            attributes={"id": "target1"},
            target_schema=xc.SimpleText(
                text='http://target.com',
                attributes={'detail': 'Target node'}
            )
        )
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.Target)
        self.assertIsInstance(reconstructed, xc.Target)
        self.assertEqual(reconstructed.attributes["id"], "target1")
        self.assertIsInstance(reconstructed.target_schema, xc.SimpleText)
        self.assertEqual(reconstructed.target_schema.text, 'http://target.com')
        self.assertEqual(reconstructed.target_schema.attributes['detail'], 'Target node')
        self.assertEqual(reconstructed, original)

    def test_target_serialize_deserialize(self):
        original = xc.Target(
            attributes={"id": "target2"},
            target_schema=xc.SimpleText(
                text='http://serialize.com',
                attributes={'info': 'Serialize test'}
            )
        )
        elem = original.serialize(Element('target'))
        reconstructed = xc.Target.from_serial(elem)
        self.assertEqual(reconstructed, original)

    ######################################################################################

    def test_MappingInfo_serialize(self):
        original = xc.MappingInfo()
        serial = original.serialize(Element('mappinginfo'))
        self.assertEqual(serial.tag, 'mappinginfo')
        self.assertIsNotNone(serial.find('mapping_created_by_org'))
        self.assertIsNotNone(serial.find('mapping_created_by_person'))
        self.assertIsNotNone(serial.find('in_collaboration_with'))

    def test_mappinginfo_deserialize(self):
        elem = Element('mappinginfo')
        SubElement(elem, 'mapping_created_by_org')
        SubElement(elem, 'mapping_created_by_person')
        SubElement(elem, 'in_collaboration_with')
        mappinginfo_instance = xc.MappingInfo().deserialize(elem)
        self.assertIsInstance(mappinginfo_instance, xc.MappingInfo)
        self.assertEqual(mappinginfo_instance, xc.MappingInfo())

    def test_mappinginfo_json_loop(self):
        original = xc.MappingInfo()
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.MappingInfo)
        self.assertIsInstance(reconstructed, xc.MappingInfo)
        self.assertEqual(reconstructed, original)

    ######################################################################################

    def test_Link_json_loop(self):
        original = xc.Link(
            path=xc.Path(
                attributes={"step": "1"},
                sourceRelation=xc.SourceRelation(
                    attributes={"type": "source"},
                    relation=xc.SimpleText(text="related")
                ),
                targetRelation=xc.TargetRelation(
                    attributes={"type": "target"}
                )
            ),
            range=xc.Range()
        )
        json_data = to_json(original)
        reconstructed = from_json(json_data, xc.Link)
        self.assertIsInstance(reconstructed, xc.Link)
        self.assertEqual(reconstructed.path, original.path)
        self.assertEqual(reconstructed.range, original.range)
        self.assertEqual(reconstructed.attributes, original.attributes)

    def test_Link_xml_loop(self):
        original = create_link('path1')
        data = original.serialize(Element('link'))
        reconstructed = xc.Link.from_serial(data)
        self.assertIsInstance(reconstructed, xc.Link)
        self.assertEqual(reconstructed, original)


if __name__ == "__main__":
    unittest.main()
