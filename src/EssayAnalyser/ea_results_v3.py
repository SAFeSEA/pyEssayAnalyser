'''

'''
from collections import OrderedDict

'''
This is to keep track of changes made in the data output of the analyser.
The version number is based on "semantic versioning" (http://semver.org/) and is constituted of three-parts:
    major version, minor version, and patch
    
Any change in the STRUCTURE of the dictionary (adding element, changing name of a key, ...)  
increases the minor version (e.g. changing from 3.1.5 to 3.2.0)
Any change in the CONTENT of the dictionary (new way of computing "countAvSentLen")
increases the patch version (e.g. changing from 3.1.5 to 3.1.6)

@change: 
3.0.0    Initial version of the data structure
'''
ANALYTICS_VERSION = "3.0.0"

def make_results_array(parasenttok,myarray_ke,number_of_words,paras,len_body,len_headings,countTrueSent,countAvSentLen,\
                                   introheaded,i_first,i_last,introcount,countIntroSent,percent_body_i,\
                                   conclheaded,c_first,c_last,conclcount,countConclSent,percent_body_c,refs_present,\
                                   ranked_global_weights,nodes,edges,edges_over_sents,\
                                   keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                                   scoresNfreqs,fivemostfreq,avfreqsum,\
                                   kls_in_ass_q_long,sum_kls_in_ass_q_long,\
                                   kls_in_ass_q_short,sum_kls_in_ass_q_short,\
                                   all_bigrams):
    """
    Return the result of the text & sentence analytics
    @return: A dictionary containing various elements of the text analytics
    """
    essay = OrderedDict()
    ### Add version of data structure 
    essay['version'] = ANALYTICS_VERSION
    
    
    ### Add paragraph/sentence structure
    essay['parasenttok'] = parasenttok    
    ### Add statistics on essay
    se_stats = OrderedDict()
    se_stats['paras'] = paras
    se_stats['len_body'] = len_body
    se_stats['len_headings'] = len_headings
    se_stats['all_sents'] =  sum(w for w in [len(x) for x in parasenttok])
    se_stats['countTrueSent'] = countTrueSent
    se_stats['number_of_words'] = number_of_words
    se_stats['countAvSentLen'] = countAvSentLen

    se_data = OrderedDict()
    mylist2 = []
    top_ranked_global_weights = ranked_global_weights[:15]    
    for (a,b,c,d,e) in top_ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        mylist2.append((a,b,c))        
    se_data['se_ranked'] = mylist2    
    essay['se_stats'] = se_stats

    se_graph = OrderedDict()
    se_graph['nodes'] = nodes
    se_graph['edges'] = edges
    se_graph['edges_over_sents'] = edges_over_sents
    essay['se_graph'] = se_graph

    refs = OrderedDict()
    refs['refs_present'] = refs_present
    essay['refs'] = refs

    ### Add section feedback
    intro = OrderedDict()
    intro['introheaded'] = introheaded
    intro['i_first'] = i_first
    intro['i_last'] = i_last
    intro['countIntroSent'] = countIntroSent
    intro['percent_body_i'] = percent_body_i
    intro['i_toprank'] = introcount
    essay['intro'] = intro

    concl = OrderedDict()
    concl['conclheaded'] = conclheaded
    concl['c_first'] = c_first
    concl['c_last'] = c_last
    concl['countConclSent'] = countConclSent
    concl['percent_body_c'] = percent_body_c
    concl['c_toprank'] = conclcount
    essay['concl'] = concl

    ke_data = OrderedDict()
    ke_data['myarray_ke'] = myarray_ke
    ke_data['fivemostfreq'] = fivemostfreq
    ke_data['keylemmas'] = keylemmas
    ke_data['keywords'] = keywords
    ke_data['all_bigrams'] = all_bigrams
    ke_data['bigram_keyphrases'] = bigram_keyphrases
    ke_data['trigram_keyphrases'] = trigram_keyphrases
    ke_data['quadgram_keyphrases'] = quadgram_keyphrases
    ke_data['kls_in_ass_q_long'] = kls_in_ass_q_long
    ke_data['kls_in_ass_q_short'] = kls_in_ass_q_short
    ke_data['scoresNfreqs'] = scoresNfreqs
    essay['ke_data'] = ke_data

    ke_stats = OrderedDict()
    ke_stats['avfreqsum'] = avfreqsum
    ke_stats['sum_kls_in_ass_q_long'] = sum_kls_in_ass_q_long
    ke_stats['sum_kls_in_ass_q_short'] = sum_kls_in_ass_q_short
    essay['ke_stats'] = ke_stats
    
    #print '\n\nThis is essay[ke_stats][bigram_keyphrases]\n'
    #print essay['ke_data']
    #print essay['ke_stats']
    #print essay['struc_feedback']
    #print essay['ranked']
    
    #pprint.pprint(essay)
    return essay
