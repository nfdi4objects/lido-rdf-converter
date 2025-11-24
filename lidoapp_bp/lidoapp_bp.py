import copy
import io
import xml.etree.ElementTree as ET
import LidoRDFConverter as LRC
from pathlib import Path
from .x3ml_classes import Mapping, Link, PredicateVariant, Equals, X3ml
from flask import Blueprint, render_template, request, send_file, jsonify, make_response
from .database import db, User
import logging


class LidoBP(Blueprint):
    def __init__(self,user=None):
        super().__init__('LidoBP', __name__,  template_folder='templates', static_folder='static', static_url_path='/assets')
        self.model = X3ml()
        self.user = user
        self.logger = logging.getLogger(__name__)
    
    def info(self,s):
        self.logger.info(s)


lidoapp_bp = LidoBP()

def index():
    return render_template('index.html')

def dlftMappingFile():
    return Path('./defaultMapping.x3ml')


def dlftLidoFile():
    return Path('./defaultLido.xml')


def convert_lido_str(lido_str, x3ml_str,format='turtle'):
    '''Converts LIDO XML string to RDF using the provided X3ML mapping string.
    Returns the RDF string in the specified format.'''
    if lido_str:
        converter = LRC.LidoRDFConverter.from_str(x3ml_str)
        graph = converter.parse_string(lido_str)
        return graph.serialize(format=format)
    return ''



def register_lido_bp(app,user, use_logger=True):
    '''Registers the Lido Blueprint with the Flask app and initializes it with the given user.'''
    global lidoapp_bp
    if use_logger:
        logging.basicConfig(filename='app.log', level=logging.INFO)
        lidoapp_bp.info('Started')
    
    lidoapp_bp.add_url_rule('/', methods=["GET","POST"], view_func=index)

    app.register_blueprint(lidoapp_bp)
    lidoapp_bp.model = X3ml.from_serial(ET.XML(user.x3ml))
    lidoapp_bp.user = user

    return lidoapp_bp

def file_content(fileName):
    '''Returns the content of a file as a string.'''
    with open(fileName,'r', encoding='utf-8') as file:
        return  file.read()
    return ''

def createLido2RdfService(app, use_logger=True):
    '''Creates and configures the Lido to RDF conversion service'''
    db_file = Path('.') / 'lido_conv.db'
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' +str(db_file.absolute())
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    db.init_app(app)
    app.app_context().push()

    if not db_file.exists():
        db.create_all()

    if users := User.query.all():
        firstUser = users[0]
        print('Recent first user',firstUser)
    else:
        # Create first user from default files
        lido = file_content('./defaultLido.xml')
        x3ml = file_content('./defaultMapping.x3ml')
        firstUser = User(id=1,username='master', lido=lido,x3ml=x3ml)
        print('initial new user added', firstUser)
        db.session.add(firstUser)
        db.session.commit()

    # Bind all parts
    return register_lido_bp(app,firstUser, use_logger=use_logger)


#############################################################################



@lidoapp_bp.route('/downloadX3ml')
def downloadX3ml():
    global lidoapp_bp
    buffer = io.BytesIO()
    buffer.write(lidoapp_bp.model.to_str())
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, mimetype="application/xml", download_name='mapping.x3ml')


@lidoapp_bp.route('/x3ml', methods=['GET', 'POST'])
def x3ml():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        try:
            parm = request.get_json()
            mapping = lidoapp_bp.model.mappings[int(parm['mIndex'])]
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
        response_object['jsonX3ml'] = lidoapp_bp.model.toJSON()
    return jsonify(response_object)


@lidoapp_bp.route('/uploadMapping', methods=['GET', 'POST'])
def uploadMapping():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        if data := parm['data']:
            lidoapp_bp.user.x3ml = data
        else:
            lidoapp_bp.user.x3ml = dlftMappingFile().read_text()
        db.session.commit()
        lidoapp_bp.model = X3ml.from_serial(ET.XML(lidoapp_bp.user.x3ml))
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)


@lidoapp_bp.route('/runMappings', methods=['GET', 'POST'])
def runMappings():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        lidoapp_bp.user.lido = parm['data']
        response_object['text'] = convert_lido_str(lidoapp_bp.user.lido, lidoapp_bp.model.to_str())
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)

@lidoapp_bp.route('/convert', methods=['POST'])
def convert():
    # TODO: catch error and provide better error response e.g. code 400 for malformed LIDO
    # Valid formats: "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "json-ld", "hext"
    # Example: curl -X POST -F file=@my_lido_file.xml -F mapping=@my_mapping_file.x3ml -F format='nt' HOST:PORT/convert
    if request.mimetype == "multipart/form-data":
        if 'file' not in request.files:
            return jsonify({'error': "No LIDO file part in the request."}), 400
        if 'mapping' in request.files:
            mapping_data = request.files['mapping'].read().decode('utf-8')
        else:
            mapping_data = dlftMappingFile().read_text()
        lido_data = request.files['file'].read().decode('utf-8')
        format = request.form.get('format','turtle')
    else:
        mapping_data = dlftMappingFile().read_text()
        lido_data = request.get_data()
        format ='turtle'
    try:
        rdf_str = convert_lido_str(lido_data, mapping_data,format=format)
        response = make_response(rdf_str, 200)
        response.mime_type = f"text/{format}"
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return response

@lidoapp_bp.route('/updateLido', methods=['GET', 'POST'])
def updateLido():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        lidoapp_bp.user.lido = parm['data']
        db.session.commit()
    return jsonify(response_object)


@lidoapp_bp.route('/clearMappings', methods=['GET', 'POST'])
def clearMappings():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        lidoapp_bp.model.mappings = []
        response_object['message'] = 'Mappings deleted!'
    return jsonify(response_object)


@lidoapp_bp.route('/addMap', methods=['GET', 'POST'])
def addMap():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        newMapping = Mapping()
        if len(lidoapp_bp.model.mappings):
            newMapping.domain = copy.deepcopy(lidoapp_bp.model.mappings[-1].domain)
        else:
            newMapping.domain.sourceNode.text = '//lido:lido'
        lidoapp_bp.model.mappings.append(newMapping)
        response_object['message'] = 'Map changes applied!'
    return jsonify(response_object)


@lidoapp_bp.route('/addLink', methods=['GET', 'POST'])
def addLink():
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'POST':
        # Find mapping and add a new link (a copy of the first if exists)
        parm = request.get_json()
        mapping = lidoapp_bp.model.mappings[int(parm['mIndex'])]
        newLink = Link()
        if len(mapping.links):
            newLink.path = copy.deepcopy(mapping.links[-1].path)
        mapping.links.append(newLink)
        response_object['message'] = 'Map changes applied!'
    return jsonify(response_object)


@lidoapp_bp.route('/deleteMap/<int:mapId>', methods=['DELETE'])
def deleteMap(mapId):
    global lidoapp_bp
    response_object = {'status': 'success'}
    if request.method == 'DELETE':
        lidoapp_bp.model.mappings.pop(mapId)
        response_object['message'] = 'Map removed!'
    return jsonify(response_object)


@lidoapp_bp.route('/deleteLink/<int:mapId>/<int:linkId>', methods=['DELETE'])
def deleteLink(mapId, linkId):
    global lidoapp_bp
    answer = {'status': 'success'}
    if request.method == 'DELETE':
        lidoapp_bp.model.mappings[mapId].links.pop(linkId)
        answer['message'] = 'Link removed!'
    return jsonify(answer)


@lidoapp_bp.route('/applyCondition', methods=['POST'])
def applyCondition():
    response_object = {'status': 'success'}
    parm = request.get_json()
    mode = parm['mode']  # 'link' or 'map'
    mapping = lidoapp_bp.model.mappings[int(parm['mIndex'])]
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
        lidoapp_bp.user.lido = dlftLidoFile().read_text()
    answer = {'status': 'success', 'lidoData': lidoapp_bp.user.lido}
    return jsonify(answer)
