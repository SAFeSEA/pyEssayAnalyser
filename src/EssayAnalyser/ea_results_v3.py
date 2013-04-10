'''
@todo OrderedDict does not exist in Python 2.6, running on Linux.
An alternative needs to be installed manually: https://pypi.python.org/pypi/ordereddict
Or switch back to standard Dict.
'''
## @todo: Added for backward compatibility with Python 2.6 (linux)
import sys
if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
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
3.1.0    Added mashup of parasenttok (se_parasenttok) to contains all info (id, text, toprank, tag, raking)
'''
ANALYTICS_VERSION = "3.1.0"

def make_results_array(parasenttok,myarray_ke,\
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
                               kls_in_tb_index, sum_freq_kls_in_tb_index,\
                               all_bigrams):
    """
    Return the result of the text & sentence analytics
    @return: A dictionary containing various elements of the text analytics
    """
    essay = OrderedDict()
    
    '''
    @todo: What limit should we implement for the top ranked sentence? Hard-coded? Threshold-based? Parameter to process?
    '''
    top_ranked_global_weights = ranked_global_weights[:15]  

    # Index sentence ID by rank
    mylist2 = {}
    for idx,val in enumerate(top_ranked_global_weights): 
        mylist2[val[1]]=idx         
    
    # Restructure parasenttok with text,ID, structure tag (and score?)
    reorpar = []
    inc=0
    for par in parasenttok:
        newpar = []
        for sent in par:
            newsent = {
                'text': sent,                       ## sentence text
                'id':inc,                           ## sentence ID
                'tag': reorganised_array[inc][2]    ## structural tag
            }
            if inc in mylist2:
                newsent['rank'] = mylist2[inc]      ## rank if in top 15
            newpar.append(newsent)
            inc+=1
        reorpar.append(newpar)

    ### Add version of data structure 
    essay['version'] = ANALYTICS_VERSION
        
    ### Add paragraph/sentence structure
    essay['parasenttok'] = parasenttok    

    ### Add data on sentences 
    se_data = OrderedDict()
    mylist2 = []
    for (a,b,c,d,e) in top_ranked_global_weights:
        mylist2.append((a,b,c))        
    se_data['se_ranked'] = mylist2
    se_data['se_parasenttok'] = reorpar
    essay['se_data'] = se_data
   
            
    ### Add statistics on essay
    se_stats = OrderedDict()
    se_stats['paras'] = paras
    se_stats['len_body'] = len_body
    se_stats['len_headings'] = len_headings
    se_stats['all_sents'] =  sum(w for w in [len(x) for x in parasenttok])
    se_stats['countTrueSent'] = countTrueSent
    se_stats['number_of_words'] = number_of_words
    se_stats['countAvSentLen'] = countAvSentLen
    se_stats['countAssQSent'] = countAssQSent # new
    se_stats['countTitleSent'] = countTitleSent # new
    essay['se_stats'] = se_stats

    se_graph = OrderedDict()
    se_graph['nodes'] = nodes
    se_graph['edges'] = edges
    se_graph['edges_over_sents'] = edges_over_sents
    essay['se_graph'] = se_graph


    body = OrderedDict()
    body['late_wc'] = late_wc # new    
    body['b_last'] = b_last # new
    essay['body'] = body
    
    ### Add section feedback
    intro = OrderedDict()
    intro['introheaded'] = introheaded
    intro['i_first'] = i_first
    intro['i_last'] = i_last
    intro['countIntroSent'] = countIntroSent
    intro['percent_body_i'] = percent_body_i
    intro['i_toprank'] = i_toprank # var name changed
    essay['intro'] = intro

    concl = OrderedDict()
    concl['conclheaded'] = conclheaded
    concl['c_first'] = c_first
    concl['c_last'] = c_last
    concl['countConclSent'] = countConclSent
    concl['percent_body_c'] = percent_body_c
    concl['c_toprank'] = c_toprank # var name changed
    essay['concl'] = concl

    refs = OrderedDict()
    refs['len_refs'] = len_refs # new
    refs['refsheaded'] = refsheaded # var name changed
    essay['refs'] = refs

    appendix = OrderedDict()
    appendix['appendixheaded'] = appendixheaded # new
    essay['appendix'] = appendix
    
    ke_data = OrderedDict()
    ke_data['myarray_ke'] = myarray_ke
    ke_data['fivemostfreq'] = fivemostfreq
    ke_data['keylemmas'] = keylemmas
    ke_data['threshold_ke'] = threshold_ke # new    
    ke_data['keywords'] = keywords
    ke_data['all_bigrams'] = all_bigrams
    ke_data['bigram_keyphrases'] = bigram_keyphrases
    ke_data['trigram_keyphrases'] = trigram_keyphrases
    ke_data['quadgram_keyphrases'] = quadgram_keyphrases
    ke_data['kls_in_ass_q_long'] = kls_in_ass_q_long
    ke_data['kls_in_ass_q_short'] = kls_in_ass_q_short
    ke_data['kls_in_tb_index'] = kls_in_tb_index # new
    ke_data['scoresNfreqs'] = scoresNfreqs
    essay['ke_data'] = ke_data

    ke_stats = OrderedDict()
    ke_stats['avfreqsum'] = avfreqsum
    ke_stats['sum_freq_kls_in_ass_q_long'] = sum_freq_kls_in_ass_q_long # var name changed
    ke_stats['sum_freq_kls_in_ass_q_short'] = sum_freq_kls_in_ass_q_short # var name changed
    ke_stats['sum_freq_kls_in_tb_index'] = sum_freq_kls_in_tb_index   # new
    essay['ke_stats'] = ke_stats
    
    #print '\n\nThis is essay[ke_stats][bigram_keyphrases]\n'
    #print essay['ke_data']
    #print essay['ke_stats']
    #print essay['struc_feedback']
    #print essay['ranked']
    
    #pprint.pprint(essay)
    return essay
