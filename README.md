
#VQG Annotation Application

# To Set up for the First Time

## Accessing AWS

Put something here about cloning repo, installing python3 and requirements.txt
Don't forget to upgrade pip

## DB Initiation and Setup

To create the database and its corresponding tables, from the top-level directory, run the following:

```
flask db init
flask db migrate -m "[description]"
flask db upgrade
```

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

To access the app, you can now navigate to [http://localhost:5000](http://localhost:5000)

To quit the app, go to the terminal and hit Ctrl+C.