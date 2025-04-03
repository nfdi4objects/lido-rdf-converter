from app import db

class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(64), unique=True, index=True)
   lido = db.Column(db.UnicodeText,index=True)
   x3ml = db.Column(db.UnicodeText,index=True)
   def __repr__(self):
      return '<User %r>' % self.username
