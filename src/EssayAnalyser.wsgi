activate_this = '/PATHTOPROJECT/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0,'/PATHTOPROJECT')

from TestFlask import app as application
