import networkx as nx # This is for implementing networks/graphs
#from time import time # For calculating processing times
from nltk.tag import pos_tag
from se_preprocess_v3 import parasent_tokenize, edit_text, get_essay_body, reinstate_hyphens1, reinstate_hyphens2, process_sents, word_tokenize, remove_punc_fm_sents, find_and_label_numeric_sents, count_words, lowercase_sents, remove_stops_fm_sents, get_lemmas  # File containing my own functions. This version of the functions uses cosine similarity, no edge if edge == 0, AND uses two arrays to speed up building of the graph. 
from se_struc_v3 import find_and_label_headings,find_and_label_section_sents
from se_graph_v3 import make_sentence_graph_nodes, add_sentence_graph_edges, find_sentence_graph_scores
"""
This file contains two long functions which specify the order
in which the essay text will be pre-processed, and how the results of
that will be processed so as to produce and analyse the sentence
graphs. The related procedure for the key phrase graph is not in here
but is in the file ke_all.py. This file does not contain the
functions for carrying out all the pre-processing and the sentence
graph processing. Those are in files se_preprocess.py, se_struc.py,
se_graph.py.

Functions in this file:
def pre_process_text(text0,ass_q_long_words,nf,nf2,dev):
def process_essay_se(text, parasenttok, section_labels,nf, nf2, dev):
"""

# Function: pre_process_text_se(text0,nf,nf2,dev)
# Carries out some of the text processing that is necessary
# before the graph can be constructed from the essay's sentences.
# Called by se_main.py.
def pre_process_text(text0,ass_q_long_words,nf,nf2,dev):
#_______________________________________
    #########################
    # DO SOME PRE-PROCESSING BEFORE STRUCTURE ANALYSIS
    #########################
    # EDIT TEXT
    # This makes a number of changes to the raw input text before tokenisation
    # to reduce errors by the sentence splitter and to determine how hyphens are dealt with.
    # Note this function replaces hyphens with a string of h's. Lower down the hyphens are reinstated., 
    # If hyphens are left in the text, the word tokeniser will split a hyphenated word into two words.
    # We want one single hyphenated word to be analysed as a single lemma, so we remove the hyphens before
    # word tokenisation (leaving a marker) and replace them later on.   
    text = edit_text(text0) 

    # PARAGRAPH- AND SENTENCE- TOKENISE TEXT
    text = parasent_tokenize(text)

    # GET ESSAY BODY
    # Find the body of the essay, being everything before the bibliography and/or appendices.
    # Also takes note of word count citation as potential marker of end of essay body.
    # Note at this stage the text is paragraph- and sentence- tokenised, but not word-tokenised.
    b_last,text, len_refs, refsheaded, late_wc, appendixheaded = get_essay_body(text,nf,dev)
    
    #process_sents(print_function_name, parasenttok)  # xxxx only for printing function names. Need to save Python files as .txt and run EssayAnalyser on them.
    #process_sents(print_unicode_name, parasenttok) # xxx only for printing unicode codes.

    # PUT THE HYPHENS BACK INTO PARASENTTOK TEXT AND KEEP FOR LATER (NOT WORD TOKENISED)
    # Note that 'parasenttok' preserves sentences more or less as written by essay author.
    # This var is passed on so that these sentences can be quoted back to user.
    parasenttok = process_sents(reinstate_hyphens2, text)

    # WORD-TOKENISE THE PARAGRAPH- AND SENTENCE-TOKENISED TEXT BEFORE HYPHENS PUT BACK IN          
    wordtok = word_tokenize(text)

    # PUT THE HYPHENS BACK IN
    # Preserve variable 'wordtok' to pass for later use in key word analysis.
    # Key word analysis uses a part-of-speech tagger that
    # uses _all_ the tokens to help decisions about parts of speech.
    # So keep 'wordtok' for later as is before punctuation removed.
    wordtok = process_sents(reinstate_hyphens1, wordtok)

    # REMOVE PUNCTUATION
    # Note that this also labels sentences that only contain punctuation as '#-s:p#'.
    # Hyphens are not removed by this because hyphens are used sometimes as list itemisers.
    # Hyphens are removed by 'get_lemmas' prior to lemmatising and key word analysis.
    # Only hyphens that constitute tokens are removed, not hyphens within words.
    text = process_sents(remove_punc_fm_sents, wordtok)
        
    # LABEL THE SENTENCES THAT ONLY CONTAIN NUMBERS
    # This labels sentences that only contain numbers and hyphens as '#-s:n#'.
    # This is done to help with identification of headings
    # as well as to omit them from key word and key sentence analysis.
    text = process_sents(find_and_label_numeric_sents, text)
#_______________________________________
    #########################
    # DO STRUCTURE ANALYSIS
    #########################

    # FIND AND LABEL HEADINGS
    # Find and label as 'heading' all the paragraphs that are probably headings, captions, table entries, list items, etc.
    # Happens before lowercasing in case we use letter case as a clue.
    # Happens before removing stop words because some sentences become very short if you remove all the stop words from them, and so can get mistaken for headings.
    text50, headings = find_and_label_headings(text,ass_q_long_words,nf2,dev)

    # FIND AND LABEL SECTION SENTENCES
    text77,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last = \
        find_and_label_section_sents(text50,headings,nf,nf2,dev)
#__________________________________________
    #########################
    # DO FURTHER PRE-PROCESSING OF TEXT FOLLOWING STRUCTURE ANALYSIS
    #########################
    # COUNT THE NUMBER OF WORDS IN THE ESSAY. ONLY COUNT PROSE WORDS (WORDS IN TRUE SENTENCES). 
    countslist = process_sents(count_words, text77)
    mylist = [x for y in countslist for x in y] # unnest
    mylist = [x for y in mylist for x in y] # unnest again
    #print mylist
    number_of_words = sum(mylist)
    print 'number of words: ', number_of_words
       
    # POS-TAG THE TEXT.
    # This has to be done for the lemmatiser to be able to work.
    text77 = process_sents(pos_tag, text77)

    # REMOVE UNWANTED POSs
    # xxxx Don't delete. This was added specifically to test the
    # system against Mihalcea's paper example. I was trying to
    # reproduce her input text, but there weren't enough details in
    # the paper. 
    #text77 = process_sents(remove_unwanted_pos,text77)
    
    # LOWER-CASE THE TEXT
    # This is done so that the same word token represented in
    # different cases will be counted as the same word. Note that
    # this is done after sentence splitting because capitalisation
    # of sentence-initial words is used by sentence splitter.
    text7 = process_sents(lowercase_sents, text77)
    
    # REMOVE STOP WORDS
    text = process_sents(remove_stops_fm_sents, text7)

    # GET THE LEMMA FOR EACH WORD AND PAIR IT WITH ITS SURFACE FORM
    text = process_sents(get_lemmas, text)
        
    return text,parasenttok,wordtok,b_last,\
           len_refs,refsheaded,late_wc,appendixheaded,\
           section_names,section_labels,headings,\
           conclheaded,c_first,c_last,introheaded,i_first,i_last,number_of_words    


# Function: process_essay_se(text, parasenttok, section_labels,nf, nf2, dev):
# Carries out all procedures relating to drawing of sentence graph
# and analysing edges and weights and calculating global weight scores of nodes.
# Called by se_main.py.
def process_essay_se(text, parasenttok, section_labels,nf, nf2, dev):
    # INITIALISE AN EMPTY ARRAY TO HOLD THE SENTENCES
    # Initialise an empty associative array (Python dict) that will
    # hold the sentence- and word- tokenised sentences, each
    # associated with an index key. This is done partly so that we
    # can build a graph using numbers as nodes instead of actual
    # sentences as nodes.
    myarray = {}  

    # DEFINE NODES FOR THE SENTENCE GRAPH TAKING PARTICULAR TEXT SENTENCES AS NODES
    make_sentence_graph_nodes(myarray,text,section_labels,parasenttok)
  
    # INITIATE AN EMPTY GRAPH TO BE THE SENTENCE GRAPH
    #gr_se=nx.DiGraph() # xxxx @directedness: 'directed'. 
    gr_se=nx.Graph() # xxxx @directedness: 'undirected'. 

    # ADD THE DEFINED NODES TO THE EMPTY GRAPH
    # 'list(myarray)' lists only the keys from 'myarray', so this
    # adds the keys from 'myarray' as nodes to the graph 'gr_se'
    # that we have already defined and filled with the essay's
    # sentences, one per key/node.
    gr_se.add_nodes_from(list(myarray)) 
                
    # INITIALISE EMPTY ARRAYS FOR VECTORS
    # Initialise some empty arrays that will be filled with the
    # vectors that will be constructed to enable cosine similarity
    # measurement.
    myWarray = {} 
    myCarray = {}

    # ADD THE EDGES TO THE SENTENCE GRAPH
    add_sentence_graph_edges(gr_se,myarray,myWarray,myCarray,nf2,dev)
    
    #print '\n\nThis is sample_gr_se', sample_gr_se
    #print 'Writing weighted edge list'
    #nx.write_weighted_edgelist(gr_se, 'test.weighted.edgelist.txt') # For graphics purposes. This writes out all the nodes and edges with weights to a text file in current working dir. Used it for graph making.        
    #possible_number_of_edges = ((len(myarray))**2)/2

    # Set current time to a variable for later calculations    
    #graphtime = time() 

    # INITIALISE KEY-NESS SCORES ARRAY
    # Initialise an array with WSVi node score set to 1/graph_size (no. nodes) for all nodes.
    # The decision to use this number to seed scores_array is copied directly from pagerank.py.
    # Beware the problem of massive numbers coming up in WSVi scores if initial scores are too high.
    try:
        scores_array = dict.fromkeys(gr_se.nodes(),1.0/len(gr_se.nodes()))
    except ZeroDivisionError:
        print '\nZero division error: no nodes in graph\n'
        scores_array = dict.fromkeys(gr_se.nodes(),1.0/1)
        #return 'nil','nil','nil'
    #scores_array = dict.fromkeys(gr_se.nodes(),1.0/len(gr_se.nodes()))
        
    # CALCULATE THE KEY-NESS SCORES
    ranked_global_weights,reorganised_array = find_sentence_graph_scores(gr_se,myarray,scores_array,nf2,dev)
        
    return gr_se, ranked_global_weights, reorganised_array                      
    #return gr_se, ranked_global_weights, reorganised_array, graphtime                      

    # Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>


