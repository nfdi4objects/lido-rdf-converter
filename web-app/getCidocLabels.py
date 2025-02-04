import rdflib, json,sys

from urllib.parse import urlparse



def read_rdf_file(file_path):
    g = rdflib.Graph()
    g.parse(file_path)
    return g

def split_url(url):
    parts = urlparse(str(url))
    vs = parts.path.split('/')
    return parts.scheme+'://'+parts.netloc+'/'.join(vs[0:-1]),vs[-1]

def findEntities(graph):
    classNames = set()
    propNames = set()
    isProp =rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
    tP = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    isClass = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
    path = None
    for tS,tO in graph.subject_objects(tP):
        fullPath,entity = split_url(tS)
        if not path:
            path = fullPath
        if tO == isProp:
            propNames.add(entity)
        elif tO == isClass:
            classNames.add(entity)
    data = {}
    if path:
        data['path'] = path
    if classNames:
        data['classes'] = [x for x in sorted(classNames)]
    if propNames:
        data['properties'] = [x for x in sorted(propNames)]
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
        print('Usage: python getCidocLabels.py <rdf_file>')
        print('Example: python getCidocLabels.py CIDOC_CRM_v7.1.1.rdf')
        sys.exit(1)