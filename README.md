# Parking App

### Development Notes
- Follow `Project Setup` below for the high-fidelity prototype and HERE for the low-fidelity prototype
- For activity, case, and class diagrams, updated project definition, look at `RubberDuckyParking/documentation/homework_milestones/milestone2/requirements_definition_group_6.pdf`
- Look on `github.com/Bryson14/RubberDuckyParking/issues` for our GitHub backlog.


### Organization
The project is organized into two main part: `src` and `documentation`. Since this is a semester project, there is lots of documentation and decisions made in `documentation` under their respective milestones folders. `src` contains the django webserver, the website files, database, and anything else to run the app.

### Version Control
Required software is under `src/requirements.txt`. It is recommended to run this project in a virtualenv so their is no issues between python and DJango versions.
This project is controlled through pull requests. Every commit from every member is a pull request. It is recommended that at
least one member of the team review another pull request, before the author merges the pr. The main branch
for every team member should be updated before working every day so avoid merge conflicts.

## Project Setup

Create a virtualenv 
```
$ python -m virtualenv ducky_env
```


Activate the virtualenv
```
$ cd ducky_env
$ source Scrpits/activate (Windows)
$ source bin/activate (Linux/ Mac)
```

Clone the repo inside of the virualenv
```
$ cd ducky_env
$ git clone https://github.com/Bryson14/RubberDuckyParking.git
```
Download the packages inside the virtualenv

```
$ python -m pip install -r RubberDuckyParking/requirements.txt (With active virtualenv)
```

### Django db setup
```
$ python manage.py migrate
```
- this will create the schema for the models
```
$ python manage.py db_seed
```
- this is the custom management command that will add some basic models for you
```
$ python manage.py createsuperuser
```
- this will create your user that has admin access
```
localhost:8000/admin
```
- go check out the newly created models

Tool Stack:
Linux, DJango Webserver, SQLite, Vue

### Compiles and hot-reloads for development
```
$ python manage.py runserver
```

### Unit Testing
`./manage.py test` will run the JDango's built in system to run unit test that are found in `test.py`

### System Testing
For best testing results, running the server on many different computers and accessing them from various browsers for desktop and mobile (Brave, Cake, Safari, Chrome, Edge, Mozilla)

### For documentation
See documentation/

### starting your db over
```
$ python manage.py flush
```
- this will remove all your db's data, but it will not change the schema
- If you want to completely start over, delete your db.sqlite3 file and all the migration files except for the `__init__.py` files
    - once this is done, follow the db setup mentioned at the top of this readme
    