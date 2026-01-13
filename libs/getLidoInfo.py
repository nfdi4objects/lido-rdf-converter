import sys
import json
from lxml import etree


namespaces = {'xs': 'http://www.w3.org/2001/XMLSchema'}


def processElement(elem, f=None):
    if f:
        if name := elem.get('name'):
            f(f'lido:{name}')
        elif ref := elem.get('ref'):
            f(f'{ref}')


def processCT(elem, f=None):
    for x in elem.findall('xs:sequence/xs:element', namespaces):
        processElement(x, f)


def process(root, f):
    for elem in root.findall('xs:element', namespaces):
        processElement(elem, f)
    for elem in root.findall('xs:complexType', namespaces):
        processCT(elem, f)


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        tree = etree.parse(args[1])
        result = set()
        process(tree.getroot(), lambda x: result.add(x))
        w = {'source': args[1], 'pathes': sorted(result)}
        print(json.dumps(w, indent=3))
    else:
        appName = sys.argv[0]
        print(f'Usage: python {appName} <xml_file>')
        print(f'Example: python {appName} lido-schema/lido-v1.1.xsd')
        sys.exit(1)
