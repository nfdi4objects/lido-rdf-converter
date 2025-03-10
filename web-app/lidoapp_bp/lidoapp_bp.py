import sys
import copy
import io
sys.path.insert(0, '..')
import xml.etree.ElementTree as ET
import LidoRDFConverter as LRC
from pathlib import Path
from .x3ml_classes import Mapping, Link, PredicateVariant, Equals, X3ml
from flask import Blueprint, render_template, request, send_file, jsonify, current_app


def x3mlToStr(x3ml):
    elem = x3ml.serialize(ET.Element('root'))
    return ET.tostring(elem)


def dlftMappingFile(): return Path('./defaultMapping.x3ml')
def dlftLidoFile(): return Path('./defaultLido.xml')


def processString(lidoString, x3mlstr):
    result = '<no-data/>'
    if lidoString:
        converter = LRC.LidoRDFConverter.from_str(x3mlstr)
        graph = converter.parse_string(lidoString)
        result = graph.serialize(format='turtle')
    return result


lidoapp_bp = Blueprint('lidoapp_bp', __name__,  template_folder='templates', static_folder='')
lidoapp_bp.x3ml = X3ml()


def registerLidoBlueprint(app):
    global lidoapp_bp
    app.register_blueprint(lidoapp_bp, url_prefix=f'/{lidoapp_bp.name}')
    lidoapp_bp.x3ml = X3ml.from_serial(ET.XML(app.user.x3ml))
    return lidoapp_bp

#############################################################################


@lidoapp_bp.route('/')
def index():
    return render_template('index.html', url_prefix=f'/{lidoapp_bp.name}')


@lidoapp_bp.route('/downloadX3ml')
def downloadX3ml():
    global lidoapp_bp
    buffer = io.BytesIO()
    buffer.write(lidoapp_bp.x3ml.to_str())
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, mimetype="application/xml", download_name='mapping.x3ml')


@lidoapp_bp.route('/x3ml', methods=['GET', 'POST'])
def x3ml():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        try:
            parm = request.get_json()
            mapping = lidoapp_bp.x3ml.mappings[int(parm['mIndex'])]
            match parm['type']:
                case 'mapping':
                    mapping['skip'] = parm['skip']
                    mapping.domain.set(parm['path'], parm['entity'])
                case 'link':
                    link = mapping.links[int(parm['lIndex'])]
                    link['skip'] = parm['skip']
                    link.set(parm['path'], parm['relationship'], parm['entity'])
            response_object['message'] = 'Map changes applied!'
        except Exception as e:
            response_object['message'] = f'error {e}'
    else:
        response_object['jsonX3ml'] = lidoapp_bp.x3ml.toJSON()
    return jsonify(response_object)


@lidoapp_bp.route('/uploadMapping', methods=['GET', 'POST'])
def uploadMapping():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        if data := parm['data']:
            current_app.user.x3ml = data
        else:
            current_app.user.x3ml = dlftMappingFile().read_text()
        lidoapp_bp.x3ml = X3ml.from_serial(ET.XML(current_app.user.x3ml))
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)


@lidoapp_bp.route('/runMappings', methods=['GET', 'POST'])
def runMappings():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        current_app.user.lido = parm['data']
        response_object['text'] = processString(current_app.user.lido, lidoapp_bp.x3ml.to_str())
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)

@lidoapp_bp.route('/updateLido', methods=['GET', 'POST'])
def updateLido():
    global lidoapp_bp
    response_object = {'status': 'success'}
    print('update lido')
    if request.method == 'POST':
        parm = request.get_json()
        current_app.user.lido = parm['data']
    return jsonify(response_object)


@lidoapp_bp.route('/clearMappings', methods=['GET', 'POST'])
def clearMappings():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        lidoapp_bp.x3ml.mappings = []
        response_object['message'] = 'Mappings deleted!'
    return jsonify(response_object)


@lidoapp_bp.route('/addMap', methods=['GET', 'POST'])
def addMap():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        newMapping = Mapping()
        if len(lidoapp_bp.x3ml.mappings):
            newMapping.domain = copy.deepcopy(lidoapp_bp.x3ml.mappings[0].domain)
        else:
            newMapping.domain.sourceNode.text = '//lido:lido'
        lidoapp_bp.x3ml.mappings.insert(0, newMapping)
        response_object['message'] = 'Map changes applied!'
    return jsonify(response_object)


@lidoapp_bp.route('/addLink', methods=['GET', 'POST'])
def addLink():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        # Find mapping and add a new link (a copy of the first if exists)
        parm = request.get_json()
        mapping = lidoapp_bp.x3ml.mappings[int(parm['mIndex'])]
        newLink = Link()
        if len(mapping.links):
            newLink.path = copy.deepcopy(mapping.links[0].path)
        mapping.links.insert(0, newLink)
        response_object['message'] = 'Map changes applied!'
    return jsonify(response_object)


@lidoapp_bp.route('/deleteMap/<int:mapId>', methods=['DELETE'])
def deleteMap(mapId):
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'DELETE':
        lidoapp_bp.x3ml.mappings.pop(mapId)
        response_object['message'] = 'Map removed!'
    return jsonify(response_object)


@lidoapp_bp.route('/deleteLink/<int:mapId>/<int:linkId>', methods=['DELETE'])
def deleteLink(mapId, linkId):
    global lidoapp_bp
    answer = {'status': 'success'}
    if request.method == 'DELETE':
        lidoapp_bp.x3ml.mappings[mapId].links.pop(linkId)
        answer['message'] = 'Link removed!'
    return jsonify(answer)


@lidoapp_bp.route('/applyCondition', methods=['POST'])
def applyCondition():
    response_object = {'status': 'success'}
    parm = request.get_json()
    mode = parm['mode']  # 'link' or 'map'
    mapping = lidoapp_bp.x3ml.mappings[int(parm['mIndex'])]
    def createEquals(x): return PredicateVariant.from_op(Equals.byValues(x['xpath'], x['value']))
    if mode == 'link':
        link = mapping.links[int(parm['lIndex'])]
        predicates = [createEquals(x['predicate']) for x in parm['predicates']]
        link.path.targetRelation.condition.op.predicates = predicates
        response_object['message'] = 'Conditions applied!'
    elif mode == 'map':
        predicates = [createEquals(x['predicate']) for x in parm['predicates']]
        mapping.domain.targetNode.condition.op.predicates = predicates
        response_object['message'] = 'Conditions applied!'
    return jsonify(response_object)


@lidoapp_bp.route('/loadLido/<int:mode>')
def loadLido(mode):
    if mode == 1:#Reset
        current_app.user.lido = dlftLidoFile().read_text()
    answer = {'status': 'success', 'lidoData': current_app.user.lido}
    return jsonify(answer)
