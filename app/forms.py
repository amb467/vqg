#import wtforms.validators
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, RadioField, StringField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
#from wtforms.validators import DataRequired
from wtforms import validators
from app.utils import validate_annotation

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

"""
    def process_data(self, value):
        try:
            self.data = list(self.coerce(v) for v in value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(x) for x in valuelist)
        except ValueError:
            raise ValueError(self.gettext('Invalid choice(s): one or more data inputs could not be coerced'))

    def pre_validate(self, form):
        if self.data:
            values = list(c[0] for c in self.choices)
            for d in self.data:
                if d not in values:
                    raise ValueError(self.gettext("'%(value)s' is not a valid choice for this field") % dict(value=d))
"""       
class BaseForm(FlaskForm):
    user_id = HiddenField('User ID', validators=[validators.DataRequired()])
    submit = SubmitField('Next >>')

class InitialScriptForm(BaseForm):
    understand = BooleanField('I have read and understand', validators=[validators.DataRequired()])
       
class AnnotationForm(BaseForm):
    image_id = HiddenField('Image ID', validators=[validators.DataRequired()])
    annotation1 = TextAreaField('Q1: ', validators=[validators.DataRequired(), validate_annotation], render_kw={'cols': '100'})
    annotation2 = TextAreaField('Q2: ', validators=[validators.DataRequired(), validate_annotation], render_kw={'cols': '100'})
    #annotation3 = TextAreaField('Q3: ', validators=[DataRequired(), validate_annotation], render_kw={'cols': '100'})

class PostSurvey(BaseForm):
    vision_q = RadioField(choices=[("True", 'I was able to see the images well enough to generate questions'), ("False", 'My vision was impaired and I was not able to see the images well enough to generate questions')], validators=[validators.DataRequired()])
    race_q = MultiCheckboxField('Which of the following best describes you?  Please select all that apply:',
                               choices=[('a', 'Asian or Pacific Islander'),
                                        ('b', 'Black or African American'), 
                                        ('h', 'Hispanic or Latino'),
                                        ('n', 'Native American or Alaskan Native'),
                                        ('w', 'White or Caucasian'),
                                        ('m', 'Multiracial or Biracial'),
                                        ('other', 'Let me type:'),
                                        ('r', 'I\'d rather not say')],
                               validators=[validators.DataRequired()])
    race_q_other = StringField('', [validators.optional(), validators.length(max=48)])
    gender_q = MultiCheckboxField('Which of the following best describes you?  Please select all that apply:',
                               choices=[('n', 'Non-Binary'),
                                        ('f', 'Female'), 
                                        ('m', 'Male'),
                                        ('t', 'Transgender'),
                                        ('i', 'Intersex'),
                                        ('other', 'Let me type:'),
                                        ('r', 'I\'d rather not say')],
                               validators=[validators.DataRequired()])
                                                              
    gender_q_other = StringField('', [validators.optional(), validators.length(max=48)])
    attention_check = RadioField(choices=[("False", 'They must be answerable from content in the image'), ("True", 'They must not be answerable from content in the image')], validators=[validators.DataRequired()])
    #post_q1 = BooleanField('They must be answerable from content in the image')
    #post_q2 = BooleanField('They must not be answerable from content in the image')
    #post_q3 = BooleanField('They must contain different languages')
    #post_q4 = BooleanField('They must be funny')
    #post_q5 = BooleanField('They must be varied')