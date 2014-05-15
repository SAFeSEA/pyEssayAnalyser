#from time import time # For calculating processing times
#from operator import itemgetter # For sorting by particular arguments etc.
#import itertools # For working with multiple arguments that are iterators
import os.path # This is for file handling
import tempfile # For handling OS's temporary files directories
import shutil # For file operations
import codecs # For handling encoding 
from EssayAnalyser.se_main_v3 import top_level_procedure
#import networkx as nx  # For drawing the sample graph.
#import matplotlib.pyplot as plt # For drawing the sample graph.
#import pylab
#import sbd # This is an alternative sentence splitter
#import profile # For running the Python profiler to see which functions are hogging the time
#from __future__ import division # This enables Python to use floating point division (otherwise division of smaller integer by greater = 0)

"""
Filename: se_batch_v3.py
Run this file to invoke EssayAnalyser. All files with extension .txt located in
 the same folder as this file will be analysed. Results will be put into a new
 temporary folder in the 'Temp' directory on the hard disk 
 (e.g., C:\users\debora\appdata\local\temp\...).
Before running a new version to generate a test set of data, check:
 - directedness of the sentence graph
 - key lemma threshold -  Does Nicolas want all the lemmas ranked, or the top N?
 - key sentence threshold -  Do you want all the sentences ranked, or the top N?
 - values defining the subgraphs
 - algorithm (betweenness or pagerank) of the key word graph
 - comment out arguments for comparing assignment question with essay. These are in ke_all.py.
 - make sure the correct sentence labels are being fed into ea.py by main.py.
Before uploading to Github:
 - empty the data folder in src
 - remove any text files from src
 - remove any other files you have added to src
 - check no invalid 'import' expressions.
 # -*- coding: ascii -*-
 
"""

#startproctime = time() # Set current time to a variable for later calculations

#def main():

# Toggle between developer initials. My initials set to 'dev' switches on printing in a handful of cases.
dev = 'DGF'
#dev = 'NVL'

# The following model needs to be loaded if we use the alternative sentence splitter.
#model = sbd.load_sbd_model('C:/Python27/Lib/site-packages/splitta.1.03/model_nb/', use_svm=False) # Playing with a different sentence splitter

# Begin by deleting the temporary directory and files you created last time you ran this program.
tempdir0 = tempfile.gettempdir() # This gets the path to the location of the temporary files and dirs.
tempfilelist = os.listdir(tempdir0) # This gets a list of the items stored in that location

for dirname in tempfilelist:
	fullpath = os.path.join(tempdir0, dirname) # Join the path name to the dir name so you can delete the directories
	if dirname.startswith('AAA_SentExtrac_Results_'): # Only delete the temp dirs that you have created in an earlier run of this program.
		shutil.rmtree(fullpath) # Do the deletion

tempdir1 = tempfile.mkdtemp(suffix='', prefix='AAA_SentExtrac_Results_', dir=None) # Create a new directory for the essay results files to go in. Make it a temporary directory. Temporary files are stored here: c:\\users\\debora\\appdata\\local\\temp		
cwdir = os.getcwd()  # Get current working directory
filelist = os.listdir(cwdir) # Set var 'filelist' to a list of files in cwdir. 'listdir' reads the dir you've given it, and returns a list of files.
newfilename2 = os.path.join(tempdir1, 'sent_extract_results_summary.txt') 
nf2 = codecs.open(newfilename2, 'w',encoding='utf-8') # Open 'newfilename2' (for writing to) and set open file to var 'nf2'
#nf2.write('\nProgram started running at: ') # Write to summary results file 'nf2' the start time of the program
#nf2.write(str(startprogtime))
#nf2.write('\n\n*********************************************************\n\n')
#endimporttime = time() # Set current time to a variable for later calculations

for essay_fname in filelist: # For each file in the current directory...
    #startfiletime = time() # Set current time to a variable for later calculations
    if essay_fname[-3:] == 'txt': # If a file name ends in 'txt'...
        print '\n', essay_fname # Print to shell to monitor progress
        f = codecs.open(essay_fname, 'r',encoding='utf-8') # Open current essay file for reading
        essay_txt = f.read() # Read in the essay and set to var 'essay_txt'
        f.close() # Close the essay file
        string = essay_fname[:-4] + '_results' + '.txt'
        newfilename = os.path.join(tempdir1, string)                     
        nf = codecs.open(newfilename, 'w',encoding='utf-8') # Open 'newfilename' (for writing to) and set open file to var 'nf'

        #if dev == 'DGF':
            #nf2.write('\n') # Add blank lines to the essay results file            
        nf2.write(str(essay_fname)) # Write the new file name to the essay results file
        nf2.write('; ')        
        essay = top_level_procedure(essay_txt,essay_fname,nf,nf2,dev,"H810","TMA01")

        #nx.write_weighted_edgelist(gr_se, fullpath, comments="#", delimiter=' ', encoding='utf-8') # This writes edge list to temp dir instead of to cwd
        #print '\n\n', essay, '\n\n', essay_id , '\n\n'
        # soopakallerfrajallipstickcexxpeealliidoshus
        #print gr_se.edges(data = True)
        print '\n', essay_fname # Print to shell to monitor progress        
        nf.close() # Close the essay results file
nf2.close() # Close the summary results file.

#endproctime = time()
#proctime = endproctime - startproctime
#print '\n\n\nThis is proctime for all files: ', proctime


#main()
#profile.run('main(); print') # These lines concern profiling this program (see how many times functions are called, etc. NB profiler runs slowly.) but the indentation is wrong for this at the moment.

# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>

