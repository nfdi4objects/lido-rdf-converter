import sys
sys.path.insert(0, '..')
import os
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, jsonify
from x3ml_classes import loadX3ml, storeX3ml, Namespace, Mapping,Link
from LidoRDFConverter import LidoRDFConverter
from lidoEditor import makeWorkspace
import copy

UPLOAD_FOLDER = './work'
ALLOWED_EXTENSIONS = {'x3ml'}
mapper =  makeWorkspace()

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
    return  os.path.join(app.config['UPLOAD_FOLDER'], s)

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

@app.route('/')
def index():
    return render_template('index.html', data=mapper)

@app.route('/download')
def download():
    global workX3ml
    storePath = localFile('download.x3ml')
    storeX3ml(workX3ml,storePath)
    return send_file(storePath,  download_name='mapping.x3ml')

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    global workX3ml
    if request.method == 'POST':
        if 'default' in request.form:
            workX3ml = loadX3ml()
            return redirect(url_for('index'))
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            store = localFile('upload.x3ml')
            file.save(store)
            workX3ml = loadX3ml(store)
            return redirect(url_for('index'))
    return render_template('loadFile.html')

#############################################################################

@app.route('/x3ml', methods=['GET', 'POST'])
def x3ml():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        if parm['type'] == 'mapping':
            print(parm)
            i = int(parm['mIndex'])
            d = workX3ml.mappings[i].domain
            d.apply(parm['path'], parm['entity'])
        if parm['type'] == 'link':
            print(parm)
            i = int(parm['mIndex'])
            j = int(parm['lIndex'])
            link = workX3ml.mappings[i].links[j]
            link.apply(parm['path'],parm['relationship'], parm['entity'])
            print(link.toJSON())
        response_object['message'] = 'Map changes applied!'
    else:
        print(f'#M={len(workX3ml.mappings)}')
        response_object['jsonX3ml'] = workX3ml.toJSON()
    return jsonify(response_object)

@app.route('/addMap', methods=['GET', 'POST'])
def addMap():
    global workX3ml
    response_object = {'status': 'success'}
    if request.method == 'POST':
        parm = request.get_json()
        print(parm)
        newMapping = Mapping()
        if len(workX3ml.mappings):
            newMapping.domain =copy.deepcopy(workX3ml.mappings[0].domain)
        else:
            newMapping.domain.sourceNode.text = '//lido:lido'
        workX3ml.mappings.insert(0,newMapping)
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
