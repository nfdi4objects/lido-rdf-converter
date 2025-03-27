import rdflib
import json
import sys

''' Read RDF file and return graph '''


def graphFromFile(file_path):
    graph = rdflib.Graph()
    graph.namespace_manager.bind('crm', rdflib.URIRef('http://www.cidoc-crm.org/cidoc-crm/'))
    graph.namespace_manager.bind('skos', rdflib.URIRef('http://www.w3.org/2004/02/skos/core#'))
    graph.parse(file_path)
    return graph


''' Get all namespaces from the graph '''


def namespaces2dict(graph):
    return {k: v for k, v in graph.namespaces() if not k.isdigit()}


''' Class to store entity information '''


class QNameInfo():
    def __init__(self, qname):
        if qname.startswith('http'):  # Handle URLs
            self.entity = qname
            self.prefix = ''
        else:
            vx = qname.split(':')  # Handle qnames
            if len(vx) == 2:
                self.prefix, self.entity = vx
            else:
                self.prefix, self.entity = '', vx[-1]

    def __lt__(self, other):
        return self.entity < other.entity

    def __hash__(self):
        return hash(self.entity)

    def __str__(self):
        return f'{self.prefix}:{self.entity}'


''' Get all entity and property names from the graph '''


def getQNameInfos(graph, **kw):
    entities = set()
    properties = set()
    rdfProperty = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
    rdfClass = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
    predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    # Get all classes and properties
    for subject, object in graph.subject_objects(predicate):
        info = QNameInfo(graph.qname(subject))
        if object == rdfProperty:
            properties.add(info)
        elif object == rdfClass:
            entities.add(info)
    # Return the compiled data
    def sortedDictList(aList): return [x.__dict__ for x in sorted(aList)]
    return {
        'source': kw.get('source', ''),
        'namespaces': namespaces2dict(graph),
        'classes': sortedDictList(entities),
        'properties': sortedDictList(properties)
    }


if __name__ == "__main__":
    file_path = 'CIDOC_CRM_v7.1.1.rdf'
    args = sys.argv[1:]
    if len(args) > 0:
        file_path = args[0]
        graph = graphFromFile(file_path)
        data = getQNameInfos(graph, source=file_path)
        print(json.dumps(data, indent=3))
    else:
        appName = sys.argv[0]
        print(f'Usage: python {appName} <rdf_file>')
        print(f'Example: python {appName} CIDOC_CRM_v7.1.1.rdf')
        sys.exit(1)
