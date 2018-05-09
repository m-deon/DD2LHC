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
## Deployment
### Heroku
In order go get plots on heroku, before deploying the first time go to in Heroku to 'settings' app and add the following buildpack: https://github.com/kennethreitz/conda-buildpack.git
