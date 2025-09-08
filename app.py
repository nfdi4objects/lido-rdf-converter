from flask import Flask, redirect
from waitress import serve
from lidoapp_bp.lidoapp_bp import createLido2RdfService
from argparse import ArgumentParser, BooleanOptionalAction

app = Flask(__name__)
l2rService = createLido2RdfService(app)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-w', '--wsgi', action=BooleanOptionalAction, help="Use WSGI server")
    parser.add_argument('-p', '--port', type=int,
                        default=5000, help="Server port")
    args = parser.parse_args()

    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=args.port)
    else:
        app.run(host="0.0.0.0", port=args.port)
