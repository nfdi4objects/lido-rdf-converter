import re
import time
import x3ml
import os
import shutil
import rdflib as RF
import urllib.request as ulr
import urllib.parse as ulp
from io import BytesIO
from lxml import etree


# prefix namespace mapping
NAMESPACE_MAP = {
    "n4o": RF.Namespace('http://graph.nfdi4objects.net/id/'),
    "crm": RF.Namespace("http://www.cidoc-crm.org/cidoc-crm/"),
    "geosparql": RF.Namespace('http://www.ontotext.com/plugins/geosparql#')
}
LIDO_TAG = x3ml.expand_with_namespaces('lido:lido')
OAI_SCHEMA_URL = 'http://www.openarchives.org/OAI/2.0/'
RESUMPTION_TAG = f'{{{OAI_SCHEMA_URL}}}resumptionToken'


def make_short_uri(uri_str, **kw) -> RF.term.URIRef:
    '''Returns URI' like e.g. crm:Enn_cccc'''
    # tag = kw.get('tag',None)
    for k, v in NAMESPACE_MAP.items():
        if uri_str.startswith(f"{k}:"):
            return v[uri_str.split(':')[-1]]
    return RF.term.URIRef(uri_str)


def isHttp(url) -> bool:
    """Checks if a string is a valid HTTP URL."""
    return re.match(r"^https?:", url) is not None


def proper_uri(uri: str | None) -> str | None:
    """Returns a proper URI string, replacing spaces with underscores and encoding special characters."""
    if uri:
        uri_t = uri.strip()
        if isHttp(uri_t):
            return ulp.quote(uri_t).replace('%3A', ':')
        return uri_t


def oai_request(server_uri: str, command: str) -> ulr.Request | None:
    """Primary function for requesting OAI-PMH data from repository,
       checking for errors, handling possible compression and returning
       the XML string to the rest of the script for writing to a file."""

    request_str = server_uri + f'?verb={command}'
    headers = {'User-Agent': 'pyoaiharvester/3.0',
               'Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
    try:
        return ulr.Request(request_str, headers=headers)
    except ulr.HTTPError as ex_value:
        print('Http Error:', ex_value)
        if ex_value.code == 503:
            retry_wait = int(ex_value.hdrs.get("Retry-After", "-1"))
            if retry_wait < 0:
                return None
            print(f'Waiting {retry_wait} seconds')
            time.sleep(retry_wait)
            return oai_request(server_uri, command)
        return None


def read_request(req: ulr.Request) -> str:
    '''Write request response in a buffer file'''
    with ulr.urlopen(req) as response:
        temp_filename = 'oai.buffer.xml'
        with open(temp_filename, 'w') as out_file:
            out_file.write(response.read().decode('utf-8'))
        return temp_filename


def make_result_graph() -> RF.Graph:
    '''Creates an RDF graph with bound namespaces'''
    graph = RF.Graph()
    for k, v in NAMESPACE_MAP.items():
        graph.bind(k, v)
    return graph


def make_clean_subdir(dir_path):
    '''Creates a clean subdirectory for storing RDF files'''
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)


def hash(s:str):
    '''Returns a hash of the string s'''
    return x3ml.md5Hash(s)


def strip_schema(url: str) -> str:
    """Strips the schema from a URL"""
    return re.sub(r"^https?:", '', url).strip().strip('/')


def make_n4o_id(text: str, **kw) -> str:
    """Creates a N4O ID from text and specify"""
    return NAMESPACE_MAP['n4o'][f"{hash(text)}"]


#def pd(*args): print([json.dumps(x, indent=2) for x in args])


def add_triples(graph, mapping: x3ml.Mapping, recID: str, **kw) -> None:
    '''Add triples to the graph'''
    info = mapping.info
    if id_S := info.id.strip():
        id_S = recID + '-' + id_S
        S = make_n4o_id(id_S, tag='S')
        all_triples = []
        all_triples.append(
            (S, RF.RDF.type, make_short_uri(mapping.S.entity, tag='S')))
        # all_triples.append((S,make_short_uri('crm:P999'), RF.Literal(id_S)))
        num_S_triples = len(all_triples)
        for po in mapping.POs:
            all_triples.extend(get_po_triples(S, recID,  po, **kw))
        if len(all_triples) > num_S_triples:
            for t in all_triples:
                graph.add(t)


def get_po_triples(S, recID, po: x3ml.PO, **kw) -> list:
    '''Compile triples from PO data'''
    triples = []
    if po.valid:
        P = make_short_uri(po.P.entity, tag='P')
        for info in po.infos:
            if info.mode == 'lidoID' or info.mode == 'path':
                id_O = recID + '-' + info.id.strip()
                O = make_n4o_id(id_O, tag='O')
                if (O != S):
                    triples.append(
                        (O, RF.RDF.type, make_short_uri(po.O.entity, tag='O')))
                    # triples.append((O, make_short_uri('crm:P90_has_value'), RF.Literal(info.id.strip(), lang=info.lang)))
                    triples.append((S, P, O))
            else:
                if text := info.text:
                    O = RF.Literal(text.strip(), lang=info.lang)
                    triples.append((S, P, O))
    return triples


def updateNS(elem)-> None:
    '''Updates the supported namespaces from the XML element (only one update)'''
    if x3ml.not_none(elem):
        if not hasattr(updateNS, "first"):
            x3ml.used_namespaces.update(get_ns(elem) )
            updateNS.first = True

def get_ns(elem):
    '''Returns the save namespace map from an XML element'''
    return dict(filter(lambda item: item[0], elem.nsmap.items()))

class LidoRDFConverter():
    '''Converts LIDO XML files to RDF graphs using X3ML mappings'''
    def __init__(self, file_path):
        self.mappings = x3ml.Mappings.from_file(file_path)
        
    Graph = RF.Graph

    @classmethod
    def from_str(cls, mapping_str):
        obj = cls('')
        obj.mappings = x3ml.Mappings.from_str(mapping_str)
        return obj

    def process_url(self, url: str, **kw)-> Graph:
        if url.endswith('.xml'):
            '''Fetches and parses a single LIDO XML file from a URL'''
            headers = {'Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
            request = ulr.Request(url, headers=headers)
            with ulr.urlopen(request) as response:
                graph, _ = self.parse_file(response)
                return graph
        else:
            '''Fetches and processes LIDO records from an OAI-PMH endpoint'''
            rdf_folder = kw.get('rdf_folder', 'data')
            suffix = kw.get('suffix', 'ttl')

            make_clean_subdir(rdf_folder)

            def serialize(graph, token):
                file = f'./{rdf_folder}/{token}.{suffix}'
                graph.serialize(destination=file, format=suffix, encoding='utf-8')
                
            request = oai_request( url, 'ListRecords&metadataPrefix=lido')
            while request:
                buffer_file = read_request(request)
                graph, rs_token = self.parse_file(buffer_file)
                serialize(graph, rs_token)
                if not rs_token:
                    break
                request = oai_request(url, f"ListRecords&resumptionToken={rs_token}")

    def parse_file(self, lido_file) -> tuple[RF.Graph, str]:
        '''Parses a LIDO file and returns the RDF graph and a resumption token'''
        graph = make_result_graph()
        valid_tag = (LIDO_TAG, RESUMPTION_TAG, 'error')
        next_token = ''
        for _, elem in etree.iterparse(lido_file, events=("end",),  tag=valid_tag, encoding='UTF-8', remove_blank_text=True):
            updateNS(elem)
            next_token = self._process_valid_element(graph, elem)
        return graph, next_token

    def parse_string(self, lido_str) -> RF.Graph:
        '''Parses a LIDO string and returns the RDF graph'''
        parser = etree.XMLPullParser(events=("end",), tag=(LIDO_TAG), encoding='UTF-8', remove_blank_text=True)
        parser.feed(lido_str)
        graph = make_result_graph()
        for _, elem in parser.read_events():
            self._process_lido_element(elem, graph)
        return graph

    def _process_valid_element(self, graph, elem)-> str:
        '''Process valid LIDO or resumptionToken elements'''
        token = ''
        if RESUMPTION_TAG == elem.tag:
            token = elem.text
            print('completeListSize', elem.attrib['completeListSize'])
            print('cursor', elem.attrib['cursor'])
            print('expirationDate', elem.attrib['expirationDate'])
            print('token', token)
        elif 'error' in elem.tag:
            print('error', elem.tag, elem.text)
        elif elem.tag == LIDO_TAG:
            self._process_lido_element(elem, graph)
        else:
            print('unexpeced :-(')
            elem.clear()
        return token

    def _process_lido_element(self, elem, graph) -> None:
        '''Create graph LIDO root element w.r.t given mappings'''
        recIDs = x3ml.xpath_lido(elem, "./lido:lidoRecID/text()")
        recID = ' '.join([x.strip() for x in recIDs])
        for data in [m.evaluate(elem) for m in self.mappings]:
            for i, elem_data in enumerate(data):
                if elem_data.valid:
                    add_triples(graph, elem_data, recID, index=i)
