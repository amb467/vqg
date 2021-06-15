from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer)
    session_id = db.Column(db.Integer)
    progress = db.Column(db.Integer, default=0)
    attn_check = db.Column(db.String(12))
    vision_check = db.Column(db.String(8))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    current_image_id = db.Column(db.Integer, db.ForeignKey('image.id')) 
    annotations = db.relationship('Annotation', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.id)  

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_set = db.Column(db.String(5), index=True)
    img_url = db.Column(db.String(256))

    def __repr__(self):
        return '<Image {}>'.format(self.id)    
    
                   
class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q_num = db.Column(db.Integer)
    q_content = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), index=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        return '<Annotation {}>'.format(self.q_content)