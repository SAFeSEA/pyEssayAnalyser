from __future__ import division # This enables Python to use floating point division (otherwise division of smaller integer by greater = 0)
from time import time # For calculating processing times
import os # This is for file handling
import tempfile
import shutil
#import networkx as nx  # Leave this in. For testing.
#import sbd # This is an alternative sentence splitter
#import profile # For running the Python profiler to see which functions are hogging the time
####from se_procedure_v3 import *
####from ke_all_v3 import *
####import codecs



from EssayAnalyser.se_procedure_v3 import pre_process_ass_q, pre_process_text_se,\
	process_essay_se, pre_process_struc
from EssayAnalyser.ke_all_v3 import process_essay_ke, debora_results_ke
from EssayAnalyser.se_print_v3 import debora_results_se, nicolas_results_se

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

##############################
##############################
## 1. Do required NLP pre-processing on assignment question.
##############################
##############################
ass_q_long = "Write a report explaining the main accessibility challenges for disabled learners that you work with or support in your own work context(s). Use examples from your own experience, supported by the research and practice literature. If you're not a practitioner, write from the perspective of a person in a relevant context. Critically evaluate the influence of the context (e.g. country, institution, educational sector, perceived role of online learning within education) on: the identified challenges particular to your own context. the influence of legislation and local policies. the roles and responsibilities of key individuals. the role of assistive technologies in addressing these challenges."
ass_q_short = "Write a report explaining the main accessibility challenges for disabled learners that you work with or support in your own work context(s)"

ass_q_long = pre_process_ass_q(ass_q_long,dev)
ass_q_short = pre_process_ass_q(ass_q_short,dev)        

##############################
##############################
## 2. Do some file handling for all the essays to be read in and the results files to be written out.
##############################
##############################

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
#nf2.write('\nProgram started running at: ') # Write to summary results file 'nf2' the start time of the program
#nf2.write(str(startprogtime))
#nf2.write('\n\n*********************************************************\n\n')
#endimporttime = time() # Set current time to a variable for later calculations

for filename in filelist: # For each file in the current directory...
    #startfiletime = time() # Set current time to a variable for later calculations
    if filename[-3:] == 'txt': # If a file name ends in 'txt'...
        print filename # Print to shell to monitor progress
        f = open(filename, 'r') # Open current essay file for reading
        text0 = f.read() # Read in the essay and set to var 'text0'
        f.close() # Close the essay file
        string = filename[:-4] + '_results' + '.txt'
        newfilename = os.path.join(tempdir1, string)                     
        nf = open(newfilename, 'w') # Open 'newfilename' (for writing to) and set open file to var 'nf'

        # DGF: Nicolas, hopefully you should be able to just lift everything between here and the next double row of hashes
        # and substitute it for your two functions 'get_segmented_text' and 'process_essay' in your 'api.py' file.
        

        if dev == 'DGF':
            #nf2.write('\n') # Add blank lines to the essay results file            
            nf2.write(str(filename)) # Write the new file name to the essay results file
            nf2.write('; ')
            
        #struc_feedback = {}
        
        # DGF: Nicolas, merging the key sentence and key lemma/word work has meant I have had to split essay pre-processing into two procedures.
        ##############################
        ##############################
        ## 3. Do required NLP pre-processing on this essay
        ##############################
        ##############################

        text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,nf,nf2,dev)
        # Next line is needed instead of above line if we are using sbd sentence splitter.
        #text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,nf,nf2,model,dev)
       
        ##############################
        ##############################
        ## 4. Do required essay structure pre-processing on this essay
        ##############################
        ##############################

        text_se,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last = pre_process_struc(text,nf,nf2,dev)

        #texttime = time() # Set current time to a variable for later calculations

        ##############################
        ##############################
        ## 5. Construct the key sentence graph and do the graph analyses
        ##############################
        ##############################      
        
        gr_se,myarray_se,ranked_global_weights,reorganised_array,graphtime=process_essay_se(text_se,parasenttok,nf,nf2,dev)

        ##############################
        ##############################
        ## 6. Construct the key word graph and do the graph analyses
        ##############################
        ##############################      
        
        text_ke,gr_ke,di,myarray_ke,keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases=process_essay_ke(text_se,wordtok_text,nf,nf2,dev)

        ##############################
        ##############################
        ## 7. Write to file whichever results you choose
        ##############################
        ##############################      

        if dev == 'DGF':
            # Write the key sentence results to file
            debora_results_se(gr_se,text_se,ranked_global_weights,reorganised_array,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,filename, nf,nf2,dev)            
            # Write the key lemma/word results to file
            debora_results_ke(text_ke,text_se,gr_ke,di,myarray_ke,keylemmas,keywords,bigram_keyphrases, trigram_keyphrases,quadgram_keyphrases,ass_q_long,ass_q_short,nf,nf2,dev)    
            # Have a look at Nicolas's potential results
            essay, essay_id = nicolas_results_se(gr_se,ranked_global_weights,parasenttok, number_of_words,struc_feedback)
            #nx.write_weighted_edgelist(gr, fullpath, comments="#", delimiter=' ', encoding='utf-8') # This writes edge list to temp dir instead of to cwd
            #print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2)
            #print '\n\n', essay, '\n\n', essay_id , '\n\n'
            
            # DGF: Nicolas, 'nicolas_results' returns 'essay' ready for your 'jsonify' procedure, as it was a few months ago.
            # I expect you will want to add some additional arguments from above. I have tried to make the arguments clear by their names. Let me know if you are not sure which ones you need.
            # Also if you want any arguments that are not there, let me know.
            # The difference between text_se and text_ke is that text_se has paragraph+sentence structure, but text_ke does not, it has been removed.
            # Sorry, but I haven't had the time to do the derived graph with a smaller set of nodes, but I will do it soon.
            # As before, I have not written a function to process the key lemma/word results as you want them.
            # The arguments you want for the key lemma/word work are in 6. above. 
        else: 
            #True    
            essay, essay_id = nicolas_results_se(gr_se,ranked_global_weights,parasenttok, number_of_words,struc_feedback)                    
        
        #scorestime = time() # Set current time to a variable for later calculations
            
        ###################################################
        ###################################################
        
        nf.close() # Close the essay results file
nf2.close() # Close the summary results file.

#main()
#profile.run('main(); print') #  Swap these two lines if you want to profile this program (see how many times functions are called, etc. NB profiler runs slowly.)

# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>

