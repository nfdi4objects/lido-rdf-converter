from dataclasses import dataclass, asdict, field
import xml.etree.ElementTree as ET

ARG_NAME_TAG = 'name'
ARG_TYPE_TAG = 'type'

@dataclass
class Arg:
    '''Class representing an argument with a name and type.'''
    name: str
    type: str = ''

    def to_xml(self, elem):
        """Serialize the dataclass to an XML string."""
        elem.attrib[ARG_NAME_TAG] = str(self.name)
        elem.attrib[ARG_TYPE_TAG] = str(self.type)
        return elem

    @classmethod
    def from_xml(cls, elem):
        """Deserialize an XML string into a dataclass instance."""
        name = elem.get(ARG_NAME_TAG, '')
        type = elem.get(ARG_TYPE_TAG, '')
        return cls(name=name, type=type)


CUSTOM_CLASS_TAG = 'generatorClass'
CUSTOM_SETARG_TAG = 'set-arg'
@dataclass
class Custom:
    '''Class representing a custom item with arguments.'''
    args: list = field(default_factory=list)
    class_name: str = ''

    def to_xml(self, elem) -> str:
        elem.attrib[CUSTOM_CLASS_TAG] = self.class_name
        for x in self.args:
            x.to_xml(ET.SubElement(elem, CUSTOM_SETARG_TAG))
        return elem
    
    @classmethod
    def from_xml(cls, elem):
        args = [Arg.from_xml(child) for child in elem.findall(f'./{CUSTOM_SETARG_TAG}')]
        class_name = elem.get(CUSTOM_CLASS_TAG, '')
        return cls(class_name=class_name, args=args)

################################################################################################

def get_sub_text(elem, name, dflt=''):
    name_elem = elem.find(f'./{name}')
    if name_elem is not None and name_elem.text is not None:
        return name_elem.text
    return dflt

GEN_CUSTOM_TAG = 'custom'
GEN_PATTERN_TAG = 'pattern'
GEN_DESCRIPTION_TAG = 'description'
GEN_BASETAG = 'generator'

@dataclass
class Generator:
    '''Class representing a generator with pattern, custom, and other attributes.'''
    pattern: str = ''
    custom: Custom | None = None
    description: str = 'Default generator'
    name: str = 'unknown'
    prefix: str = ''
    shorten: str = ''
    type: str = ''

    def to_xml(self, elem):
        '''Serialize the dataclass to an XML element.'''
        ET.SubElement(elem, GEN_DESCRIPTION_TAG).text = self.description
        if self.custom:
            self.custom.to_xml(ET.SubElement(elem, GEN_CUSTOM_TAG))
        if self.pattern:
            ET.SubElement(elem, GEN_PATTERN_TAG).text = self.pattern
            
        elem.attrib['name'] = self.name
        elem.attrib['prefix'] = self.prefix
        elem.attrib['shorten'] = self.shorten
        elem.attrib['type'] = self.type
        return elem

    def save_to_file(self, file_path: str):
        """Save the serialized XML to a file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            elem = ET.Element(GEN_BASETAG)
            file.write(ET.tostring(self.to_xml(elem), encoding='unicode'))

    @classmethod
    def from_xml(cls, root):
        custom = None
        elem = root.find(f'./{GEN_CUSTOM_TAG}')
        if elem is not None:  custom = Custom.from_xml(elem)
        pattern = get_sub_text(root, GEN_PATTERN_TAG)
        description = get_sub_text(root, GEN_DESCRIPTION_TAG)

        return cls(
            custom = custom,
            pattern = pattern,
            description = description,
            name = root.get('name', ''),
            prefix = root.get('prefix', ''),
            shorten = root.get('shorten', ''),
            type = root.get('type', '')
        )

    @classmethod
    def load_from_file(cls, file_path: str):
        """Load and deserialize XML data from a file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            xml_data = file.read()
        return cls.from_xml(ET.fromstring(xml_data))
    
GeneratorPolicy = list[Generator]
POLICY_BASE_TAG = 'generator_policy'

def load_policy(filen_name: str) -> GeneratorPolicy:
    """Load a list of Generators from an XML file."""
    root = ET.parse(filen_name)
    return [Generator.from_xml(child) for child in root.findall(f'./{GEN_BASETAG}')]

def save_policy(filen_name: str, policy: GeneratorPolicy):
    """Save a list of Generators to an XML file."""
    with open(filen_name, 'w', encoding='utf-8') as file:
        root = ET.Element(POLICY_BASE_TAG)
        for gen in policy:
            gen.to_xml(ET.SubElement(root, GEN_BASETAG))
        file.write(ET.tostring(root, encoding='unicode'))
