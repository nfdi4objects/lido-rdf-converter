import os
from flask import Flask, redirect
from waitress import serve
from lidoapp_bp.lidoapp_bp import lidoapp_bp, init
import argparse

app = Flask(__name__)

app.config['SECRET_KEY'] = '110662'
app.config['UPLOAD_FOLDER'] = os.path.abspath('./work')
init(app.config['UPLOAD_FOLDER'])

app.register_blueprint(lidoapp_bp, url_prefix='/lidoapp_bp')

@app.route('/')
def index():
    print('app/')
    return redirect('/lidoapp_bp/')

if __name__ == '__main__': 
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=argparse.BooleanOptionalAction, help="Use WSGI server")
    parser.add_argument('-p', '--port', type=int, default=5000, help="Server port")
    args = parser.parse_args()
    opts = {"port": args.port}
  
    if args.wsgi:
        serve(app, host="0.0.0.0", **opts)
    else:
        app.run(host="0.0.0.0", **opts)
