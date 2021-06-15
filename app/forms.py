from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from app.utils import validate_annotation
    
class BaseForm(FlaskForm):
    user_id = HiddenField('User ID', validators=[DataRequired()])
    submit = SubmitField('Next >>')

class InitialScriptForm(BaseForm):
    understand = BooleanField('I have read and understand', validators=[DataRequired()])
       
class AnnotationForm(BaseForm):
    image_id = HiddenField('Image ID', validators=[DataRequired()])
    annotation1 = TextAreaField('Generate a question about this image', validators=[DataRequired(), validate_annotation], render_kw={'cols': '100'})
    annotation2 = TextAreaField('Generate a question about this image', validators=[DataRequired(), validate_annotation], render_kw={'cols': '100'})
    annotation3 = TextAreaField('Generate a question about this image', validators=[DataRequired(), validate_annotation], render_kw={'cols': '100'})

class PostSurvey(BaseForm):
    vision_q = RadioField(choices=[(True, 'I was able to see the images well enough to generate questions'), (False, 'My vision was impaired and I was not able to see the images well enough to generate questions')], validators=[DataRequired()])
    post_q1 = BooleanField('They must be answerable from content in the image')
    post_q2 = BooleanField('They must not be answerable from content in the image')
    post_q3 = BooleanField('They must contain different languages')
    post_q4 = BooleanField('They must be funny')
    post_q5 = BooleanField('They must be varied')