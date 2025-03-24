import re
import time
import urllib.request as ulr
import urllib.parse as ulp
import x3ml as x3ml
from lxml import etree
import rdflib as RF
import os
import shutil
from io import BytesIO

# General used namespaces
CRM = RF.Namespace("http://www.cidoc-crm.org/cidoc-crm/")
N4O = RF.Namespace('http://graph.nfdi4objects.net/id/')
LIDO_TAG = f'{{{x3ml.lidoSchemaURI}}}lido'
RESUMPTION_TAG = f'{{{x3ml.oaiSchemaURL}}}resumptionToken'


def make_erm_uri(uri_str):
    '''Returns URI' like e.g. crm:Enn_cccc'''
    right_token = uri_str.split(':')[-1]
    return CRM[right_token]


def deep_get(nested_dict, keys):
    if not keys or nested_dict is None:
        return nested_dict
    return deep_get(nested_dict.get(keys[0]), keys[1:])


def is_uri(uri_str):
    return ulp.urlparse(uri_str).scheme.startswith('http')


def safe_uri(uri_str):
    if is_uri(uri_str):
        return ulp.quote(uri_str).replace('%3A', ':')
    return uri_str


def create_oai_request(server_uri: str, command: str) -> ulr.Request | None:
    """Primary function for requesting OAI-PMH data from repository,
       checking for errors, handling possible compression and returning
       the XML string to the rest of the script for writing to a file."""

    request_str = server_uri + f'?verb={command}'
    headers = {'User-Agent': 'pyoaiharvester/3.0', 'Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
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
            return create_oai_request(server_uri, command)
        return None


def request_to_buffer(req: ulr.Request) -> str:
    '''Write request response in a file'''
    with ulr.urlopen(req) as response:
        buffer = BytesIO()
        buffer.write(response.read())
        buffer.seek(0)
        return buffer


def make_result_graph():
    graph = RF.Graph()
    graph.bind("crm", CRM)
    graph.bind("n4o", N4O)
    return graph


def make_clean_subdir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)


class LidoRDFConverter():
    def __init__(self, file_path):
        self.mappings = x3ml.getMapping(file_path) if file_path else []

    @classmethod
    def from_str(cls, mapping_str):
        obj = cls('')
        obj.mappings = x3ml.getMappingS(mapping_str)
        return obj

    def process_url(self, url: str, **kw):
        rdf_folder = kw.get('rdf_folder', 'data')
        make_clean_subdir(rdf_folder)

        def serialize(g, t):
            file = f'./{rdf_folder}/{t}.ttl'
            g.serialize(destination=file, format='ttl')

        '''Transfers all LIDO elements'''
        headers = {'User-Agent': 'pyoaiharvester/3.0', 'Accept': 'text/html', 'Accept-Encoding': 'compress, deflate'}
        request = ulr.Request(url, headers=headers)
        if url.startswith('http'):
            request = create_oai_request(url, f'ListRecords&metadataPrefix=lido')
            while request:
                buffer = request_to_buffer(request)
                graph, rs_token = self.parse_file(buffer, processor=serialize)
                if not rs_token:
                    print('No more resumptionToken')
                    break
                request = create_oai_request(url, f"ListRecords&resumptionToken={rs_token}")
        else:
            with ulr.urlopen(request) as response:
                graph, _ = self.parse_file(response)
                return graph

    def parse_file(self, lido_file, **kw):
        graph = make_result_graph()
        processor = kw.get('processor')
        valid_tag = (LIDO_TAG, RESUMPTION_TAG, 'error')
        token = None
        for _, elem in etree.iterparse(
                lido_file, events=("end",),
                tag=valid_tag, encoding='UTF-8', remove_blank_text=True):
            token = self._process_valid_element(graph, elem)
        if processor:
            processor(graph, token)
        return graph, token

    def parse_string(self, lido_str):
        graph = make_result_graph()
        valid_tag = (LIDO_TAG)
        parser = etree.XMLPullParser(events=("end",), tag=valid_tag, encoding='UTF-8', remove_blank_text=True)
        parser.feed(lido_str)
        for _, elem in parser.read_events():
            self._process_lido_element(elem, graph)
        return graph

    def _process_valid_element(self, graph, elem):
        token = None
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

    def _process_lido_element(self, elem, graph):
        '''Create graph LIDO root element w.r.t given mappings'''
        rec_id = ' '.join(x3ml.lidoXPath(elem, "./lido:lidoRecID/text()"))
        for data in [m.getData(elem) for m in self.mappings]:
            for i, elem_data in enumerate(data):
                if elem_data.get('valid'):
                    add_spo(graph, elem_data, index=i, rec_id=rec_id)


def hash(s):
    return x3ml.md5Hash(s)


__url_regex = re.compile(r"https?:")
def __strip_schema(url): return __url_regex.sub('', url).strip().strip('/')


def make_item(text, specify, use_id=False):
    if is_uri(text) and not use_id:
        return RF.term.URIRef(text)
    return N4O[f"{hash(__strip_schema(text)+specify)}"]  # No URI for ID => local ID from path and recID


def add_spo(graph, elem_data, **kw):
    rec_id = kw.get('rec_id', '')
    entity_S = deep_get(elem_data, ['S', 'entity'])
    id_S = safe_uri(deep_get(elem_data, ['info', 'id']))
    S = make_item(id_S, rec_id, use_id=True)
    triples = [(S, RF.RDF.type, make_erm_uri(entity_S))]
    for po in deep_get(elem_data, ['PO']):
        po_triples = []
        if po.get('isValid'):
            entity_P = deep_get(po, ['P', 'entity'])
            entity_O = deep_get(po, ['O', 'entity'])
            for po_data in po.get('data'):
                if text := po_data.get('text'):
                    if not is_uri(text):
                        po_triples.append((S, make_erm_uri('P90_has_value'), RF.Literal(text)))
                    else:
                        text = safe_uri(text)
                        is_uri_id = is_uri(text) and entity_O == "crm:E42_Identifier"
                        id_O = po_data.get('id')
                        if id_S != id_O:
                            P = make_erm_uri(entity_P)
                            if is_uri(id_O) or is_uri_id:
                                O = RF.term.URIRef(text)
                                po_triples.append((S, P, O))
                            else:
                                O = make_item(id_O, rec_id)
                                po_triples.append((O, RF.RDF.type, make_erm_uri(entity_O)))
                                po_triples.append((O, make_erm_uri('P90_has_value'), RF.Literal(text)))
                                po_triples.append((S, P, O))
        if po_triples:
            triples += po_triples
    for triple in triples:
        graph.add(triple)
