'''

@author: Nicolas Van Labeke (https://github.com/vanch3d)
@date: 22 Nov 2012
@version: 0.1
'''

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()