'''
Created on 11 Nov 2012

@author: Nicolas Van Labeke (https://github.com/vanch3d)
'''

from flask import Flask, request

from EssayAnalyser import API as API

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/essay', methods=['POST'])
def essay_post_new():
    return API.process_essay()
    


@app.route('/api/essay/<essayID>', methods=['GET','PUT'])
def essay_getput(essayID):
    return 'Hello ' + essayID  + "!"

@app.route('/api/essay/<essayID>/analytics', methods=['GET'])
def essay_get_analytics(essayID):
    return 'Hello ' + essayID  + "!"


if __name__ == '__main__':
    app.run(debug = False)