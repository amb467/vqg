import re, logging
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, StopValidation
from app import db
from app.models import User, Annotation

logger = logging.getLogger('vqg')

def validate_annotation(form, field):
    
    user_id = form.user_id.data
    
    annotation_orig = field.data
    annotation = lcase_and_remove_whitespace(annotation_orig)
    
    # First make sure that this annotation does not match other annotations on the form
    other_annotations_orig = [form.annotation1.data, form.annotation2.data, form.annotation3.data]
    other_annotations = set([lcase_and_remove_whitespace(item) for item in other_annotations_orig])
    other_annotations.remove(annotation)
    
    if not len(other_annotations) == 2:
        validation_err(user_id, field, 'The three annotations for this image are not unique', f'{other_annotations_orig} - {len(other_annotations)}')
    
    # Now make sure that this annotation does not match other previously submitted annotations
    u = User.query.get(user_id)
    
    if u:
        other_annotations = u.annotations
        logger.info(f'User {user_id}: Other annotations are {other_annotations}')
    else:
        validation_err(user_id, field, 'When validating annotations, could not find this user in the database')
    
    
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
    vision_q = RadioField(choices=['I was able to see the images well enough to generate questions', 'My vision was impaired and I was not able to see the images well enough to generate questions'], validators=[DataRequired()])
    post_q1 = BooleanField('They must be answerable from content in the image')
    post_q2 = BooleanField('They must not be answerable from content in the image')
    post_q3 = BooleanField('They must contain different languages')
    post_q4 = BooleanField('They must be funny')
    post_q5 = BooleanField('They must be varied')
    
def lcase_and_remove_whitespace(s):
    s = re.findall("[a-z]+", s.lower())
    return "".join(s)

def validation_err(user_id, field, validation_msg, supp_logging_msg=""):
    logger.error(f'User {user_id}: {validation_msg}; {supp_logging_msg}')
    field.errors += (ValidationError(validation_msg),)
    StopValidation()
    