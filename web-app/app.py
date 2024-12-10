import os
from io import BytesIO
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from x3ml_classes import loadX3ml, storeX3ml, Namespace
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './work'
ALLOWED_EXTENSIONS = {'x3ml'}


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
    return next((x for x in localModel.namespaces if hasPrefix(x)),None)

def getNSdata(id):
    ns = localModel.namespaces[id]
    return { 'id': id, 'title':f"{ns.getAttr('prefix')}",'content':f"{ns.getAttr('uri')}"}

app = Flask(__name__)
app.config['SECRET_KEY'] = '110662'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
localModel = loadX3ml()

@app.route('/')
def index():
    return render_template('index.html', data=localModel)


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
                localModel.namespaces.append(ns)
            return redirect(url_for('index'))

    return render_template('createNS.html')

@app.route('/<int:id>/editNS', methods=('GET', 'POST'))
def editNS(id):
    ns = localModel.namespaces[id]

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
    localModel.namespaces.pop(id)
    flash(f"Namespace '{id+1}' was successfully deleted!")
    return redirect(url_for('index'))

@app.route('/<int:id>/deleteMapping', methods=('POST',))
def deleteMapping(id):
    localModel.mappings.pop(id)
    flash(f"Mapping '{id+1}' was successfully deleted!")
    return redirect(url_for('index'))

@app.route('/<int:id>/editMapping', methods=('GET', 'POST'))
def editMapping(id):
    m = localModel.mappings[id]
    if request.method == 'POST':
        rf = lambda s : request.form[s] 
        m.domain.sourceNode.text =rf('domainS') 
        m.domain.targetNode.entity.value =  rf('domainT')
        for i,l in enumerate(m.links):
            l.path.sourceRelation.relation = rf(f'relationP#{i}')
            l.path.targetRelation.relationship.value = rf(f'relationURI#{i}')
            l.range.targetNode.entity.value = rf(f'targetURI#{i}')
        return redirect(url_for('index'))
    return render_template('editMapping.html', mapping=m, id=id)

@app.route('/download')
def download():
    global localModel
    storePath = localFile('download.x3ml')
    storeX3ml(localModel,storePath)
    return send_file(storePath,  download_name='mapping.x3ml')

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    global localModel
    if request.method == 'POST':
        if 'default' in request.form:
            localModel = loadX3ml()
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
            localModel = loadX3ml(store)
            return redirect(url_for('index'))
    return render_template('loadFile.html')


if __name__ == '__main__': 
    app.run(host="localhost", port=8000)
