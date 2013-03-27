import os # This is for file handling
import shutil
import codecs

from EssayAnalyser.se_procedure_v3 import pre_process_shorttext, pre_process_text,\
	pre_process_struc, process_essay_se
from EssayAnalyser.ke_all_v3 import process_essay_ke, get_essay_stats_ke, debora_write_results_ke
from EssayAnalyser.se_print_v3 import get_essay_stats_se, debora_write_results_se
from EssayAnalyser.ea_results_v3 import make_results_array

##############################
##############################
## 1. Read in assignment question and text book index.
##############################
##############################
      
#cwdir = os.getcwd() # get current working directory
#cwdir = os.path.abspath(os.path.dirname(__file__))
#assignment_question = cwdir + '\\assignment_extras\\H810_TMA01_ass_q_long.txt'
#f = codecs.open(assignment_question,'r',encoding='utf-8') # Open for reading the assignment question
#ass_q_txt = f.read() # Read in the assignment question and set to var 'ass_q_txt'
#print '\n\nThis is ass_q_long_string', ass_q_long_string
#f.close() # Close the file
#tb_index = cwdir + '\\assignment_extras\\H810_TMA01_seale_textbook_index.txt'
#f = codecs.open(tb_index,'r',encoding='utf-8') # Open for reading the text book index
#tb_index_txt = f.read() # Read in the text book index
#f.close() # Close the file


def getAssignmentData(module,assignment):
    # get path of current file
    cwdir = os.path.abspath(os.path.dirname(__file__))
    # build path to data file
    assignment_question = os.path.join(cwdir,'..\\data\\',module + '_' + assignment + '_ass_q_long.txt')
    assignment_question = os.path.normpath(assignment_question)
    f = codecs.open(assignment_question,'r',encoding='utf-8') # Open for reading the assignment question
    ass_q_txt = f.read() # Read in the assignment question and set to var 'ass_q_txt'
    f.close() # Close the file
 
    tb_index = os.path.join(cwdir,'..\\data\\',module + '_textbook_index.txt')
    f = codecs.open(tb_index,'r',encoding='utf-8') # Open for reading the text book index
    tb_index_txt = f.read() # Read in the text book index
    f.close() # Close the file

    return ass_q_txt, tb_index_txt

def top_level_procedure(essay_txt,essay_fname,nf,nf2,dev,module,assignment):
    
    # Get the data associated with module/course
    ass_q_txt, tb_index_txt = getAssignmentData(module,assignment)
    
##    ass_q_long = "Write a report explaining the main accessibility challenges for disabled learners that you work with or support in your own work context(s). Use examples from your own experience, supported by the research and practice literature. If you're not a practitioner, write from the perspective of a person in a relevant context. Critically evaluate the influence of the context (e.g. country, institution, educational sector, perceived role of online learning within education) on: the identified challenges particular to your own context. the influence of legislation and local policies. the roles and responsibilities of key individuals. the role of assistive technologies in addressing these challenges."
##    ass_q_short = "Write a report explaining the main accessibility challenges for disabled learners that you work with or support in your own work context(s)"
##
##    ass_q_long = pre_process_ass_q(ass_q_long,dev)
##    ass_q_short = pre_process_ass_q(ass_q_short,dev)
    ass_q_long_words, ass_q_long_lemmd, ass_q_long_lemmd2,ass_q_short_lemmd = pre_process_shorttext(ass_q_txt,'NOPRINT')

    # Note there are two versions of the text book index. First, the original text file 'H810_TMA01_seale_textbook_index.txt'
    # as copied and pasted from the internet version of the book. That text file is used as input to function 'pre_process_shorttext'
    # to create a list of text book lemmas which is then used in a comparison with the essay's key lemmas.
    # The second file 'H810_TMA01_textbook_seale_index.py' has been pre-processed prior to run-time to derive a text book index
    # that has had a few stop words removed, but not all the stop words that get removed by EssayAnalyser.
    # This distinction is critically important. We must not use EssayAnalyser to produce
    # the text book index that we use to decide which stop words should and should not be used by EssayAnalyser.
    a1,tb_index_lemmd, tb_index_lemmd2,a2 = pre_process_shorttext(tb_index_txt,'NOPRINT') # a1 and a2 are dummies. We don't want to create an index using the same process (the same stop words) as we use for the essays and assignment question. We also don't want the first sentence only of the index.

    #print '\n\nThis is ass_q_long_words', ass_q_long_words
    #print '\n\nThis is ass_q_long_lemmd2', ass_q_long_lemmd2

    #print '\n\nThis is tb_index_lemmd', tb_index_lemmd
    #print '\n\nThis is tb_index_lemmd2', tb_index_lemmd2
  

    ##############################
    ##############################
    ## 1. Do required NLP pre-processing on this essay
    ##############################
    ##############################

    #text,parasenttok,wordtok_text,number_of_words,refs_present = pre_process_text_se(essay_txt,nf,nf2,dev)
    text,parasenttok,wordtok_text,b_last,len_refs,refsheaded,late_wc,appendixheaded = pre_process_text(essay_txt,nf,nf2,dev)
    # Next line is needed instead of above line if we are using sbd sentence splitter.
    #text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(essay_txt,nf,nf2,model,dev)
   
    ##############################
    ##############################
    ## 2. Do required essay structure pre-processing on this essay
    ##############################
    ##############################

    text_se,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,number_of_words = \
    pre_process_struc(text,ass_q_long_words,nf,nf2,dev)

    #texttime = time() # Set current time to a variable for later calculations

    ##############################
    ##############################
    ## 3. Construct the key sentence graph and do the graph analyses
    ##############################
    ##############################      
    
    gr_se,ranked_global_weights,reorganised_array,graphtime = \
    process_essay_se(text_se,parasenttok,nf,nf2,dev)

    ##############################
    ##############################
    ## 4. Construct the key word graph and do the graph analyses
    ##############################
    ##############################      
    
    text_ke,gr_ke,di,myarray_ke,keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,threshold_ke = \
    process_essay_ke(text_se,wordtok_text,nf,nf2,dev)


    ##############################
    ##############################
    ## 5. Get some stats to pass to Nicolas and to write to file
    ##############################
    ##############################      


    paras, rankorder,len_body,len_headings,countSentLen,countTrueSent,countAvSentLen,\
    countIntroSent,countConclSent,countAssQSent,countTitleSent,\
    percent_body_i,i_toprank,percent_body_c,c_toprank,nodes,edges,edges_over_sents = \
    get_essay_stats_se(gr_se,text_se,headings,ranked_global_weights,reorganised_array)        

    scoresNfreqs,fivemostfreq,avfreqsum,\
    uls_in_ass_q_long,kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
    kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
    kls_in_tb_index, sum_freq_kls_in_tb_index,\
    bigrams_in_intro1,bigrams_in_intro2,\
    bigrams_in_concl1,bigrams_in_concl2,\
    bigrams_in_assq1,bigrams_in_assq2,\
    all_bigrams,topbetscore =\
    get_essay_stats_ke(text_se,gr_ke,di,myarray_ke,keylemmas,keywords,\
                        bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                        ass_q_long_words, ass_q_long_lemmd, ass_q_long_lemmd2,ass_q_short_lemmd,\
                        tb_index_lemmd, tb_index_lemmd2)
                        #ass_q_long,ass_q_short)


    ##############################
    ##############################
    ## 6. Write to file whichever results you choose
    ##############################
    ##############################      

    if dev == 'DGF':
        # Write the key sentence results to file
        #paras,len_body,len_headings,countTrueSent,countAvSentLen,countIntroSent,i_toprank,c_toprank,percent_body_i,countConclSent,percent_body_c,nodes,edges,edges_over_sents =\
        debora_write_results_se(essay_fname,\
            paras,rankorder,number_of_words,\
            countTrueSent,countSentLen,countAvSentLen,\
            nodes,edges,edges_over_sents,\
            ranked_global_weights,reorganised_array,\
            section_names,section_labels,headings,len_headings,\
            countAssQSent,countTitleSent,
            b_last,len_body,len_refs,refsheaded,late_wc,appendixheaded,\
            introheaded,i_first,i_last,i_toprank,countIntroSent,percent_body_i,\
            conclheaded,c_first,c_last,c_toprank,countConclSent,percent_body_c,\
            nf,nf2)
        # Write the key lemma/word results to file
        debora_write_results_ke(text_ke,text_se,gr_ke,di,myarray_ke,threshold_ke,\
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

        # Have a look at Nicolas's potential results
    essay = make_results_array(parasenttok,myarray_ke,\
                               paras,number_of_words,
                               countTrueSent,countAvSentLen,\
                               nodes,edges,edges_over_sents,\
                               ranked_global_weights,reorganised_array,threshold_ke,\
                               len_headings,\
                               countAssQSent,countTitleSent,\
                               b_last,len_body,len_refs,refsheaded,late_wc,appendixheaded,\
                               introheaded,i_first,i_last,i_toprank,countIntroSent,percent_body_i,\
                               conclheaded,c_first,c_last,c_toprank,countConclSent,percent_body_c,\
                               keylemmas,keywords,fivemostfreq,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                               scoresNfreqs,avfreqsum,\
                               kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
                               kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
                               kls_in_tb_index, sum_freq_kls_in_tb_index,
                               all_bigrams)
        #nx.write_weighted_edgelist(gr, fullpath, comments="#", delimiter=' ', encoding='utf-8') # This writes edge list to temp dir instead of to cwd
        #print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2)
        #print '\n\n', essay, '\n\n', essay_id , '\n\n'

    #print '\n\nThis is essay[ke_stats][bigram_keyphrases]\n'
    #print essay['ke_data']
    #print essay['ke_stats']

    return essay    
    #scorestime = time() # Set current time to a variable for later calculations
        
    ###################################################
    ###################################################
