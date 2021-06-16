import os, logging
from flask import flash, redirect, render_template, request, url_for
from app import app
from app.forms import InitialScriptForm, AnnotationForm, PostSurvey
from app.utils import get_progress_completion, get_user_progress, get_url_params, get_image, validate_step, get_unique_prolific_id
from app.nocache import nocache

### Set up logging
logger = logging.getLogger('vqg')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('vqg.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

@app.route('/', methods=['GET', 'POST'])
@nocache
def main():

    user_id, progress, err_msg = get_user_progress(request)
    logger.info(f'User {user_id}: Received request at progress step {progress}')
    if err_msg:
        logger.error(f'User {user_id}: Error message received when checking progress: {err_msg}')
        return err_msg, 400
        
    # The participant has completed the task and needs a completion code
    if progress == get_progress_completion():
        logger.info(f'User {user_id}: User completed the task and is receiving a completion code')
        title = "Task Completion"
        return render_template('completion.html', title=title, progress=progress, completion_code=os.environ.get('COMPLETION_CODE'))
    
    # The participant went through the survey but did not successfully complete the task
    # and does not get a completion code
    if progress == -1:
        logger.info(f'User {user_id}: User failed to complete and will not receive a completion code')
        title = "Task Not Complete"
        return render_template('completion.html', title=title, progress=get_progress_completion())
    
    # New user
    if progress == 0:
        logger.info(f'User {user_id}: Returning initial script to user')
        form = InitialScriptForm()
        title = "Welcome to the VQG (Visual Question Generation) annotation application"
    
    # The participant has completed the annotation task and must now complete the post-survey
    if progress == get_progress_completion() - 1:
        logger.info(f'User {user_id}: User completed the annotation task, returning post-survey')
        form = PostSurvey()
        title = "Post-Survey"
        
    # The participant is in the middle of annotation
    elif progress > 0:
        logger.info(f'User {user_id}: User is at annotation step {progress}, returning annotation form')
        form = AnnotationForm()
        title = "Image Annotation"
             
    if request.method == 'POST':
        if form.validate_on_submit():
            form_str = []
            for field in form:
                form_str.append(f"{field.name}: {field.data}")
            logger.info(f'User {user_id}: Progress step {progress} form validated: {"; ".join(form_str)}')        
            err_msg = validate_step(user_id, form)
        
            if err_msg:
                logger.error(f'User {user_id}: Error message received when validating progress: {err_msg}')
                return err_msg, 400
        
            return redirect(f"{url_for('main')}{get_url_params(request, progress)}")
    
        else:
            logger.info(f'User {user_id}: Form did not validate.  Form errors: {form.errors}')
            flash(f'Form errors: {form.errors}')
            
    image_id, image_url, err_msg = get_image(user_id)
        
    if not err_msg is None:
        return err_msg, 400
    
    if "image_id" in form.data.keys():
        logger.info('User {user_id}: adding image id {image_id} to form')
        form.image_id.data = image_id
        
    form.user_id.data = user_id    
    return render_template('index.html', title=title, progress=progress, form=form, image_id=image_id, image_url=image_url)

# Navigate here to automatically generate an unused Prolific ID 
@app.route('/get_params', methods=['GET'])
@nocache
def get_params():
    return redirect(f"{url_for('main')}{get_unique_prolific_id()}")
    