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

from networkx.readwrite import json_graph

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

def make_results_array(parasenttok,myarray_ke,gr_ke_sample,\
                               paras,number_of_words,
                               countTrueSent,countAvSentLen,\
                               nodes,edges,gr_se_sample,edges_over_sents,\
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

    ##se_sample_graph = OrderedDict()
    ##se_sample_graph['gr_se_sample'] = gr_se_sample
    ##essay['se_sample_graph'] = se_sample_graph
    essay['se_sample_graph'] = json_graph.dumps(gr_se_sample)
    
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

    ##ke_sample_graph = OrderedDict()
    ##ke_sample_graph['gr_ke_sample'] = gr_ke_sample
    ##essay['ke_sample_graph'] = ke_sample_graph
    essay['ke_sample_graph'] = json_graph.dumps(gr_ke_sample)

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

def make_results_docs():
    essay = OrderedDict()

    essay['version'] =         u"The version of the result structure"
    essay['parasenttok'] =     u"The whole text (up to the references) tokenised for paragraphs and sentences."
    
    essay['se_data'] = {
        'se_ranked':           u"Ranked list (top 15) of sentences",
        'se_parasenttok':      u"Re-labelled parasenttok, each sentence with  attributes {text,id,tag,rank}",
        }
    
    essay['se_stats'] = {
        'paras':               u"Total number of paragraphs (includes everything that occurs before refs)",
        'len_body':            u"Total number of paragraphs minus the total number of headings",
        'len_headings':        u"Total number of headings",
        'all sents':           u"Total number of sentences (up to refs, including all headings, captions, etc.)",
        'countTrueSent':       u"Total number of true sentences (not headings, captions, title,  ass_q, toc)",
        'number_of_words':     u"Total number of words (I think this version includes every word that occurs before refs)",
        'countAvSentLen':      u"Mean average length of a tidysent",
        'countAssQSent':       u"",
        'countTitleSent':      u"",
        'countAvSentLen':      u"",
        }
    
    essay['se_graph'] = {
        'nodes':               u"Total number of nodes in the key sentence graph (not necessarily the same as 'all sents')",
        'edges':               u"Total number of edges in the key sentence graph",
        'edges_over_sents':    u"Number of edges in key sentence graph divided by number of true sentences",
        }
    
    essay['se_sample_graph'] = u""
    essay['ke_sample_graph'] = u""
    
    
    essay['body'] = {
        'late_wc':             u"",
        'b_last':              u"",
        }
    
    essay['intro'] = {
        'introheaded':         u"Boolean: Is there an introduction heading?",
        'i_first':             u"Index: First paragraph of introduction section",
        'i_last':              u"Index: Last paragraph of introduction section",
        'countIntroSent':      u"Number of sentences in the introduction",
        'percent_body_i':      u"Percentage of the essay body that constitutes introduction",
        'i_toprank':           u"Number of the top N key sentences that are in introduction section    ",
        }
    
    essay['concl'] = {
        'conclheaded':         u"Boolean: Is there a conclusion heading?",
        'c_first':             u"Index: First paragraph of conclusion section",
        'c_last':              u"Index: Last paragraph of conclusion section",
        'countConclSent':      u"Number of sentences in the conclusion",
        'percent_body_c':      u"Percentage of the essay body that constitutes conclusion",
        'c_toprank':           u"Number of the top 30 key sentences that are in conclusion section",
        }
    
    essay['refs'] = {
        'len_refs':            u"",
        'refsheaded':          u"Boolean: Is there a references section?",
        }

    essay['appendix'] = {
        'appendixheaded':      u"",
        }

    essay['ke_data'] = {
        'myarray_ke':          u"list of lemmas and their associated inflected forms ",
        'fivemostfreq':        u"List of the five most frequent lemmas",
        'keylemmas':           u"List of key lemmas",
        'threshold_ke':        u"",
        'keywords':            u"List of distinct key words  ",
        'all_bigrams':         u"List of bigrams",
        'bigram_keyphrases':   u"List of distinct bigrams",
        'trigram_keyphrases':  u"List  of distinct trigrams",
        'quadgram_keyphrases': u"List of distinct quadgrams    ",
        'kls_in_ass_q_long':   u"List of the essay's key lemmas that occur in assignment question (long version)",
        'kls_in_ass_q_short':  u"List of the essay's key lemmas occurring in assignment question (short version)",
        'kls_in_tb_index':     u"",
        'scoresNfreqs':        u"List of all the key lemmas presented like: (lemma,score,rank,frequency): ('student', 0.332893, 0, 38)",
        }
    
    essay['ke_stats'] = {
        'avfreqsum':                u"Mean average frequency of five most frequent lemmas",
        'sum_kls_in_ass_q_long':    u"Sum of the frequences of the essay's key lemmas that occur in the assignment question (long version)",
        'sum_kls_in_ass_q_short':   u"Sum of the frequences of the essay's key lemmas that occur in the assignment question (short version)",
        'sum_freq_kls_in_tb_index': u"",
        }
    
    return essay
