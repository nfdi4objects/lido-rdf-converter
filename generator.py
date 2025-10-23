from dataclasses import dataclass, asdict,field
import xml.etree.ElementTree as ET

@dataclass
class Arg:
    name: str
    type: str=''

    def to_xml(self, root=ET.Element('set-arg')):
        """Serialize the dataclass to an XML string."""
        root.attrib['name'] = str(self.name)
        root.attrib['type'] = str(self.type)
        return root

    @classmethod
    def from_xml(cls, root):
        """Deserialize an XML string into a dataclass instance."""
        name = root.get('name','')
        type = root.get('type','')
        return cls(name=name, type=type)

    
@dataclass
class Custom:
    args: list = field(default_factory=list)
    class_name: str = ''

    def to_xml(self, root = ET.Element('custom')) -> str:
        root.attrib['generatorClass'] = self.class_name
        for x in self.args:
            x.to_xml(ET.SubElement(root, 'set-arg'))
        return root 

    def save_to_file(self, file_path: str):
        """Save the serialized XML to a file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(ET.tostring(self.to_xml(), encoding='unicode'))

    @classmethod
    def from_xml(cls, root):
        data = [Arg.from_xml(child) for child in root.findall('./set-arg') ]
        return cls(class_name=root.get('generatorClass',''), args=data)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load and deserialize XML data from a file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            xml_data = file.read()
        return cls.from_xml(ET.fromstring(xml_data))
    
