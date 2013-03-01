from __future__ import division # This enables Python to use floating point division (otherwise division of smaller integer by greater = 0)
from time import time # For calculating processing times
startprogtime = time() # Set current time to a variable for later calculations
import os # This is for file handling
import tempfile
import shutil
#import sbd # This is an alternative sentence splitter
import re # For regular expressions
from sentence_extrac_v2_functions import * # File containing my own functions. This version of the functions uses cosine similarity, no edge if edge == 0, AND uses two arrays to speed up building of the graph. Results are in results_4a.

"""
This program implements a version of the TextRank algorithm for extractive summaries (based on sentence extraction) from (Mihalcea and Tarau, 2005, 2004), which uses the PageRank algorithm (Brin and Page 1998) and applies it to the extraction of key sentences from a text (extractive summarisation). The program processes every file in its current working directory that ends in 'txt', and puts a results file for each file processed in a newly created temporary directory. The program also generates a single summary results file that contains results information on all the files that have been processed. For each file ending in 'txt', the program does the following. It assumes the file has been saved in Latin9 encoding. First it does some pre-processing: latin9 tidy-up, paragraph, sentence, and then word tokenisation, removal of punctuation, put into lower case, stop words removed. Then structural parts are identified and each sentence is labelled with its structural function in the essay. Then the program builds a graph using sentences as nodes. The actual sentences are not the nodes, a Python dictionary is used to store the sentences using a key, and the key is used for the nodes. Directed edges are drawn between pairs of sentences that are similar. The similarity of a pair of sentences/nodes is represented by the weight of the edge that joins them. In this version of the program the similarity measure is cosine similarity. Edges point only from a later/greater sentence/node to an earlier one. A global weight score WSVi for each node is then calculated. The WSVi score for a node Vi represents how important the sentence Vi is compared to the whole essay. A sentence is important if it is similar to other sentences that are similar to other sentences that are similar to other sentences that are similar... Initially, an arbitrary WSVi value is set for every node in order to enable the program to work out the 'real' value. It is necessary to set arbitrary values for WSVi in the first instance because the procedure for finding a WSVi score requires you to find a WSVi score, i.e., it is recursive. So you need some values in order to be able to start. The arbitrary values move closer towards the real values at every iteration until very little difference is made by further iterations. Once the scores are derived, all the sentences with their WSVi scores are sorted according to the scores, and written to the results file. The highest-scoring sentences are those that are the most important/representative in the text.

Refs:
Brin, S. and L. Page, (1998). The Anatomy of a Large-Scale Hypertextual Web Search Engine. In Seventh International World-Wide Web Conference (WWW 1998), Brisbane, Australia, 14-18 April 1998.

R. Mihalcea and P. Tarau (2004). Textrank: Bringing order into texts. In L. Dekang and W. Dekai (eds.), Proceedings of Empirical Methods in Natural Language Processing (EMNLP) 2004, pp. 404–-411, Association for Computational Linguistics, Barcelona, Spain, July 2004.

R. Mihalcea and P. Tarau (2005). A language independent algorithm for single and multiple document summarization. In Proceedings of the Second International Joint Conference Natural Language Processing (IJCNLP’05), Korea, pp. 602–-607, 11–-13 October 2005.
"""

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
nf2 = open(newfilename2, 'w') # Open 'newfilename2' (for writing to) and set open file to var 'nf2'
nf2.write('\nProgram started running at: ') # Write to summary results file 'nf2' the start time of the program
nf2.write(str(startprogtime))
nf2.write('\n\n*********************************************************\n\n')
#endimporttime = time() # Set current time to a variable for later calculations
# The following model needs to be loaded if we use the alternative sentence splitter.
#model = sbd.load_sbd_model('C:/Python27/Lib/site-packages/splitta.1.03/model_nb/', use_svm=False) # Playing with a different sentence splitter
for filename in filelist: # For each file in the current directory...
    #startfiletime = time() # Set current time to a variable for later calculations
    if filename[-3:] == 'txt': # If a file name ends in 'txt'...
        print '\n\n_____________________________________________'            
        print filename # Print to shell to monitor progress
        f = open(filename, 'r') # Open current essay file for reading
        text0 = f.read() # Read in the essay and set to var 'text0'
        f.close() # Close the essay file
        string = filename[:-4] + '_results' + '.txt'
        newfilename = os.path.join(tempdir1, string)                     
        nf = open(newfilename, 'w') # Open 'newfilename' (for writing to) and set open file to var 'nf'
        nf.write('\n\n') # Add blank lines to the essay results file            
        nf.write(str(filename)) # Write the new file name to the essay results file
        nf.write('\n\n') # Add blank lines to the essay results file
        nf2.write(str(filename)) # Write current essay file name to the summary results file
        #nf2.write('\n') # Add a blank line to the summary results file            

        ###################################################
        ###################################################
        # DGF: Nicolas, hopefully you should be able to just lift everything between here and the next double row of hashes
        # and substitute it for your two functions 'get_segmented_text' and 'process_essay' in your 'api.py' file.
        
        # DGF: Nicolas, toggle between developer initials. My initials set to 'dev' switches on printing and writing to file. 
        dev = 'DGF'
        #dev = 'NVL'

        struc_feedback = {}

        # DGF: Nicolas, next line does all text processing work, including analysing the structure of the essay
        # In the returned 'text', each sentence is labelled according to its structural function.
        text,parasenttok,number_of_words,section_names,section_labels = pre_process_essay(text0,struc_feedback,nf,nf2,dev)

        # Next line is needed instead of above line if we are using sbd sentence splitter.
        #text,parasenttok,number_of_words,section_names,section_labels = pre_process_essay(text0,struc_feedback,nf,nf2,model)        

        # DGF: Nicolas, I have added in your 'apiLogger' calls (commented out). 
        #_apiLogger.info("text segmented:\t" + str(parasenttok))

        #texttime = time() # Set current time to a variable for later calculations

        gr, myarray, ranked_global_weights, reorganised_array, graphtime = process_essay(text, parasenttok, nf,nf2,dev)

        #_apiLogger.info("nodes:\t" + str(gr.nodes()))
        #_apiLogger.info("" + str(len(gr.edges())) + "\t: Total number of edges in the graph (pairs of sentences with some similarity)")
        #_apiLogger.info("" + str(((len(myarray))**2)/2) + " : Half the square of the number of sentences")

        if dev == 'DGF':
            # DGF: Nicolas, 'debora_results' prints to file more results that I want to see for development purposes.            
            debora_results(gr,text,ranked_global_weights,reorganised_array,number_of_words,section_names,section_labels, nf,nf2)            
            #essay, essay_id = nicolas_results(gr,ranked_global_weights,parasenttok, number_of_words,struc_feedback)
            #print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2)
            #print '\n\n', essay, '\n\n', essay_id , '\n\n'
        else: # DGF: Nicolas, 'nicolas_results' returns 'essay' ready for your 'jsonify' procedure.
            essay, essay_id = nicolas_results(gr,ranked_global_weights,parasenttok, number_of_words,struc_feedback)                    
        
        #scorestime = time() # Set current time to a variable for later calculations
            
        ###################################################
        ###################################################
        
        nf.close() # Close the essay results file
nf2.close() # Close the summary results file.


# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>

