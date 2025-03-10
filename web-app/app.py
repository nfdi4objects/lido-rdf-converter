import os
from flask import Flask, redirect
from waitress import serve
from lidoapp_bp.lidoapp_bp import registerLidoBlueprint
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

import argparse

db_file = Path('.') / 'lido_conv.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' +str(db_file.absolute())
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy()
db.init_app(app)

class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(64), unique=True, index=True)
   lido = db.Column(db.UnicodeText,index=True)
   x3ml = db.Column(db.UnicodeText,index=True)
   def __repr__(self):
      return '<User %r>' % self.username

app.app_context().push()

if not db_file.exists():
    db.create_all()

if users := User.query.all():
    user0 = users[0]
else:
    f = Path('./defaultLido.xml')
    lido = f.read_text() if f.exists() else ''
    f = Path('./defaultMapping.x3ml')
    x3ml = f.read_text() if f.exists() else ''
    user0 = User(id=1,username='master', lido=lido,x3ml=x3ml)
    print('initial new user added')
    db.session.add(user0)
    db.session.commit()

app.user = user0
lidoBp = registerLidoBlueprint(app)

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
