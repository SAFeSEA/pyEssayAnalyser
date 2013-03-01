import logging
from logging import getLogger
#import tempfile
#from nltk.data import load
#from time import time

# Create an event logger for the EssayAnalyser module
_apiLogger = getLogger(__name__)
_apiLogger.setLevel(logging.DEBUG)

# Create a file handler for the output
fh = logging.FileHandler('_EssayAnalyser.log')
fh.setLevel(logging.INFO)

# Change the format of the output
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
fh.setFormatter(formatter)

# Add the file handler to the logger
_apiLogger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
_apiLogger.addHandler(ch)

# Create a temporary directory (used for caching results)
# This will be created once per session, when the system is launched 
#_tempDir = tempfile.mkdtemp(suffix='', prefix='AAA_essayAnalyser_cache_', dir=None)
#_apiLogger.info("Create cache directory: " + _tempDir)


#proctime = time() 
#_POS_TAGGER = 'taggers/maxent_treebank_pos_tagger/english.pickle'
#_eaTagger = load(_POS_TAGGER)
#_apiLogger.info(">> #####_eaTagger###### : %s" % (time() - proctime)) 
