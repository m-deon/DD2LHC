# +++++++++++ FLASK +++++++++++
# Flask works like any other WSGI-compatible framework, we just need
# to import the application.  Often Flask apps are called "app" so we
# may need to rename it during the import:
#
#
import sys
import os
from dotenv import load_dotenv
#
## The "/home/JCope" below specifies your home
## directory -- the rest should be the directory you uploaded your Flask
## code to underneath the home directory.  So if you just ran
## "git clone git@github.com/myusername/myproject.git"
## ...or uploaded files to the directory "myproject", then you should
## specify "/home/JCope/myproject"
path = '/home/JCope/DD2LHC'

#Apply environment variables
project_folder = os.path.expanduser(path)  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

if path not in sys.path:
    sys.path.append(path)

#from app import app as application  # noqa
from app import create_app
application = create_app()
