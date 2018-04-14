# DD2LHC

## DEV

```
# install conda
# create env
conda create -n dd2lhc python=2.7.10 -y
source activate dd2lhc
conda install -y --file conda-requirements.txt
pip install -r requirements.txt
```

To run locally:
```
source activate dd2lhc #if in new session
python app.py
```

#for Heroku:
In order go get plots on heroku, before deploying the first time go to in Heroku to 'settings' app and add the following buildpack:
https://github.com/kennethreitz/conda-buildpack.git


#for Docker:
heroku plugins:install heroku-container-registry
heroku container:login
heroku create
heroku container:push web
