import sys
sys.path.insert(0, '..')
import os
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, jsonify
from x3ml_classes import loadX3ml, storeX3ml, Namespace
from LidoRDFConverter import LidoRDFConverter
from lidoEditor import makeWorkspace
import json

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


@app.route('/createNS', methods=('GET', 'POST'))
def createNS():
    if request.method == 'POST':
        prefix = request.form['title']
        uri = request.form['content']
        if not prefix:
            flash('Prefix is required!')
        else:
            if not findNS(prefix):
                ns = Namespace().set(prefix,uri)
                workX3ml.namespaces.append(ns)
            return redirect(url_for('index'))

    return render_template('createNS.html')

@app.route('/<int:id>/editNS', methods=('GET', 'POST'))
def editNS(id):
    ns = workX3ml.namespaces[id]

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            ns.set(title,content)
            return redirect(url_for('index'))

    return render_template('editNS.html', ns=ns, id=id)

@app.route('/<int:id>/deleteNS', methods=('POST',))
def deleteNS(id):
    workX3ml.namespaces.pop(id)
    flash(f"Namespace '{id+1}' was successfully deleted!")
    return redirect(url_for('index'))

@app.route('/<int:id>/deleteMapping', methods=('POST',))
def deleteMapping(id):
    mapper.mappings.pop(id)
    flash(f"Mapping '{id+1}' was successfully deleted!")
    return redirect(url_for('index'))

@app.route('/<int:id>/editMapping', methods=('GET', 'POST'))
def editMapping(id):
    m = mapper.mappings[id]
    if request.method == 'POST':
        rf = lambda s : request.form[s] 
        m.S.path =rf('domainS') 
        m.S.entity =  rf('domainT')
        for i,l in enumerate(m.POs):
            l.P.path = rf(f'relationP#{i}')
            l.P.entity = rf(f'relationURI#{i}')
            l.O.entity = rf(f'targetURI#{i}')
    return render_template('editMapping.html', mapping=m, id=id)

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
        response_object['jsonX3ml'] = workX3ml.toJSON()
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

if __name__ == '__main__': 
   
    app.run(host="localhost", port=8000)
