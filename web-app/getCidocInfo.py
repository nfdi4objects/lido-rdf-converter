import rdflib, json,sys

from urllib.parse import urlparse


NAMESPACES = [{'crm': 'http://www.cidoc-crm.org/cidoc-crm/'},
              {'skos': 'http://www.w3.org/2004/02/skos/core#'},]

def get_prefixes(graph):
    prefixes = {}
    for ns in NAMESPACES:
        for k,v in ns.items():
            prefixes[k] = v
    for prefix, uri in graph.namespaces():
        prefixes[prefix] = uri
    return prefixes

def prefix(qname,prefixes):
    for k,v in prefixes.items():
        if qname.startswith(v):
            return qname.replace(v,k+':')
    return qname

def read_rdf_file(file_path):
    g = rdflib.Graph()
    g.parse(file_path)
    return g

def splitQname(qname):
    if qname.startswith('http'):    
        enitity=qname
        ns = ''
    else:
        vx = qname.split(':')
        if len(vx) == 2:
            ns,enitity = vx
        else:
            ns,enitity = '',vx[-1]
    return enitity,ns

class Info():
    def __init__(self,entity,prefix=''):
        self.entity = entity
        self.prefix = prefix

    def __lt__(self, other):
        return self.entity < other.entity
    
    def __hash__(self):
        return hash(self.entity)


def findEntities(graph):
    classNames = set()
    propNames = set()
    isProp =rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
    tP = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    isClass = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
    prefixes = get_prefixes(graph)
    for tS,tO in graph.subject_objects(tP):
        qname = prefix(tS,prefixes) 
        entity, ns = splitQname(qname)
        info = Info(entity,ns)
        if tO == isProp:
            propNames.add(info)
        elif tO == isClass:
            classNames.add(info)
    data = {}
    data['namespaces'] = prefixes
    if classNames:
        data['classes'] = [x.__dict__ for x in sorted(classNames)]
    if propNames:
        data['properties'] = [x.__dict__ for x in sorted(propNames)]
    return data

  
if __name__ == "__main__":
    file_path = 'CIDOC_CRM_v7.1.1.rdf'
    args = sys.argv[1:]
    if len(args) > 0:
        file_path = args[0]
        graph = read_rdf_file(file_path)
        data = findEntities(graph)
        data['source'] = file_path
        print(json.dumps(data, indent=3))
    else:
        appName = sys.argv[0]
        print(f'Usage: python {appName} <rdf_file>')
        print(f'Example: python {appName} CIDOC_CRM_v7.1.1.rdf')
        sys.exit(1)