import sys
from lxml import etree


NS = {'path':'http://www.w3.org/2001/XMLSchema','label':'lido'}

class NameInfo():
    def __init__(self, prefix,entity):
        self.prefix = prefix
        self.entity = entity

    def __hash__(self):
        return hash(self.entity)

    def __str__(self):
        lbl = NS.get('label')
        return f'{lbl}:{self.entity}'


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        file_path = args[0]
        xs = NS.get('path')
        valid_tag = (f'{{{xs}}}element')
        names = set()
        for _, elem in etree.iterparse(file_path, events=("end",),tag=valid_tag, encoding='UTF-8', remove_blank_text=True):
            if name := elem.get('name'):
                names.add(name)
        infos = (NameInfo(xs,name) for name in sorted(names))
        for x in  infos: print(x)
    else:
        appName = sys.argv[0]
        print(f'Usage: python {appName} <rdf_file>')
        print(f'Example: python {appName} CIDOC_CRM_v7.1.1.rdf')
        sys.exit(1)
