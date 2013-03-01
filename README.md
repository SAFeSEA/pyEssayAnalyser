pyEssayAnalyser {#pyEssayAnalyser}
===============

An essay Analyser &amp; Summariser, using Flask for the API and NLTK for the language processing.

## Installation

1. Clone the project locally on your computer.
2. Make sure pip and virtualenv are installed.
3. Create a Python virtual environment in the project directory.
   The Git repository already ignores a `venv` directory so why not creating it  

~~~~~~~~~~~~~~~~~~~~~
    $ cd pyEssayAnalyser
    $ virtualenv venv
~~~~~~~~~~~~~~~~~~~~~

4. Activate the virtual environment. On Linux, do the following:
   
~~~~~~~~~~~~~~~~~~~~~
    $ . venv/bin/activate
~~~~~~~~~~~~~~~~~~~~~

   On Windows, the following will work:
  
~~~~~~~~~~~~~~~~~~~~~
    $ venv\scripts\activate
~~~~~~~~~~~~~~~~~~~~~
  
5. Install the Python requirements. 
   The project contains a file `stable-req.txt` created with pip. Use it to install - in the virtual environment - 
   all the packages needed for the system to work.
  
~~~~~~~~~~~~~~~~~~~~~
  $ pip install -r stable-req.txt 
~~~~~~~~~~~~~~~~~~~~~

6. Download the NLTK data.
   NLTK comes with many corpora and trained models, some of which are needed for various aspect of essay analysis.
   Run the Python interpreter and type the commands: 

~~~~~~~~~~~~~~~~~~~~~{.py}
. >>>	import nltk
. >>>	nltk.download('all')
~~~~~~~~~~~~~~~~~~~~~
   
   Try the NLTK installation:
   
~~~~~~~~~~~~~~~~~~~~~{.py}
   >>> from nltk.corpus import brown
   >>> brown.words()
   ['The', 'Fulton', 'County', 'Grand', 'Jury', 'said', ...]
~~~~~~~~~~~~~~~~~~~~~

7. Try the Flask installation and configuration:

~~~~~~~~~~~~~~~~~~~~~
   $ python src/TestFlask.py
     * Running on http://127.0.0.1:5000/
~~~~~~~~~~~~~~~~~~~~~

Head over to http://127.0.0.1:5000/ in your browser, you should see the Hello World greetings.
 

## Deployment of the EssayAnalyser

~~~~~~~~~~~~~~~~~~~~~
   $ python src/pyEssayAnalyser.py
     * Running on http://127.0.0.1:5000/
~~~~~~~~~~~~~~~~~~~~~

TO DO.

## API

TO DO.

Method  | URL        | Action
--------|------------|------
GET     | /                | Hello world 
POST    | /api/essay       | add a new essay to the system and return various analytics
GET     | /api/essay/UID | Retrieve essay with id = UID
PUT     | /api/essay/UID | Update essay with id = UID
GET     | /api/essay/UID/analytics | Retrieve various analytics on the essay with id = UID
