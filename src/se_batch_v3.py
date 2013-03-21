from __future__ import division # This enables Python to use floating point division (otherwise division of smaller integer by greater = 0)
from time import time # For calculating processing times
import os # This is for file handling
import tempfile
import shutil
import codecs
from EssayAnalyser.se_main_v3 import top_level_procedure
#import networkx as nx  # Leave this in. For testing.
#import sbd # This is an alternative sentence splitter
#import profile # For running the Python profiler to see which functions are hogging the time

startprogtime = time() # Set current time to a variable for later calculations


"""
This is the top-level script for a program which implements a version of the TextRank algorithm for extractive summaries (based on sentence extraction) and key word/phrase extraction from (Mihalcea and Tarau, 2005, 2004). Ibid uses the PageRank algorithm (Brin and Page 1998) and applies it to the extraction of key sentences, words, and phrases from a text (extractive summarisation). This program follows ibid's basic design, but with some differences. This file-handling script processes every file in its current working directory that ends in 'txt', and puts a results file for each file processed in a newly created temporary directory. A single summary results file is also generated that contains results information on all the files that have been processed. The program is split over seven different files: se_main.py, se_procedure.py, se_preprocess.py, se_struc.py, se_graph.py, se_print.py, and ke_all.py. For each file ending in 'txt', the program does the following. It assumes the file has been saved in Latin9 encoding. First it does some pre-processing: latin9 tidy-up, paragraph, sentence, and then word tokenisation, removal of punctuation. Then structural parts are identified and each sentence is labelled with its structural function in the essay. Then some more NLP pre-processing is done: POS-tagging, lowercasing, removal of stop words, lemmatisation. Then the program performs two independent analyses using the same pre-processed text. 
First it does extractive summarisation through sentence extraction. It builds a graph using sentences as nodes. The actual sentences are not the nodes, a Python dictionary is used to store the sentences using a key, and the key is used for the nodes. Directed edges are drawn between pairs of sentences that are similar. The similarity of a pair of sentences/nodes is represented by the weight of the edge that joins them. In this version of the program the similarity measure is cosine similarity. Edges point only from a later/greater sentence/node to an earlier one. A global weight score WSVi for each node is then calculated. The WSVi score for a node Vi represents how important the sentence Vi is compared to the whole essay. A sentence is important if it is similar to other sentences that are similar to other sentences that are similar to other sentences that are similar... Initially, an arbitrary WSVi value is set for every node in order to enable the program to work out the 'real' value. It is necessary to set arbitrary values for WSVi in the first instance because the procedure for finding a WSVi score requires you to find a WSVi score, i.e., it is recursive. So you need some values in order to be able to start. The arbitrary values move closer towards the real values at every iteration until very little difference is made by further iterations. Once the scores are derived, all the sentences with their WSVi scores are sorted according to the scores, and written to the results file. The highest-scoring sentences are those that are the most important/representative in the text.
Next the program builds a separate graph to identify the key lemmas/words and phrases in an essay. In this procedure (unlike for sentence extraction) the actual lemmas are the nodes, there is no an array storing the lemmas with a key, as with the sentence extraction procedure. Directed edges are drawn between pairs of lemmas/nodes (from earlier to later ones). Each pair of linked lemmas/nodes must co-occur within a window of N (I use N = 2) in the processed version of the text. Once the graph is built, a centrality algorithm is applied to it to find the 'important' words. In this version, I use 'betweenness centrality'. In a different version I use PageRank, a version of Eigenvector centrality. 'Important words' are those that are important with respect to the entire text. A word is important (is a key word) if it co-occurs with lots of words that co-occur with lots of words that co-occur... The centrality algorithm attributes an 'importance' score to every word in the text. These are then sorted in descending order of score. The words that are considered to be the key words are those that are in the top X per cent of words and that have a centrality score of above a certain threshold. An additional procedure takes the key words and looks for within-sentence sequences of them in the original text, and these are considered to be key phrases. 


Refs:
Brin, S. and L. Page, (1998). The Anatomy of a Large-Scale Hypertextual Web Search Engine. In Seventh International World-Wide Web Conference (WWW 1998), Brisbane, Australia, 14-18 April 1998.

R. Mihalcea and P. Tarau (2004). Textrank: Bringing order into texts. In L. Dekang and W. Dekai (eds.), Proceedings of Empirical Methods in Natural Language Processing (EMNLP) 2004, pp. 404–-411, Association for Computational Linguistics, Barcelona, Spain, July 2004.

R. Mihalcea and P. Tarau (2005). A language independent algorithm for single and multiple document summarization. In Proceedings of the Second International Joint Conference Natural Language Processing (IJCNLP’05), Korea, pp. 602–-607, 11–-13 October 2005.
"""

#def main():


# DGF: Nicolas, toggle between developer initials. My initials set to 'dev' switches on printing and writing to file. 
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
        print essay_fname # Print to shell to monitor progress
        f = codecs.open(essay_fname, 'r',encoding='utf-8') # Open current essay file for reading
        essay_txt = f.read() # Read in the essay and set to var 'essay_txt'
        f.close() # Close the essay file
        string = essay_fname[:-4] + '_results' + '.txt'
        newfilename = os.path.join(tempdir1, string)                     
        nf = codecs.open(newfilename, 'w',encoding='utf-8') # Open 'newfilename' (for writing to) and set open file to var 'nf'

        if dev == 'DGF':
            #nf2.write('\n') # Add blank lines to the essay results file            
            nf2.write(str(essay_fname)) # Write the new file name to the essay results file
            nf2.write('; ')

        top_level_procedure(essay_txt,essay_fname,nf,nf2,dev,"H810","TMA01")            

        nf.close() # Close the essay results file
nf2.close() # Close the summary results file.

#main()
#profile.run('main(); print') #  Swap these two lines if you want to profile this program (see how many times functions are called, etc. NB profiler runs slowly.)

# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>

