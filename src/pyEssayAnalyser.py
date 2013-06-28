'''
Created on 11 Nov 2012

@author: Nicolas Van Labeke (https://github.com/vanch3d)
'''

from flask import Flask, request
from flask_debugtoolbar import DebugToolbarExtension

#from EssayAnalyser import API
from flask.helpers import jsonify
#from EssayAnalyser.se_print_v3 import Flask_process_text

from api_handlers import Flask_process_text

app = Flask(__name__)

# Create the debug toolbar
app.debug = False
#app.config['DEBUG'] = True
#app.config['SECRET_KEY'] = 'nvl'   # enable the Flask session cookies
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
#app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
#app.config['DEBUG_TB_PANELS'] = (
# 'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
# 'flask_debugtoolbar.panels.logger.LoggingPanel',
# 'flask_debugtoolbar.panels.timer.TimerDebugPanel',
#)
#toolbar = DebugToolbarExtension(app)

# Define the routes

@app.route('/')
def hello_world():
    """
    Route for the documentation of the API
    
    @return: a JSON object containing the APIs of the services
    """
    
    apis = []
    apis.append({
                 'method' : 'POST', 
                 'url' : '/api/analysis',
                 'params': [{
                        'attribute' : 'text',
                        'value' : 'string'
                           }]
    })
    
    info = {}
    info['name'] = 'pyEssayAnalyser'
    info['version'] = "3.0"
    info['api'] = apis

    return jsonify(info)


@app.route('/api/analysis', methods=['POST'])
def essay_post_new():
    """
    Route for the processing of an essay submitted by POST request
    @param text:    the text to process
    @return:
        - a JSON object containing the learning analytics of the essay, an error message if problems
        - the status code of the transaction (200 or 500)
    """
    
    try:
        text0 = request.form['text']
        module = request.form['module']
        task = request.form['task']
        essay = {}
        status = 200
    
        #if (app.debug is  True):
        #    essay = Flask_process_text(text0,module,task) 
        #else:
        essay = Flask_process_text(text0,module,task) 
    except Exception as e:
        ## Any unsupported exceptions coming from code
        ## TODO: get a better error message (not revealing internal error)
        print repr(e)
        status = 500
        essay = { 'error' : {  
            'status' : status,
            'msg'    :repr(e)}}
    
    return jsonify(essay) , status  
    

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(None,8062)