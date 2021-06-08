from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(64))
    ethnicity = db.Column(db.String(64))
    education = db.Column(db.String(64))
    attn_check = db.Column(db.String(12))

    def __repr__(self):
        return '<User {}>'.format(self.username)  

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(500))

    def __repr__(self):
        return '<Image {}>'.format(self.id)    
    
    	           
class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q_num = db.Column(db.Integer)
    q_content = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), index=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        return '<Annotation {}>'.format(self.q_content)