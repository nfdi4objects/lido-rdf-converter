import os
from flask import Blueprint, render_template, request, send_file, jsonify,current_app
from .x3ml_classes import loadX3ml, storeX3ml, Namespace, Mapping,Link, PredicateVariant, Equals
from .lidoEditor import makeWorkspace, processString,workMappingFile
import copy


lidoapp_bp = Blueprint('lidoapp_bp', __name__,  template_folder='templates', static_folder='')

mapper = makeWorkspace()

def init(fd):
    print(lidoapp_bp.name)
    try:
        if not os.path.exists(fd):
            print('create folder ',fd)
            os.mkdir(fd)
    except OSError as error:
        print(error)  

def localFile(s):
    folder = current_app.config['UPLOAD_FOLDER']
    return os.path.join(folder, s)

def findNS(prefix) -> Namespace|None:
    hasPrefix = lambda x : x.prefix()==prefix
    return next((x for x in workX3ml.namespaces if hasPrefix(x)),None)

def getNSdata(id):
    ns = workX3ml.namespaces[id]
    return { 'id': id, 'title':f"{ns['prefix']}",'content':f"{ns['uri']}"}


workX3ml = loadX3ml()

#############################################################################

@lidoapp_bp.route('/')
def index():
    return render_template('index.html', url_prefix=f'/{lidoapp_bp.name}')

@lidoapp_bp.route('/downloadX3ml')
def downloadX3ml():
    global workX3ml
    storePath = localFile('download.x3ml')
    storeX3ml(workX3ml,storePath)
    return send_file(storePath,  download_name='mapping.x3ml')

@lidoapp_bp.route('/x3ml', methods=['GET', 'POST'])
def x3ml():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        try:
            parm = request.get_json()
            mapping = workX3ml.mappings[int(parm['mIndex'])]
            match parm['type']:
                case 'mapping':
                    mapping['skip'] = parm['skip']
                    mapping.domain.set(parm['path'], parm['entity'])
                case 'link':
                    link = mapping.links[int(parm['lIndex'])]
                    link['skip'] = parm['skip']
                    link.set(parm['path'],parm['relationship'], parm['entity'])
            response_object['message'] = 'Map changes applied!'
        except Exception as e:
             response_object['message'] = f'error {e}'
    else:
        response_object['jsonX3ml'] = workX3ml.toJSON()
    return jsonify(response_object)

@lidoapp_bp.route('/uploadMapping', methods=['GET', 'POST'])
def uploadMapping():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        if data := parm['data']:
            fileName = toFile(workMappingFile(),data)
            workX3ml = loadX3ml(fileName)
        else:
            workX3ml = loadX3ml() #use default mapping
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)

@lidoapp_bp.route('/runMappings', methods=['GET', 'POST'])
def runMappings():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        wmf = storeX3ml(workX3ml,workMappingFile())
        response_object['text'] = processString(parm['data'],wmf)
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)

@lidoapp_bp.route('/clearMappings', methods=['GET', 'POST'])
def clearMappings():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        workX3ml.mappings = []
        response_object['message'] = 'Mappings deleted!'
    return jsonify(response_object)

@lidoapp_bp.route('/addMap', methods=['GET', 'POST'])
def addMap():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        newMapping = Mapping()
        if len(workX3ml.mappings):
            newMapping.domain =copy.deepcopy(workX3ml.mappings[0].domain)
        else:
            newMapping.domain.sourceNode.text = '//lido:lido'
        workX3ml.mappings.insert(0,newMapping)
        response_object['message'] = 'Map changes applied!'
    return jsonify(response_object)

@lidoapp_bp.route('/addLink', methods=['GET', 'POST'])
def addLink():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        #print(parm)
        m = workX3ml.mappings[int(parm['mIndex'])]
        newLink = Link()
        if len(m.links):
            newLink.path =copy.deepcopy(m.links[0].path)
        m.links.insert(0,newLink)
        response_object['message'] = 'Map changes applied!'
    return jsonify(response_object)


@lidoapp_bp.route('/deleteMap/<int:mapId>', methods=['DELETE'])
def deleteMap(mapId):
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'DELETE':
        workX3ml.mappings.pop(mapId)
        response_object['message'] = 'Map removed!'
    return jsonify(response_object)

@lidoapp_bp.route('/deleteLink/<int:mapId>/<int:linkId>', methods=['DELETE'])
def deleteLink(mapId,linkId):
    global workX3ml
    answer = {'status': 'success'}
    if request.method == 'DELETE':
        workX3ml.mappings[mapId].links.pop(linkId)
        answer['message'] = 'Link removed!'
    return jsonify(answer)

@lidoapp_bp.route('/applyCondition',methods=['POST'])
def applyCondition():
    response_object = {'status': 'success'}
    parm = request.get_json()
    mode =parm['mode'] # 'link' or 'map'
    mapping = workX3ml.mappings[int(parm['mIndex'])]
    createEquals = lambda x: PredicateVariant.from_op(Equals.byValues(x['xpath'],x['value']))
    if mode =='link':
        link = mapping.links[int(parm['lIndex'])]
        predicates = [ createEquals(x['predicate']) for x in parm['predicates']]
        link.path.targetRelation.condition.op.predicates = predicates
        response_object['message'] = 'Conditions applied!'
    elif mode =='map':
        predicates = [ createEquals(x['predicate']) for x in parm['predicates']]
        mapping.domain.targetNode.condition.op.predicates = predicates
        response_object['message'] = 'Conditions applied!'
    return jsonify(response_object)

def fromFile(fname):
    with open(fname,'r') as fid:
        return fid.read()
    return ''

def toFile(fname,data):
    if data:
        with open(fname,'w') as fid:
            fid.write(data)
            return fname

@lidoapp_bp.route('/loadLido')
def loadDftlLido():
    data = fromFile('./defaultLido.xml')
    answer = {'status': 'success','lidoData':data}
    return jsonify(answer)