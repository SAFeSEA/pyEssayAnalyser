'''
Created on 11 Nov 2012

@author: Nicolas Van Labeke (https://github.com/vanch3d)
'''

from flask import Flask, request
from flask_debugtoolbar import DebugToolbarExtension

from EssayAnalyser import API
from flask.helpers import jsonify

app = Flask(__name__)

# Create the debug toolbar
app.debug = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'nvl'   # enable the Flask session cookies
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
#app.config['DEBUG_TB_PANELS'] = (
# 'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
# 'flask_debugtoolbar.panels.logger.LoggingPanel',
# 'flask_debugtoolbar.panels.timer.TimerDebugPanel',
#)
toolbar = DebugToolbarExtension(app)

# Define the routes

@app.route('/')
def hello_world():
    api = []
    api.append({"method" : "POST", "url":"/api/essay/analysis"})
    api.append({"method" : "POST", "url":"/api/essay/dispersion"})
    
    info = {}
    info['name'] = "pyEssayAnalysier"
    info['version'] = "0.1"
    info['api'] = api

    app.logger.info("Hello there")
    
    return jsonify(info)


@app.route('/api/essay/analysis', methods=['POST'])
def essay_post_new():
    return API.process_essay()
    
@app.route('/api/essay/dispersion', methods=['POST'])
def essay_post_dispersion():
    return API.process_dispersion()
    


#@app.route('/api/essay/<essayID>', methods=['GET','PUT'])
#def essay_getput(essayID):
#    return 'Hello ' + essayID  + "!"
#
#
#@app.route('/api/essay/<essayID>/analytics', methods=['GET'])
#def essay_get_analytics(essayID):
#    return 'Hello ' + essayID  + "!"


if __name__ == '__main__':
    app.run(None,8062)