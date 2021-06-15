import os, logging, random, re
from app import db
from app.models import User, Image, Annotation
from datetime import datetime
from wtforms.validators import ValidationError, StopValidation

logger = logging.getLogger('vqg')

# The total number of steps of the task
def get_progress_completion():
    return int(os.environ.get('PROGRESS_COMPLETION'))

# A list of all image_ids that is used for image selection   
def get_image_ids():
	global IMAGE_IDS
    if IMAGE_IDS is None:
        IMAGE_IDS = [image.id for image in Image.query.all()]
    return IMAGE_IDS
    
##########
#
#   This function does several things:
#       1. Extract Prolific parameters from the request
#       2. Make sure that all parameters are included (return error message otherwise)
#       3. Check if a user with this Prolific ID exists in the database yet
#       4. If the user exists, validate that the study and session ids match, (return error message otherwise)
#       5. If the user doesn't exist, create the user
#       6. If everything has gone successfully to this point, return the user's progress
#
#   Return values:
#       user_id: the Prolific ID of the user
#       progress: the progress step that the user is on
#       err: an error message, if any
#
##########

def get_user_progress(request):
    arg_dict = dict([(arg_name, request.args.get(arg_name)) for arg_name in ['PROLIFIC_PID', 'STUDY_ID', 'SESSION_ID']])
    err = []
    
    # Make sure that the Prolific parameters are all present
    for arg_name, arg_val in arg_dict.items():
        if not arg_val:
            err.append(f'{arg_name} is required')
    
    # Now check if the user exists and if the study and session ids match up
    u = User.query.get(arg_dict['PROLIFIC_PID'])
    
    if u:
        if not u.study_id == int(arg_dict['STUDY_ID']):
            err.append(f"Study ID mismatch: found {u.study_id} in db but passed {arg_dict['STUDY_ID']}")

        if not u.session_id == int(arg_dict['SESSION_ID']):
            err.append(f"Session ID mismatch: found {u.session_id} in db but passed {arg_dict['SESSION_ID']}")        
    else:
        u = User(id=arg_dict['PROLIFIC_PID'], study_id=arg_dict['STUDY_ID'], session_id=arg_dict['SESSION_ID'])
        db.session.add(u)
        err_msg = _try_commit()
        if err_msg:
            err.append(err_msg)
        
    err = "" if len(err) == 0 else "; ".join(err)
    return arg_dict['PROLIFIC_PID'], u.progress, err

##########
#
#   Return the parameters to append to the redirect url
#
########## 
def get_url_params(request, progress=None):
    return _get_url_params(request.args.get('PROLIFIC_PID'), request.args.get('STUDY_ID'), request.args.get('SESSION_ID'), progress)

def _get_url_params(user_id, study_id, session_id, progress=None):
    args = f"?PROLIFIC_PID={user_id}&STUDY_ID={study_id}&SESSION_ID={session_id}"
    args = f"{args}&progress={progress}" if progress else args
    logger.info(f"User {user_id}: returning parameters {args}")
    return args
    
##########
#
#   Randomly select an image for the annotator to view
#
#   Return values:
#       image_id: The id of the image in the COCO data set
#       image_url: The url from which to load the image
#
##########   
def get_image(user_id):
    
    # Get a list of all images previously annotated by this user
    u = User.query.get(user_id)
    if not u:
        err_msg = f"User {user_id}: User doesn't exist (in utils.get_image)"
        logger.error(err_msg)
        return None, None, err_msg
            
    annotated_images = set([annotation.image_id for annotation in u.annotations])
    
    # Now randomly select images until we find one that the user has not yet annotated
    image_id = random.choice(get_image_ids())
    
    while image_id in annotated_images:
        image_id = random.choice(get_image_ids())     
    
    logger.info(f'User {user_id}: select image {image_id}')
    # Return the image information
    image = Image.query.get(image_id)
    return image.id, image.img_url, None

##########
#
#   Based on the progress step, determine what has to be validated and validate it
#
#   Return values:
#       err: if something went wrong, this is the error message indicating the problem
#
##########     
def validate_step(user_id, form):
    
    u = User.query.get(user_id)
    err = ""
    
    if not u:
        return "Invalid user"

    # User completed the process, either successfully (PROGRESS_COMPLETION) or unsuccessfully (-1)
    if u.progress == get_progress_completion() or u.progress == -1:
        return "User complete"
    
    # New user, advance if the user select "I understand"
    if u.progress == 0:
        if not form.understand:
            err = "User did not select 'I understand'"
    
    # User submitted post-survey, advance if the user answered questions correctly
    elif u.progress == get_progress_completion()  - 1:
        err = _validate_post_survey(user_id, form)
    
    # The user is annotating, record the annotations in the Annotations table.  There is
    # no validation step here - the validation already happened on the form.
    else:
        err = _record_annotations(user_id, form)
    
    if not err:
        u.progress = u.progress + 1
        logger.info(f'User {user_id}: Advancing progress to {u.progress}')
        err = _try_commit()
    
    return err

def _validate_post_survey(user_id, form):
    vision_q = form.vision_q.data
    post_qs = [form.post_q1.data, form.post_q2.data, form.post_q3.data, form.post_q4.data, form.post_q5.data,]
    
    logger.info(f'User {user_id}: Survey question answers: {vision_q}; {post_qs}')
    
    err = []
    
    """
    validate that vision_q = 'I was able to see the images well enough to generate questions'
    otherwise, add err = "You have been excluded from this study due to vision impairment.  This study requires vision in order to view images"
    
    validate that on post_qs, answers 0, 2 are not selected and 1,4 are selected
    otherwise, add err = "You answered the attention check question incorrectly.  You have been excluded from this study."
    
    either way, add the post-survey to the database
    
    u = User.query.get(user_id)
    
    if not u:
        return "Invalid user"
        
    u.attn_check = "-".join(post_qs)
    u.vision_check = vision_q
    u.end_time = datetime.utcnow()
    db.session.add(u)
    err.append(_try_commit())
    """  
      
    return ";".append(err)


##########
#
#   Record the annotations in the annotation table.
#
#   Return:
#       err: If something went wrong while committing this annotation to the database
#
########## 
def _record_annotations(user_id, form):
        a1 = Annotation(q_num=1, q_content=form.annotation1.data, image_id=form.image_id.data, user_id=user_id)
        a2 = Annotation(q_num=2, q_content=form.annotation2.data, image_id=form.image_id.data, user_id=user_id)
        a3 = Annotation(q_num=3, q_content=form.annotation3.data, image_id=form.image_id.data, user_id=user_id)
        
        db.session.add(a1)
        db.session.add(a2)
        db.session.add(a3)
        
        return _try_commit() 

##########
#
#   Try to commit changes to the database, log an error if it occurs
#
#   Return:
#       err_msg: None if the commit went fine, includes an error message if there was one
#
########## 
def _try_commit():
    try:
        db.session.commit()
        return None
    except Exception as err:
        return f"Error message received when committing database: {err}"

##########
#
#   Get the smallest positive integer that is not being used as a prolific id in the database
#
########## 
def get_unique_prolific_id():
    pid = 1
    u = User.query.get(pid)
    
    while u:
        pid += 1
        u = User.query.get(pid)
        
    return _get_url_params(pid, 444, 555)

##########
#
#   Validate that the annotation in the passed field of the passed form meets the following criteria:
#       1. When stripped of everything but alphanumeric characters, it is at least five characters long
#       2. The annotations on the form do not match each other (looking only at lowercased alphanumeric characters)
#       3. The annotation in this form field does not match any previously submitted annotations (looking only at lowercased alphanumeric characters)
#
########## 
def validate_annotation(form, field):
    
    user_id = form.user_id.data
    
    annotation_orig = field.data
    annotation = _lcase_and_remove_whitespace(annotation_orig)
    
    if len(annotation) < 5:
        _validation_err(user_id, field, f'The annotation is not a complete question (length {len(annotation)})') 
    
    # First make sure that this annotation does not match other annotations on the form
    other_annotations_orig = [form.annotation1.data, form.annotation2.data, form.annotation3.data]
    other_annotations = set([_lcase_and_remove_whitespace(item) for item in other_annotations_orig])
    other_annotations.remove(annotation)
    
    if not len(other_annotations) == 2:
        _validation_err(user_id, field, 'The three annotations for this image are not unique', f'{other_annotations_orig} - {len(other_annotations)}')
    
    # Now make sure that this annotation does not match other previously submitted annotations
    u = User.query.get(user_id)
    
    if u:
        prev_annotation_objs = u.annotations
        other_annotations = [a.q_content for a in prev_annotation_objs]
        other_annotations = set([_lcase_and_remove_whitespace(item) for item in other_annotations])
        
        if annotation in other_annotations:
            _validation_err(user_id, field, 'This annotation matches a previous annotation from another image')          
    else:
        _validation_err(user_id, field, 'When validating annotations, could not find this user in the database')

def _lcase_and_remove_whitespace(s):
    s = re.findall("[a-z]+", s.lower())
    return "".join(s)

def _validation_err(user_id, field, validation_msg, supp_logging_msg=""):
    logger.error(f'User {user_id}: {validation_msg}; {supp_logging_msg}')
    field.errors += (ValidationError(validation_msg),)
    StopValidation()