
#VQG Annotation Application

# To Set up for the First Time

## Setting up AWS
This part of the instructions assumes that you are using an EC-2 instance running Amazon Linux.  If you are using a different OS, you may need to adjust these instructions.

Once on the instance, run the following commands:

```
yum update
yum install git
```

Follow through prompts to install packages.  Now clone the git repo:

```
git clone https://github.com/amb467/vqg.git
```

You will need to provide your git credentials.  Now move into the repo directory and install all required python packages:


```
cd vqg
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

## DB Initiation and Setup

To create the database and its corresponding tables, from the top-level directory, run the following:

```
flask db init
flask db migrate -m "[description]"
flask db upgrade
```

(You can sudo this if you're on AWS)

After running this command, you should find a SQLite database in the `app` directory.  The name of the database depends on what it is called in the `.flaskenv` file.  If you open the database and look at all of the tables, you should find the tables and schemas described in `app/models.py`.

Note that, when making table and schema changes in the future, the latter two commands described above should be used.  `flask db migrate` generates migration scripts and `flask db upgrade` runs the migration scripts.

## Loading Image Data into the Database

Once the database and schema are created, you must run the script that loads image information into the image table:

```
python3 app/load_images.py
```

The default arguments of this script are designed to be run from the top-level directory.  You will also need to change the arguments if you want to use non-default image files (the default files include the entire VQG COCO data set).  To see more information about arguments, run:

```
python3 app/load_images.py --help
```

# To Run

If you are on AWS, you should run flask in the background.  You can skip this step if you're running locally:

```
screen
```

From the top-level directory, run the following command:

```
flask run
```

You should see the following:

```
 * Serving Flask app "vqg.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

To quit the app, go to the terminal and hit Ctrl+C.

If you are running in the background, you can return to the foreground by typing Ctrl+A followed by Ctrl+D.

If you need to return to the background screen where you can interact with the application, run:

```
screen -r
```