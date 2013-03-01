'''
Created on 11 Nov 2012

@author: Nicolas Van Labeke (https://github.com/vanch3d)
'''

from flask import Flask, request
from flask_debugtoolbar import DebugToolbarExtension

#from EssayAnalyser import API
from flask.helpers import jsonify
from EssayAnalyser.se_procedure_v3 import pre_process_text_se, pre_process_struc,\
    process_essay_se
from EssayAnalyser.ke_all_v3 import process_essay_ke
from EssayAnalyser.se_print_v3 import nicolas_results_se

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
    """
    Route for the documentation of the API
    
    @return: 
        - a JSON object containing the
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

    #    app.logger.info("Hello there")
    
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
    
    text0 = request.form['text']        # NVL : the text of the essay is extracted from the FORM part of the REQUEST, as received by the API
    essay = {}
    
    status = 200
    try:
        ##############################
        ##############################
        ## 3. Do required NLP pre-processing on this essay
        ##############################
        ##############################
        text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,None,None,"NVL")
        # Next line is needed instead of above line if we are using sbd sentence splitter.
        #text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,nf,nf2,model,dev)
           
        ##############################
        ##############################
        ## 4. Do required essay structure pre-processing on this essay
        ##############################
        ##############################
        text_se,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last = pre_process_struc(text,None,None,"NVL")
        
        ##############################
        ##############################
        ## 5. Construct the key sentence graph and do the graph analyses
        ##############################
        ##############################      
        gr_se,myarray_se,ranked_global_weights,reorganised_array,graphtime=process_essay_se(text_se,parasenttok,None,None,"NVL")
    
        ##############################
        ##############################
        ## 6. Construct the key word graph and do the graph analyses
        ##############################
        ##############################      
        text_ke,gr_ke,di,myarray_ke,keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases=process_essay_ke(text_se,wordtok_text,None,None,"NVL")
    
        ##############################
        ##############################
        ## 7. Write to file whichever results you choose
        ##############################
        ##############################      
        essay, essay_id = nicolas_results_se(gr_se,ranked_global_weights,parasenttok, number_of_words,struc_feedback)
    except Exception as e:
        status = 500
        essay = { 'error' : 
                 {  'status' : status,
                    'msg'    : e.message}}
     
    return jsonify(essay) , status  

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

#@app.route('/api/essay/analysis', methods=['POST'])
#def essay_post_new():
#    return API.process_essay_v2()
    
#@app.route('/api/essay/dispersion', methods=['POST'])
#def essay_post_dispersion():
#    return API.process_dispersion()
    
#@app.route('/api/essay/keywords', methods=['POST'])
#def essay_post_keywords():
#   return API.process_keyword_v2()

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