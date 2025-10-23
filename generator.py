from dataclasses import dataclass, asdict, field
import xml.etree.ElementTree as ET

ARG_NAME_TAG = 'name'
ARG_TYPE_TAG = 'type'

@dataclass
class Arg:
    '''Class representing an argument with a name and type.'''
    name: str
    type: str = ''

    def to_xml(self, root):
        """Serialize the dataclass to an XML string."""
        root.attrib[ARG_NAME_TAG] = str(self.name)
        root.attrib[ARG_TYPE_TAG] = str(self.type)
        return root

    @classmethod
    def from_xml(cls, root):
        """Deserialize an XML string into a dataclass instance."""
        name = root.get(ARG_NAME_TAG, '')
        type = root.get(ARG_TYPE_TAG, '')
        return cls(name=name, type=type)


CUSTOM_CLASS_TAG = 'generatorClass'
CUSTOM_SETARG_TAG = 'set-arg'
@dataclass
class Custom:
    '''Class representing a custom item with arguments.'''
    args: list = field(default_factory=list)
    class_name: str = ''

    def to_xml(self, root) -> str:
        root.attrib[CUSTOM_CLASS_TAG] = self.class_name
        for x in self.args:
            x.to_xml(ET.SubElement(root, CUSTOM_SETARG_TAG))
        return root
    
    @classmethod
    def from_xml(cls, root):
        args = [Arg.from_xml(child) for child in root.findall(f'./{CUSTOM_SETARG_TAG}')]
        class_name = root.get(CUSTOM_CLASS_TAG, '')
        return cls(class_name=class_name, args=args)

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

    def to_xml(self, root):
        '''Serialize the dataclass to an XML element.'''
        ET.SubElement(root, GEN_DESCRIPTION_TAG).text = self.description
        if self.custom:
            self.custom.to_xml(ET.SubElement(root, GEN_CUSTOM_TAG))
        if self.pattern:
            ET.SubElement(root, GEN_PATTERN_TAG).text = self.pattern
            
        root.attrib['name'] = self.name
        root.attrib['prefix'] = self.prefix
        root.attrib['shorten'] = self.shorten
        root.attrib['type'] = self.type
        return root

    def save_to_file(self, file_path: str):
        """Save the serialized XML to a file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            root = ET.Element(GEN_BASETAG)
            file.write(ET.tostring(self.to_xml(root), encoding='unicode'))

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
