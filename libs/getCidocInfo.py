import rdflib
import json
import sys

''' Read RDF file and return graph '''


def createGraph():
    graph = rdflib.Graph()
    graph.namespace_manager.bind('crm', rdflib.URIRef(
        'http://www.cidoc-crm.org/cidoc-crm/'))
    graph.namespace_manager.bind('skos', rdflib.URIRef(
        'http://www.w3.org/2004/02/skos/core#'))
    graph.namespace_manager.bind('rdf', rdflib.URIRef(
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    return graph


''' Get all namespaces from the graph '''


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
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return f'{self.prefix}:{self.entity}'


''' Get all entity and property names from the graph '''


def readGraph(graph, properties,classes,namespaces):
    '''Read properties,classes and namespaces from graph'''
    _PROPERTY = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
    _CLASS = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
    _PREDICATE = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    
    # Get all classes and properties
    for subject, object in graph.subject_objects(_PREDICATE):
        info = QNameInfo(graph.qname(subject))
        if object == _PROPERTY:
            properties.add(info)
        elif object == _CLASS:
            classes.add(info)
    # Get all namespaces
    for k, v in graph.namespaces():
        if not k.isdigit():
           namespaces.update({k: v})

ADDITIONAL_CLASSES = ['skos:Concept','skos:ConceptScheme']
ADDITIONAL_PROPS = ['geo:hasGeometry','skos:inScheme']

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        namespaces = {}
        classes = set()
        properties = set()
        sources = []

        for file in args:
            graph = createGraph()
            graph.parse(file)
            readGraph(graph, properties, classes, namespaces)
            sources.append(file)
            
        for item in ADDITIONAL_CLASSES: classes.add(QNameInfo(item))
        for item in ADDITIONAL_PROPS: properties.add(QNameInfo(item))
            
        dict_list = lambda l:[x.__dict__ for x in sorted(l)] # sorted list of dict's
        json_data = {'sources': sources, 'namespaces': namespaces, 'classes': dict_list(classes), 'properties':  dict_list(properties) }
        print(json.dumps(json_data, indent=3))
    else:
        appName = sys.argv[0]
        print(f'Usage: python {appName} <rdf_file>')
        print(f'Example: python {appName} CIDOC_CRM_v7.1.3.rdf')
        sys.exit(1)
