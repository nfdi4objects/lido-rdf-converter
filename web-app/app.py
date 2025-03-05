import os
from flask import Flask, redirect
from waitress import serve
from lidoapp_bp.lidoapp_bp import registerLidoBlueprint
import argparse

app = Flask(__name__)

lidoBp = registerLidoBlueprint(app, os.path.abspath('./work'))

@app.route('/')
def index():
    return redirect(f'/{lidoBp.name}/')

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
