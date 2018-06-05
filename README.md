# DM Limiter

This app was developed at Brandeis University to leverage research by Bjoern Penning in the search for Dark Matter. The app leverages a conversion algorithm to compare results between various collider experiments and direct detection experiments. DM Limiter will analyze the selected results and  plot both the simplified model plane and the direct detection plane for comparison.

![DM Limiter Screenshot](https://github.com/jcope/DD2LHC/blob/master/Screenshot.png "DM Limiter")

---
## Install and Setup

#### install conda
https://conda.io/docs/user-guide/install/download.html

#### create conda env
```
conda create -n dd2lhc python=2.7.10 -y
```

### activate conda python session
```
source activate dd2lhc
```
#### install packages
```
conda install -y --file conda-requirements.txt
pip install -r requirements.txt
````
#### initialize User Database:
```
python manage.py init_db
```
---
## Usage

### activate conda python session
```
source activate dd2lhc
```
### To run locally:
```
python manage.py runserver #Launch App
```

### Other Commands:
Use `python manage.py` for a list of available commands.  
Use `python manage.py runserver` to start the development web server on localhost:5000.  
Use `python manage.py runserver --help` for a list of runserver options.

---
## Development
While there are many files and packages used to create DM Limiter, in practice you will only need to modify the following files during maintenance development. DM Limiter is a `Flask` application built using `python`. `Javascript` is used to handle runtime logic in the browser, and `HTML` and `CSS` is used to describe the template pages used to render the UI.

`app/dmplotter/plotter.py` Business logic that reads data, applies conversions, defines plot configurations

`app/dmplotter/conversions.py` **Actual conversion/theory that applies to DM research**

`app/dmplotter/forms.py` Declarations for the html forms found on the main DM Limiter page


`app/static/scripts/main.js` Web logic executed at run time (ie detect change in forms, update metadata displayed)

`app/views/mainviews.py`  Maps the web addresses to actual actions and page renderings


`app/templates/layout.html` Contains the basic layout all other pages are generated from

`app/templates/dmplotter.html` Template and layout for the dm limiter app (configuration forms, dual plots, everything).

`app/templates/about.html` The about page (accessed at top navigation)

`app/templates/theory.html` The theory page (accessed at top navigation)


`app/static/css/style.css` General stylesheet for the overall layout/theme of web app

---
## Deployment
### Heroku
In order go get plots on heroku, before deploying the first time go to in Heroku to 'settings' app and add the following buildpack: https://github.com/kennethreitz/conda-buildpack.git

### PythonAnywhere

https://help.pythonanywhere.com/pages/Flask/

***Note: Replace `JCope` with actual username/account name***
Create a virtual python environment using version 2.7
`mkvirtualenv --python=/usr/bin/python2.7 my-virtualenv`
Use this file to install the package requirements on
`deploy/pythonanywhere/requirements.txt`
Example WSIG file
`deploy/pythonanywhere/DMLimiter_WSIG.py`
Set working path to
`/home/JCope/DD2LHC`
