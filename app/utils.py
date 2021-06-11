import os, logging
from app import db
from app.models import User, Image, Annotation
from sqlalchemy.exc import OperationalError

PROGRESS_COMPLETION = int(os.environ.get('PROGRESS_COMPLETION'))
logger = logging.getLogger('vqg')

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
        _try_commit()
    
    err = "" if len(err) == 0 else "; ".join(err)
    return arg_dict['PROLIFIC_PID'], u.progress, err

##########
#
#   Return the parameters to append to the redirect url
#
########## 
def get_url_params(request, progress):
    args = [f"{arg_name}={request.args.get(arg_name)}" for arg_name in ['PROLIFIC_PID', 'STUDY_ID', 'SESSION_ID']]
    args = "&".join(args)
    args = f"?{args}&progress={progress}"
    logger.info(f"User {request.args.get('PROLIFIC_PID')}: returning parameters {args}")
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
def get_image(username):
    image_id = 314392
    image_url = "https://vision.ece.vt.edu/data/mscoco/images/train2014/./COCO_train2014_000000314392.jpg"
    return image_id, image_url

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
    if u.progress == PROGRESS_COMPLETION or u.progress == -1:
        return "User complete"
    
    # New user, advance if the user select "I understand"
    if u.progress == 0:
        if not form.understand:
            err = "User did not select 'I understand'"
    
    # User submitted post-survey, advance if the user answered questions correctly
    elif u.progress == PROGRESS_COMPLETION - 1:
        err = _validate_post_survey(form)
    
    # The user is annotating, advance if the user gave three unique questions for this image
    else:
        err = _validate_annotation(u, form)
    
    if not err:
        u.progress = u.progress + 1
        logger.info(f'User {user_id}: Advancing progress to {u.progress}')
        _try_commit()
    
    return err

def _validate_post_survey(form):
    return ""

def _validate_annotation(u, form):
    return ""       

def _try_commit():
    try:
        db.session.commit()
    except Exception as err:
        logger.error(f'User {user_id}: Error message received when committing database: {err}')
        print(f'Attempted to commit database and encountered a problem: {err}')
