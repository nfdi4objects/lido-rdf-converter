import sys
sys.path.insert(0, '..')
import os
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, jsonify
from x3ml_classes import loadX3ml, storeX3ml, Namespace, Mapping,Link
from lidoEditor import makeWorkspace, processString,workMappingFile
import copy

UPLOAD_FOLDER = './work'
ALLOWED_EXTENSIONS = {'x3ml'}
mapper = makeWorkspace()

try:
    if not os.path.exists(UPLOAD_FOLDER):
        print('create folder ',UPLOAD_FOLDER)
        os.mkdir(UPLOAD_FOLDER)
except OSError as error:
    print(error)  

def allowed_file(filename):
    ext = os.path.splitext(filename)[-1].lower().strip('.')
    return ext in ALLOWED_EXTENSIONS

def localFile(s):
    return os.path.join(app.config['UPLOAD_FOLDER'], s)

def findNS(prefix) -> Namespace|None:
    hasPrefix = lambda x : x.prefix()==prefix
    return next((x for x in workX3ml.namespaces if hasPrefix(x)),None)

def getNSdata(id):
    ns = workX3ml.namespaces[id]
    return { 'id': id, 'title':f"{ns.getAttr('prefix')}",'content':f"{ns.getAttr('uri')}"}

app = Flask(__name__)

app.config['SECRET_KEY'] = '110662'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

workX3ml = loadX3ml()

@app.route('/downloadX3ml')
def downloadX3ml():
    global workX3ml
    storePath = localFile('download.x3ml')
    storeX3ml(workX3ml,storePath)
    return send_file(storePath,  download_name='mapping.x3ml')

#############################################################################

@app.route('/')
def index():
    return render_template('index.html', data=mapper)

@app.route('/x3ml', methods=['GET', 'POST'])
def x3ml():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        try:
            parm = request.get_json()
            mapping = workX3ml.mappings[int(parm['mIndex'])]
            match parm['type']:
                case 'mapping':
                    mapping.domain.set(parm['path'], parm['entity'])
                case 'link':
                    link = mapping.links[int(parm['lIndex'])]
                    link.set(parm['path'],parm['relationship'], parm['entity'])
            response_object['message'] = 'Map changes applied!'
        except Exception as e:
             response_object['message'] = f'error {e}'
    else:
        print(workX3ml.mappings[0].domain.sourceNode.text)
        response_object['jsonX3ml'] = workX3ml.toJSON()
    return jsonify(response_object)

@app.route('/uploadMapping', methods=['GET', 'POST'])
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

@app.route('/runMappings', methods=['GET', 'POST'])
def runMappings():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        wmf = storeX3ml(workX3ml,workMappingFile())
        response_object['text'] = processString(parm['data'],wmf)
        response_object['message'] = 'Mappings applied to Lido!'
    return jsonify(response_object)

@app.route('/addMap', methods=['GET', 'POST'])
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

@app.route('/addLink', methods=['GET', 'POST'])
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


@app.route('/deleteMap/<int:mapId>', methods=['DELETE'])
def deleteMap(mapId):
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'DELETE':
        print(f'delete map {mapId}')
        workX3ml.mappings.pop(mapId)
        response_object['message'] = 'Map removed!'
    return jsonify(response_object)

@app.route('/deleteLink/<int:mapId>/<int:linkId>', methods=['DELETE'])
def deleteLink(mapId,linkId):
    global workX3ml
    answer = {'status': 'success'}
    if request.method == 'DELETE':
        print(f'delete link {linkId} of map {mapId}')
        workX3ml.mappings[mapId].links.pop(linkId)
        answer['message'] = 'Link removed!'
    return jsonify(answer)

def fromFile(fname):
    with open(fname,'r') as fid:
        return fid.read()
    return ''

def toFile(fname,data):
    if data:
        with open(fname,'w') as fid:
            fid.write(data)
            return fname

@app.route('/loadLido')
def loadDftlLido():
    data = fromFile('./defaultLido.xml')
    answer = {'status': 'success','lidoData':data}
    return jsonify(answer)


if __name__ == '__main__': 
   
    app.run(host="localhost", port=8000)
