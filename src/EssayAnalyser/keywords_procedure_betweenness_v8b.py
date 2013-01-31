"""
This program uses graph-based methods to identify the key phrases in an essay. The program processes every file in its current working directory that ends in 'txt', and puts a results file for each file processed in a newly created temporary directory. The program also generates a single summary results file that contains results information on all the files that have been processed. First it does some pre-processing: text tidy-up, word tokenisation, part-of-speech tagging, removal of punctuation, put into lower case, stop words removed. Then it builds a graph using words as nodes. In this program (unlike the sentence extraction program) the actual words are the nodes, there is no an array storing the sentences with a key. Directed edges are drawn between pairs of words/nodes (from earlier to later ones). Each pair of words/nodes is a bigram in the processed version of the text. Once the graph is built, an algorithm is applied to it to find the 'important' words. In this version, I use 'betweenness centrality'. In a different version I use PageRank. 'Important words' are those that are important with respect to the entire text. A word is important (is a key word) if it co-occurs with lots of words that co-occur with lots of words that co-occur... The scores algorithm attributes an 'importance' score to every word in the text. These are then sorted in order of descending score, and the top N words are considered to be the key words. An additional procedure takes the key words and looks for sequences of them in the original text, and these are considered to be key phrases. For the sake of comparison, the results files also include a straight frequency count and collocation measures using NLTK tools.

This program can be configured in a variety of ways. For example, this version is configured not to dismiss any parts of speech, but to use all of those that remain following removal of the stop words. Hence, for this version, it is not necessary to POS-tag the text. However, I am leaving the POS-tag procedure commented in. This version takes out all the stopwords and all the punctuation before the graph is built.
"""
import os # This is for file handling
import tempfile
import shutil
#import networkx as nx
from keywords_functions_betweenness_v8b import *



# Begin by deleting the temporary directory and files you created last time you ran this program.
tempdir0 = tempfile.gettempdir() # This gets the path to the location of the temporary files and dirs.
tempfilelist = os.listdir(tempdir0) # This gets a list of the items stored in that location
for dirname in tempfilelist:
	fullpath = os.path.join(tempdir0, dirname) # Join the path name to the dir name so you can delete the directories
	if dirname.startswith('AAA_Key-Word-Phrase_Results_'): # Only delete the temp dirs that you have created in an earlier run of this program.
		shutil.rmtree(fullpath) # Do the deletion
tempdir1 = tempfile.mkdtemp(suffix='', prefix='AAA_Key-Word-Phrase_Results_', dir=None) # Create a new directory for the essay results files to go in. Make it a temporary directory. Temporary files are stored here: c:\\users\\debora\\appdata\\local\\temp		

cwdir = os.getcwd()  # Get current working directory
filelist = os.listdir(cwdir) # Set var 'filelist' to a list of files in cwdir. 'listdir' reads the dir you've given it, and returns a list of files.
newfilename2 = os.path.join(tempdir1, 'key-word-phrase_results_summary.txt') 
nf2 = open(newfilename2, 'w') # Open 'newfilename2' (for writing to) and set open file to var 'nf2'
nf2.write('\n\n*********************************************************\n\n')
for filename in filelist: # For each file in the current directory...    
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
        nf2.write('\n') # Add a blank line to the summary results file
        
        ###################################################
        ###################################################
        # Nicolas, the principle is the same here as in the sentence extraction program.
        # The lines between the pair of hash lines call the procedure that you will want.
        # I have anticipated the arguments you will want (presumably 'keywords', 'bigram_keyphrases', 'trigram_keyphrases'). 
        # DGF: Nicolas, toggle between developer initials. My initials set to 'dev' switches on printing and writing to file. 
        dev = 'DGF'
        #dev = 'NVL'

        processed_text, wordtok_text = pre_process_essay_ke(text0,nf,nf2,dev)

        filtered_text, di,keywords, bigram_keyphrases, trigram_keyphrases = process_essay_ke(processed_text, wordtok_text, nf,nf2,dev)

        debora_results_ke(filtered_text, di,keywords,bigram_keyphrases, trigram_keyphrases,nf,nf2)    

        ###################################################
        ###################################################

        nf.close() # Close the essay file        

nf2.close()# Close the summary results file.


