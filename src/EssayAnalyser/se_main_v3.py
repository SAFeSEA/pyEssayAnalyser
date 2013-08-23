import os.path # This is for file handling
import pickle # For encoding text files as Python objects
#import shutil # For file operations
#import codecs # For encoding handling
#import tempfile # For handling OS's temporary files directories
#from time import time # For calculating processing times

from EssayAnalyser.se_procedure_v3 import pre_process_text, process_essay_se
#from EssayAnalyser.se_procedure_v3 import pre_process_text, pre_process_struc, process_essay_se    
from EssayAnalyser.ke_all_v3 import process_essay_ke, get_essay_stats_ke, debora_write_results_ke
from EssayAnalyser.se_print_v3 import get_essay_stats_se, debora_write_results_se #, print_processing_times
from EssayAnalyser.ea_results_v3 import make_results_array
from EssayAnalyser.se_graph_v3 import sample_nodes_for_figure

"""
This file contains the following functions:
def getAssignmentData(module,assignment):
def top_level_procedure(essay_txt,essay_fname,nf,nf2,dev,module,assignment)
"""

#### xxxx These are dummy assignment question extras for when I don't want to make these comparisons, typically when testing.
#### Comment these in and also comment out the call of get_assignment_data.
#### Note that openEssayist is not using the comparison of the essay with the assignment question. These are only
#### being used in the statistical analyses. They are dummy arguments in the openEssayist version of EssayAnalyser.
##ass_q_long_words = [[['#dummy#', u'write', u'report', u'explaining', u'main', u'accessibility', u'challenges', u'disabled', u'learners', u'work', u'support', u'work', u'context']]]
##
##ass_q_long_lemmd = [[[('#dummy#', 'NN'), (u'write', u'write'), (u'report', u'report'), (u'explaining', u'explain')]]]
##
##ass_q_long_lemmd2 = [[[u'write', u'report', u'explain', u'main', u'accessibility', u'challenge', u'disable']]]
##
##ass_q_short_lemmd = [[[('#dummy#', 'NN'), (u'write', u'write'), (u'report', u'report'), (u'explaining', u'explain')]]]
##
##tb_index_lemmd = [[[('#dummy#', 'NN'), (u'seale', u'seale'), (u'index', u'index')]]]
##
##tb_index_lemmd2 = [[[u'seale', u'index']], [[]], [[u'academic', u'freedom']], [[u'access', u'board', u'u']]]
##

##############################
##############################
## 0. Read in assignment question and text book index pre-processed files.
##############################
##############################     

def getAssignmentData(module,assignment):
    # get path of current file
    cwdir = os.path.abspath(os.path.dirname(__file__))
    # build path to data file
    
    ass_q_long_w = os.path.join(cwdir,'..' + os.sep + 'data'+ os.sep,module + '_' + assignment + '_ass_q_long_w.txt')
    ass_q_long_w = os.path.normpath(ass_q_long_w)
    f = pickle.load(open(ass_q_long_w,'rb')) # Open for reading and unpickle the assignment question long version
    ass_q_long_words = f # which is stored in 'data' dir in the same dir as 'se_batch.py'

    ass_q_long_le = os.path.join(cwdir,'..' + os.sep + 'data'+ os.sep,module + '_' + assignment + '_ass_q_long_le.txt')
    f = pickle.load(open(ass_q_long_le,'rb')) 
    ass_q_long_lemmd = f 

    ass_q_long_le2 = os.path.join(cwdir,'..' + os.sep + 'data'+ os.sep,module + '_' + assignment + '_ass_q_long_le2.txt')
    f = pickle.load(open(ass_q_long_le2,'rb')) 
    ass_q_long_lemmd2 = f 

    ass_q_short_le = os.path.join(cwdir,'..' + os.sep + 'data'+ os.sep,module + '_' + assignment + '_ass_q_short_le.txt')
    f = pickle.load(open(ass_q_short_le,'rb')) 
    ass_q_short_lemmd = f 

    tb_index_le = os.path.join(cwdir,'..' + os.sep + 'data'+ os.sep,module + '_' + assignment + '_tb_index_le.txt')
    f = pickle.load(open(tb_index_le,'rb')) 
    tb_index_lemmd = f 

    tb_index_le2 = os.path.join(cwdir,'..' + os.sep + 'data'+ os.sep,module + '_' + assignment + '_tb_index_le2.txt')
    f = pickle.load(open(tb_index_le2,'rb')) 
    tb_index_lemmd2 = f 

    #return ass_q_txt, tb_index_txt
    return ass_q_long_words, ass_q_long_lemmd, ass_q_long_lemmd2,ass_q_short_lemmd,tb_index_lemmd, tb_index_lemmd2

def top_level_procedure(essay_txt,essay_fname,nf,nf2,dev,module,assignment):
    #startassdatatime = time()

    ##############################
    ##############################
    ## 0. Prepare the assignment/module data associated with this essay
    ##############################
    ##############################

    # xxxx the line below needs commenting out if you want to use small dummy data for the assignment question extras comparisons to speed up testing.
    ass_q_long_words, ass_q_long_lemmd, ass_q_long_lemmd2,ass_q_short_lemmd,tb_index_lemmd, tb_index_lemmd2 = \
                      getAssignmentData(module,assignment)

    #getassdatatime = time()
    #processasstexttime = time() # This is obselete now, because processing has been done beforehand
    #processtbindextime = time() # This is obselete now, because processing has been done beforehand

    ##############################
    ##############################
    ## 1. Do required NLP pre-processing and structure analysis on this essay
    ##############################
    ##############################


    #startfiletime = time() # Set current time to a variable for later calculations   
    text_se,parasenttok,wordtok,b_last,\
    len_refs,refsheaded,late_wc,appendixheaded,\
    section_names,section_labels,headings,\
    conclheaded,c_first,c_last,introheaded,i_first,i_last,number_of_words =\
    pre_process_text(essay_txt,ass_q_long_words,nf,nf2,dev)


    # Next line is needed instead of above line if we are using sbd sentence splitter. xxxx now needs updating
    #text,parasenttok,wordtok,number_of_words,struc_feedback = pre_process_text_se(essay_txt,nf,nf2,model,dev)

    #texttime = time() # Set current time to a variable for later calculations
    #structime = time() # Set current time to a variable for later calculations

    ##############################
    ##############################
    ## 2. Construct the key sentence graph and do the graph analyses
    ##############################
    ##############################      

    #gr_se,ranked_global_weights,reorganised_array,graphtime = \
    gr_se,ranked_global_weights,reorganised_array\
    = process_essay_se(text_se,parasenttok,section_labels,nf,nf2,dev)

    #se_scorestime = time() # Set current time to a variable for later calculations


    ##############################
    ##############################
    ## 3. Construct the key word graph and do the graph analyses
    ##############################
    ##############################      
    
    text_ke,gr_ke,di,myarray_ke,keylemmas,keywords,\
    bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,threshold_ke\
    = process_essay_ke(text_se,wordtok,nf,nf2,dev)

    #ke_scorestime = time() # Set current time to a variable for later calculations

    ##############################
    ##############################
    ## 4. Get some stats for passing to ea_results/openEssayist and for writing to file
    ##############################
    ##############################      

    paras,rankorder,countProseSents,countProseChars,len_headings,\
    countSentLen,truesents,countTrueSent,countTrueSentChars,countFalseSent,\
    countAvSentLen,countIntroSent,countIntroChars,countConclSent,\
    countConclChars,countAssQSent,\
    countTableEnt,countListItem,\
    countTitleSent,percent_body_i,i_toprank,percent_body_c,\
    c_toprank,nodes,edges,edges_over_sents\
    = get_essay_stats_se(gr_se,text_se,headings,ranked_global_weights,reorganised_array)
    
    scoresNfreqs,fivemostfreq,avfreqsum,\
    uls_in_ass_q_long,kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
    kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
    kls_in_tb_index, sum_freq_kls_in_tb_index,\
    bigrams_in_intro1,bigrams_in_intro2,\
    bigrams_in_concl1,bigrams_in_concl2,\
    bigrams_in_assq1,bigrams_in_assq2,\
    all_bigrams,topbetscore\
    =get_essay_stats_ke(text_se,gr_ke,di,myarray_ke,keylemmas,keywords,\
                        bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                        ass_q_long_words, ass_q_long_lemmd, ass_q_long_lemmd2,ass_q_short_lemmd,\
                        tb_index_lemmd, tb_index_lemmd2)
                        #ass_q_long,ass_q_short) 
    ##############################
    ##############################
    ## 5. Derive some SE and KE subgraphs for passing to ea_results/openEssayist
    ##############################
    ##############################      

    #print '\nSE sample graph start'
    gr_se_sample = sample_nodes_for_figure(gr_se,truesents,'se') # Get a sample of the nodes from the sentence graph to make a figure with later
    #print '\nSE sample graph'
    #print(gr_se_sample.adj)    # This is how you print a networkx graph

    #print '\nKE sample graph start'
    gr_ke_sample = sample_nodes_for_figure(gr_ke,keylemmas, 'ke') # Get a sample of the nodes from the sentence graph to make a figure with later
    #print '\nKE sample graph'
    #print(gr_ke_sample.adj)    # This is how you print a networkx graph


    ##############################
    ##############################
    ## 6. Write to file whichever results are wanted for essay characterisitcs development scrutiny
    ##############################
    ##############################      

    if dev == 'DGF':
        # Write the key sentence results to file
        #paras,prose_paras,len_headings,countTrueSent,countAvSentLen,countIntroSent,i_toprank,c_toprank,percent_body_i,countConclSent,percent_body_c,nodes,edges,edges_over_sents =\
        debora_write_results_se(essay_fname,\
            paras,rankorder,number_of_words,\
            countTrueSent,countTrueSentChars,\
            countFalseSent,countSentLen,countAvSentLen,\
            nodes,edges,edges_over_sents,\
            ranked_global_weights,reorganised_array,\
            section_names,section_labels,headings,len_headings,\
            countAssQSent,countTitleSent,\
            countTableEnt,countListItem,\
            b_last,countProseSents,countProseChars,len_refs,refsheaded,late_wc,appendixheaded,\
            introheaded,i_first,i_last,i_toprank,countIntroSent,countIntroChars,percent_body_i,\
            conclheaded,c_first,c_last,c_toprank,
            countConclSent,countConclChars,percent_body_c,\
            nf,nf2)
        # Write the key lemma/word results to file
        debora_write_results_ke(text_ke,text_se,gr_ke,di,edges_over_sents,myarray_ke,threshold_ke,\
                     keylemmas,keywords,fivemostfreq,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                     scoresNfreqs,avfreqsum,\
                     uls_in_ass_q_long,kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
                     kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
                     kls_in_tb_index, sum_freq_kls_in_tb_index,\
                     bigrams_in_intro1,bigrams_in_intro2,\
                     bigrams_in_concl1,bigrams_in_concl2,\
                     bigrams_in_assq1,bigrams_in_assq2,\
                     all_bigrams,topbetscore,nf,nf2)
			     	 #ass_q_long,ass_q_short,\
                     #tb_index_lemmd, tb_index_lemmd2,\

##        print_processing_times(getassdatatime,processasstexttime,processtbindextime,\
##                               startassdatatime,startfiletime, texttime, structime, \
##                               se_scorestime, ke_scorestime, nf2)

    ##############################
    ##############################
    ## 8. Return sentence labelling scheme to earlier version. Temporary until TMA02 probably.
    ##############################
    ##############################
    # ranked_global_weights are by definition not headings so no need to change any of those labels.
    # ranked_global_weights: [(0.0015941317409155402, 1, '#+s#', u'Navigation o the o resource is not required as the screencast opens automatically.', [(u'navigation', u'navigation'), (u'resource', u'resource'), (u'required', u'require'), (u'screencast', u'screencast'), (u'opens', u'open'), (u'automatically', u'automatically')]), (0.0015941317409154273, 2,
    # All headings are listed in reorganised_array, so change that.
    # reorganised_array [(0.0015789473684210528, 0, '#-s:t#', u'1 rhubarb 1234 4567', [(u'rhubarb', u'rhubarb')]), (0.0015941317409155402, 1, '#+s#', 
    myheadings = ['#-s:H#', '#-s:s#', '#-s:d#', '#-s:l#', '#-s:c#','#-s:q#','#-s:e#','#-s:b#'] # Map these back to old heading label
#    mysents = ['#-s:e#','#-s:b#'] # Map these back to old sentence label. xxxx Note we have decided not to use the copied assignment questions in the openEssayist feedback.
    mylist = []
    for item in reorganised_array:
        if item[2] in myheadings:
            a = item[:2]
            b = item[3:]
            c = a+('#-s:h#',)
            d = c + b
            mylist.append(d)
##        elif item[2] in mysents:
##            a = item[:2]
##            b = item[3:]
##            c = a+('#+s#',)
##            d = c + b
##            mylist.append(d)            
        else:
            mylist.append(item)
    reorganised_array = mylist
    #print '\n\n reorganised_array', reorganised_array 

    ##############################
    ##############################
    ## 9. Make an array containing the paramaters Nicolas wants for ea_results/openEssayist and call it 'essay'
    ##############################
    ##############################
    # xxxx Note that 'countProseSents' is the old 'len_body'. I am leaving ea.py as it is for now.

    essay = make_results_array(parasenttok,myarray_ke,gr_ke_sample,\
                               paras,number_of_words,
                               countTrueSent,countAvSentLen,\
                               nodes,edges,gr_se_sample,edges_over_sents,\
                               ranked_global_weights,reorganised_array,threshold_ke,\
                               len_headings,\
                               countAssQSent,countTitleSent,\
                               b_last,countProseSents,len_refs,refsheaded,late_wc,appendixheaded,\
                               introheaded,i_first,i_last,i_toprank,countIntroSent,percent_body_i,\
                               conclheaded,c_first,c_last,c_toprank,countConclSent,percent_body_c,\
                               keylemmas,keywords,fivemostfreq,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                               scoresNfreqs,avfreqsum,\
                               kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
                               kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
                               kls_in_tb_index, sum_freq_kls_in_tb_index,
                               all_bigrams)

    #print '\n\nThis is essay[ke_stats][bigram_keyphrases]\n'
    #print essay['ke_sample_graph']
    #print essay['se_sample_graph']
    #print essay['ke_stats']
    #print '\n\n', essay
    #print '\n\n',parasenttok[:5]
    #print '\n\n',ranked_global_weights
    #print '\n\n',reorganised_array[-10:]
    


    #return essay, gr_se_sample, gr_ke_sample
    return essay
        
    ###################################################
    ###################################################

# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
