from dataclasses import dataclass, asdict, field
import xml.etree.ElementTree as ET

################################################################################################

ARG_NAME_TAG = 'name'
ARG_TYPE_TAG = 'type'
@dataclass
class Arg:
    '''Class representing an argument with a name and type.'''
    name: str
    type: str = ''
    
    def clone(self):
        return Arg(name=self.name, type=self.type)

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


################################################################################################

CUSTOM_CLASS_TAG = 'generatorClass'
CUSTOM_SETARG_TAG = 'set-arg'
@dataclass
class Custom:
    '''Class representing a custom item with arguments.'''
    args: list[Arg] = field(default_factory=list)
    class_name: str = ''

    def to_xml(self, elem) -> str:
        elem.attrib[CUSTOM_CLASS_TAG] = self.class_name
        for arg in self.args:
            arg.to_xml(ET.SubElement(elem, CUSTOM_SETARG_TAG))
        return elem
    
    def clone(self):
        return Custom(
            class_name=self.class_name,
            args=[arg.clone() for arg in self.args]
        )
    
    @classmethod
    def from_xml(cls, elem):
        args = [Arg.from_xml(child) for child in elem.findall(f'{CUSTOM_SETARG_TAG}')]
        class_name = elem.get(CUSTOM_CLASS_TAG, '')
        return cls(class_name=class_name, args=args)

################################################################################################

def get_sub_text(elem, name, dflt=''):
    '''Retrieve text from a sub-element, returning a default if not found.'''
    child = elem.find(f'{name}')
    if child is not None and child.text is not None:
        return child.text
    return dflt

def get_sub_class(elem, name, cls):
    '''Retrieve and deserialize a sub-element into a class instance.'''
    child = elem.find(f'{name}')
    if child is not None:
        return cls.from_xml(child)
    return None

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
    
    def clone(self):
        return Generator(
            pattern=self.pattern,
            custom=self.custom.clone() if self.custom else None,
            description=self.description,
            name=self.name,
            prefix=self.prefix,
            shorten=self.shorten,
            type=self.type
        )

    def to_xml(self, elem):
        '''Serialize the dataclass to an XML element.'''
        ET.SubElement(elem, GEN_DESCRIPTION_TAG).text = self.description
        ET.SubElement(elem, GEN_PATTERN_TAG).text = self.pattern
        if self.custom:
            self.custom.to_xml(ET.SubElement(elem, GEN_CUSTOM_TAG))
            
        elem.attrib['name'] = self.name
        elem.attrib['prefix'] = self.prefix
        elem.attrib['shorten'] = self.shorten
        elem.attrib['type'] = self.type
        return elem

    @classmethod
    def from_xml(cls, elem):
        '''Deserialize an XML element into a dataclass instance.'''
        return cls(
            custom = get_sub_class(elem, GEN_CUSTOM_TAG, Custom) ,
            pattern = get_sub_text(elem, GEN_PATTERN_TAG),
            description = get_sub_text(elem, GEN_DESCRIPTION_TAG),
            name = elem.get('name', ''),
            prefix = elem.get('prefix', ''),
            shorten = elem.get('shorten', ''),
            type = elem.get('type', '')
        )

################################################################################################
    
GeneratorPolicy = list[Generator]
POLICY_BASE_TAG = 'generator_policy'
XML_SPACE = '\t'

def load_policy(file_name: str) -> GeneratorPolicy:
    """Load a list of Generators from an XML file."""
    root = ET.parse(file_name)
    return [Generator.from_xml(child) for child in root.findall(f'{GEN_BASETAG}')]

def save_policy(file_name: str, policy: GeneratorPolicy,**kw):
    """Save a list of Generators to an XML file."""
    encoding = kw.get('encoding', 'utf-8')
    root = ET.Element(POLICY_BASE_TAG)
    for generator in policy:
        generator.to_xml(ET.SubElement(root, GEN_BASETAG))
    ET.indent(root, space=XML_SPACE)
    ET.ElementTree(root).write(file_name, encoding=encoding, xml_declaration=True)