from flask import Flask, redirect
from waitress import serve
from lidoapp_bp.lidoapp_bp import createLido2RdfService
import argparse as AP

app = Flask(__name__)
l2rService = createLido2RdfService(app)

if __name__ == '__main__':
    parser = AP.ArgumentParser()
    parser.add_argument(
        '-w', '--wsgi', action=AP.BooleanOptionalAction, help="Use WSGI server")
    parser.add_argument('-p', '--port', type=int,
                        default=5000, help="Server port")
    args = parser.parse_args()
    opts = {"port": args.port}

    if args.wsgi:
        serve(app, host="0.0.0.0", **opts)
    else:
        app.run(host="0.0.0.0", **opts)
