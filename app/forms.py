from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AnnotationForm(FlaskForm):
    username = HiddenField('Username', validators=[DataRequired()], default="{{ username }}")
    image_id = HiddenField('Image ID', validators=[DataRequired()], default="{{ image_id }}")
    image_annotation_id = HiddenField('Image Annotation Count', validators=[DataRequired()], default="{{ image_annotation_id }}")
    annotation = TextAreaField('Generate a question about this image', validators=[DataRequired()], render_kw={'cols': '100'})
    submit = SubmitField('Submit')
    