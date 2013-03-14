from EssayAnalyser.se_procedure_v3 import pre_process_ass_q, pre_process_text_se,\
	process_essay_se, pre_process_struc
from EssayAnalyser.ke_all_v3 import process_essay_ke, debora_get_stats_ke, debora_write_results_ke
from EssayAnalyser.se_print_v3 import debora_get_stats_se,debora_write_results_se
from EssayAnalyser.ea_results_v3 import make_results_array


def top_level_procedure(text0,essayfilename,nf,nf2,dev):
    ass_q_long = "Write a report explaining the main accessibility challenges for disabled learners that you work with or support in your own work context(s). Use examples from your own experience, supported by the research and practice literature. If you're not a practitioner, write from the perspective of a person in a relevant context. Critically evaluate the influence of the context (e.g. country, institution, educational sector, perceived role of online learning within education) on: the identified challenges particular to your own context. the influence of legislation and local policies. the roles and responsibilities of key individuals. the role of assistive technologies in addressing these challenges."
    ass_q_short = "Write a report explaining the main accessibility challenges for disabled learners that you work with or support in your own work context(s)"

    ass_q_long = pre_process_ass_q(ass_q_long,dev)
    ass_q_short = pre_process_ass_q(ass_q_short,dev)  
    ##############################
    ##############################
    ## 1. Do required NLP pre-processing on this essay
    ##############################
    ##############################

    text,parasenttok,wordtok_text,number_of_words,refs_present = pre_process_text_se(text0,nf,nf2,dev)
    # Next line is needed instead of above line if we are using sbd sentence splitter.
    #text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,nf,nf2,model,dev)
   
    ##############################
    ##############################
    ## 2. Do required essay structure pre-processing on this essay
    ##############################
    ##############################

    text_se,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last = pre_process_struc(text,nf,nf2,dev)

    #texttime = time() # Set current time to a variable for later calculations

    ##############################
    ##############################
    ## 3. Construct the key sentence graph and do the graph analyses
    ##############################
    ##############################      
    
    gr_se,myarray_se,ranked_global_weights,reorganised_array,graphtime=process_essay_se(text_se,parasenttok,nf,nf2,dev)

    ##############################
    ##############################
    ## 4. Construct the key word graph and do the graph analyses
    ##############################
    ##############################      
    
    text_ke,gr_ke,di,myarray_ke,keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases=process_essay_ke(text_se,wordtok_text,nf,nf2,dev)


    ##############################
    ##############################
    ## 5. Get some stats to pass to Nicolas and to write to file
    ##############################
    ##############################      


    paras, rankorder,len_body,len_headings,countSentLen,countTrueSent,\
    countIntroSent,countConclSent,countAvSentLen,\
    percent_body_i,introcount,percent_body_c,conclcount,nodes,edges,edges_over_sents = \
    debora_get_stats_se(gr_se,text_se,headings,ranked_global_weights,reorganised_array)        

    scoresNfreqs,fivemostfreq,avfreqsum,kls_in_ass_q_long,sum_kls_in_ass_q_long,\
    kls_in_ass_q_short,sum_kls_in_ass_q_short,\
    bigrams_in_intro1,bigrams_in_intro2,\
    bigrams_in_concl1,bigrams_in_concl2,\
    all_bigrams,topbetscore =\
    debora_get_stats_ke(text_se,gr_ke,di,myarray_ke,keylemmas,keywords,\
                        bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                        ass_q_long,ass_q_short)


    ##############################
    ##############################
    ## 6. Write to file whichever results you choose
    ##############################
    ##############################      

    if dev == 'DGF':
        # Write the key sentence results to file
        #paras,len_body,len_headings,countTrueSent,countAvSentLen,countIntroSent,introcount,conclcount,percent_body_i,countConclSent,percent_body_c,nodes,edges,edges_over_sents =\
        debora_write_results_se(essayfilename,paras,rankorder,number_of_words,\
            section_names,section_labels,headings,\
            conclheaded,c_first,c_last,introheaded,i_first,i_last,\
            ranked_global_weights,reorganised_array,introcount,conclcount,\
                len_body,len_headings,countTrueSent,countSentLen,countAvSentLen,\
            countIntroSent,percent_body_i,\
            countConclSent,percent_body_c,\
            nodes,edges,edges_over_sents,nf,nf2)
        # Write the key lemma/word results to file
        debora_write_results_ke(text_ke,text_se,gr_ke,di,myarray_ke,\
                     keylemmas,keywords,fivemostfreq,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                     ass_q_long,ass_q_short,\
                     scoresNfreqs,avfreqsum,\
                     kls_in_ass_q_long,sum_kls_in_ass_q_long,\
                     kls_in_ass_q_short,sum_kls_in_ass_q_short,\
                     bigrams_in_intro1,bigrams_in_intro2,\
                     bigrams_in_concl1,bigrams_in_concl2,\
                     all_bigrams,topbetscore,nf,nf2)


        # Have a look at Nicolas's potential results
    essay = make_results_array(parasenttok,myarray_ke,number_of_words,paras,len_body,len_headings,countTrueSent,countAvSentLen,\
                                   introheaded,i_first,i_last,introcount,countIntroSent,percent_body_i,\
                                   conclheaded,c_first,c_last,conclcount,countConclSent,percent_body_c,refs_present,\
                                   ranked_global_weights,nodes,edges,edges_over_sents,\
                                   keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                                   scoresNfreqs,fivemostfreq,avfreqsum,\
                                   kls_in_ass_q_long,sum_kls_in_ass_q_long,\
                                   kls_in_ass_q_short,sum_kls_in_ass_q_short,\
                                   all_bigrams)
        #nx.write_weighted_edgelist(gr, fullpath, comments="#", delimiter=' ', encoding='utf-8') # This writes edge list to temp dir instead of to cwd
        #print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2)
        #print '\n\n', essay, '\n\n', essay_id , '\n\n'
        
        # DGF: Retursn 'essay' ready for your 'jsonify' procedure, as it was a few months ago.
        # The difference between text_se and text_ke is that text_se has paragraph+sentence structure, but text_ke does not, it has been removed.
        # Sorry, but I haven't had the time to do the derived graph with a smaller set of nodes, but I will do it soon.

    print '\n\nThis is essay[ke_stats][bigram_keyphrases]\n'
    print essay['ke_data']
    print essay['ke_stats']

    return essay    
    #scorestime = time() # Set current time to a variable for later calculations
        
    ###################################################
    ###################################################
