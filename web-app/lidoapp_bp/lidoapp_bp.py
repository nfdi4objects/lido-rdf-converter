import sys, os, copy
sys.path.insert(0, '..')
from flask import Blueprint, render_template, request, send_file, jsonify
from .x3ml_classes import loadX3ml, storeX3ml, Mapping, Link, PredicateVariant, Equals
from pathlib import Path
import LidoRDFConverter as LRC

WORKFOLDER = './work'

def dlftMappingFile(): return './defaultMapping.x3ml'
def dlftLidoFile(): return './defaultLido.xml'
def workMappingFile(): return WORKFOLDER+'/mapping.x3ml'
def workLidoFile(): return WORKFOLDER+'/lido.xml'

def makeWorkspace():
    Path(WORKFOLDER).mkdir(exist_ok=True)
    mFile = Path(workMappingFile())
    if not mFile.exists():
        mFile.write_text(Path(dlftMappingFile()).read_text())
    sFile = Path(workLidoFile())
    if not sFile.exists():
        sFile.write_text(Path(dlftLidoFile()).read_text())

def initWorkspace(dirName):
    global WORKFOLDER
    try:
        if not os.path.exists(dirName):
            print('create folder ',dirName)
            os.mkdir(dirName)
        WORKFOLDER = dirName   
        makeWorkspace()
    except OSError as error:
        print(error)  

def processString(lidoString,mapingFile=workMappingFile()):
    fmt = 'turtle'
    result = '<no-data/>'
    lidoFile = workLidoFile()
    if Path(lidoFile).write_text(lidoString) > 0:
        converter = LRC.LidoRDFConverter(mapingFile)
        graph,_ = converter.processXML(lidoFile)
        result = graph.serialize(format=fmt)
    return result

lidoapp_bp = Blueprint('lidoapp_bp', __name__,  template_folder='templates', static_folder='')
workX3ml = loadX3ml()

def registerLidoApp(app, path):
    initWorkspace( path)
    app.register_blueprint(lidoapp_bp, url_prefix=f'/lidoapp_bp')
    return lidoapp_bp

#############################################################################

@lidoapp_bp.route('/')
def index():
    return render_template('index.html', url_prefix=f'/{lidoapp_bp.name}')

@lidoapp_bp.route('/downloadX3ml')
def downloadX3ml():
    global workX3ml
    storePath = Path(WORKFOLDER+'/download.x3ml')
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
            fileName = Path(workMappingFile()).write_text(data)
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


@lidoapp_bp.route('/loadLido')
def loadDftlLido():
    data = Path('./defaultLido.xml').read_text()
    answer = {'status': 'success','lidoData':data}
    return jsonify(answer)