import copy
import io
import xml.etree.ElementTree as ET
import LidoRDFConverter as LRC
from pathlib import Path
from .x3ml_classes import Mapping, Link, PredicateVariant, Equals, X3ml
from flask import Blueprint, render_template, request, send_file, jsonify, make_response
from .database import db, User


class LidoBP(Blueprint):
    def __init__(self,user=None):
        super().__init__('LidoBP', __name__,  template_folder='templates', static_folder='static', static_url_path='/assets')
        self.model = X3ml()
        self.user = user

lidoapp_bp = LidoBP()


def dlftMappingFile(): 
    return Path('./defaultMapping.x3ml')


def dlftLidoFile(): 
    return Path('./defaultLido.xml')


def processString(lidoString, x3mlstr):
    result = '<no-data/>'
    if lidoString:
        converter = LRC.LidoRDFConverter.from_str(x3mlstr)
        graph = converter.parse_string(lidoString)
        result = graph.serialize(format='turtle')
    return result


def registerLidoBlueprint(app,user):
    global lidoapp_bp
    app.register_blueprint(lidoapp_bp)
    lidoapp_bp.model = X3ml.from_serial(ET.XML(user.x3ml))
    lidoapp_bp.user = user
    return lidoapp_bp

def fileContent(fileName):
    file = Path(fileName)
    return file.read_text() if file.exists() else ''

def createLido2RdfService(app):
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
        lido = fileContent('./defaultLido.xml')
        x3ml = fileContent('./defaultMapping.x3ml')
        firstUser = User(id=1,username='master', lido=lido,x3ml=x3ml)
        print('initial new user added', firstUser)
        db.session.add(firstUser)
        db.session.commit()

    # Bind all parts
    return registerLidoBlueprint(app,firstUser)


#############################################################################

@lidoapp_bp.route('/', methods=["GET","POST"])
def index():
    return render_template('index.html')


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


@lidoapp_bp.route('/convert', methods=['POST'])
def convert():
    global lidoapp_bp
    lidoapp_bp.user.lido = request.get_data()
    # TODO: catch error and provide better error response e.g. code 400 for malformed LIDO
    turtle = processString(lidoapp_bp.user.lido, lidoapp_bp.model.to_str()) 
    response = make_response(turtle, 200)
    response.mime_type = "text/turtle"
    return response


@lidoapp_bp.route('/convert', methods=['POST'])
def convert():
    if storage_file := request.files['file']:
        lido_str =  storage_file.read().decode('utf-8')
        return processString(lido_str, dlftMappingFile().read_text())
    return f'<no-data/>'


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
            newMapping.domain = copy.deepcopy(lidoapp_bp.model.mappings[0].domain)
        else:
            newMapping.domain.sourceNode.text = '//lido:lido'
        lidoapp_bp.model.mappings.insert(0, newMapping)
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
            newLink.path = copy.deepcopy(mapping.links[0].path)
        mapping.links.insert(0, newLink)
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
