pyEssayAnalyser
===============

An essay Analyser &amp; Summariser, using Flask for the API and NLTK for the language processing.

## Installation

1- Clone the project locally on your computer.
2- Make sure pip and virtualenv are installed.
3- Create a Python virtual environment in the project directory.
   The Git repository already ignores a `venv` directory so why not creating it  

~~~~~~~~~~~~~~~~~~~~~
    $ cd pyEssayAnalyser
    $ virtualenv venv
~~~~~~~~~~~~~~~~~~~~~

4- Activate the virtual environment. On Linux, do the following:
   
~~~~~~~~~~~~~~~~~~~~~
    $ . venv/bin/activate
~~~~~~~~~~~~~~~~~~~~~

   On Windows, the following will work:
  
~~~~~~~~~~~~~~~~~~~~~
    $ venv\scripts\activate
~~~~~~~~~~~~~~~~~~~~~
  
5- Install the Python requirements. 
   The project contains a file `stable-req.txt` created with pip. Use it to install - in the virtual environment - 
   all the packages needed for the system to work.
  
~~~~~~~~~~~~~~~~~~~~~
  $ pip install -r stable-req.txt 
~~~~~~~~~~~~~~~~~~~~~

6- Download the NLTK data.
   NLTK comes with many corpora and trained models, some of which are needed for various aspect of essay analysis.
   Run the Python interpreter and type the commands: 

~~~~~~~~~~~~~~~~~~~~~{.py}
  >>> import nltk
  >>> nltk.download('all')
~~~~~~~~~~~~~~~~~~~~~
   
   Try the installation:
   
~~~~~~~~~~~~~~~~~~~~~{.py}
   >>> from nltk.corpus import brown
   >>> brown.words()
~~~~~~~~~~~~~~~~~~~~~

## APIs




