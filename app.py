import xml.etree.ElementTree as ET
import libs.LidoRDFConverter as LRC
from pathlib import Path
from libs.x3ml_classes import X3ml
from libs.x3ml import load_lido_map
from flask import Flask, render_template, request,  jsonify, make_response
import logging
import json
from dataclasses import dataclass

from waitress import serve
from argparse import ArgumentParser, BooleanOptionalAction

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/assets')


def dlftMappingFile():
    return Path('./defaultMapping.x3ml')


def dlftLidoFile():
    return Path('./defaultLido.xml')


def convert_lido_str(lido_str, x3ml_str,**kw):
    '''Converts LIDO XML string to RDF using the provided X3ML mapping string.
    Returns the RDF string in the specified format.'''
    if lido_str:
        format = kw.get('format','turtle')
        converter = LRC.LidoRDFConverter.from_str(x3ml_str, **kw)
        graph = converter.parse_string(lido_str)
        return graph.serialize(format=format)
    return ''

#############################################################################


@app.route('/')
def index():
    return render_template('index.html', version=app.config['version'].value)


@app.route('/version')
def version():
    return jsonify(app.config['version'])


@app.route('/barriere')
def barriere():
    return render_template('barriere.html')


@app.route('/json_to_x3ml', methods=['POST'])
def json_to_x3ml():
    parm = request.get_json()
    if js := parm.get('x3ml'):
        model = X3ml.fromJSON(js)
        x3ml_str = model.to_str()
        return jsonify({'status': 'success', 'x3ml': x3ml_str})
    return jsonify({'status': 'failed', 'message': 'No mapping data provided!'})


def x3mlstr_to_resonse(x3ml_str):
    if x3ml_str:
        response_object = {'status': 'success'}
        model = X3ml.from_serial(ET.XML(x3ml_str))
        response_object['jsonX3ml'] = json.dumps(model.toJSON(), indent=2)
        return jsonify(response_object)
    return jsonify({'status': 'failed', 'message': 'No mapping data provided!'})


@app.route('/default_x3ml', methods=['GET'])
def x3ml():
    x3ml_str = dlftMappingFile().read_text()
    return x3mlstr_to_resonse(x3ml_str)


@app.route('/default_lido', methods=['GET'])
def default_lido():
    answer = {'status': 'success', 'lidoData': dlftLidoFile().read_text()}
    return jsonify(answer)


@app.route('/upload_mapping', methods=['POST'])
def upload_mapping():
    parm = request.get_json()
    if data := parm['data']:
        return x3mlstr_to_resonse(data)
    return jsonify({'status': 'failed', 'message': 'No mapping data provided!'})


@app.route('/run_mappings', methods=['POST'])
def run_mappings():
    response_object = {'status': 'success'}
    parm = request.get_json()
    lido_data = parm.get('data','')
    if js := parm.get('x3ml'):
        model = X3ml.fromJSON(js)
        format = parm.get('format','turtle')
        useBlankNode = parm.get('useBlankNode',True)
        response_object = {'status': 'success', 'message': 'Mappings applied to Lido!', 'format':format}
        response_object['text'] = convert_lido_str(lido_data, model.to_str(),format=format, useBlankNode = useBlankNode)
        return jsonify(response_object)
    return jsonify({'status': 'failed', 'message': 'No Lido data provided!'})


@app.route('/convert', methods=['POST'])
def convert():
    # TODO: catch error and provide better error response e.g. code 400 for malformed LIDO
    # Valid formats: "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "json-ld", "hext"
    # Example: curl -X POST -F file=@my_lido_file.xml -F mapping=@my_mapping_file.x3ml -F format='nt' -F blankNode='true' HOST:PORT/convert
    if request.mimetype == "multipart/form-data":
        if 'file' not in request.files:
            return jsonify({'error': "No LIDO file part in the request."}), 400
        if 'mapping' in request.files:
            mapping_data = request.files['mapping'].read().decode('utf-8')
        else:
            mapping_data = dlftMappingFile().read_text()
        lido_data = request.files['file'].read().decode('utf-8')
        format = request.form.get('format', 'turtle')
        useBlankNode = request.form.get('blankNode', 'false').lower() == 'true'
    else:
        mapping_data = dlftMappingFile().read_text()
        lido_data = request.get_data()
        format = 'turtle'
        useBlankNode = False
    try:
        rdf_str = convert_lido_str(lido_data, mapping_data, format=format, useBlankNode = useBlankNode)
        response = make_response(rdf_str, 200)
        response.mime_type = f"text/{format}"
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return response


@dataclass
class Version():
    date: str = ''
    commit: str = ''
    value: str = '???'

    def update(self, tokens:list):
        ''' Updates attributes from tokens '''
        data = {'date': tokens[0], 'commit': tokens[1], 'value': tokens[2]}
        self.__dict__.update(data)
        return self

    @classmethod
    def from_tokens(cls, tokens):
        ''' Creates an object from tokens '''
        if len(tokens) == 3:
            return cls().update(tokens)
        return cls()


def get_version_data():
    ''' Reads version data from file into the app configuration'''
    tokens = []
    ver_file = Path('./version.txt')
    if ver_file.exists():
        # Get last line and split it into 3 tokens
        text = ver_file.read_text()
        last_line = text.splitlines()[-1]
        tokens = last_line.split(':', 3)
    app.config['version'] = Version.from_tokens(tokens)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=BooleanOptionalAction, help="Use WSGI server")
    parser.add_argument('-p', '--port', type=int, default=5000, help="Server port")
    parser.add_argument('-l', '--log', action=BooleanOptionalAction, help="Use logger")
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(filename='app.log', level=logging.INFO)

    get_version_data()
    load_lido_map() 

    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=args.port)
    else:
        app.run(host="0.0.0.0", port=args.port)
