import networkx as nx # This is for implementing networks/graphs
#from time import time # For calculating processing times
from se_preprocess_v3 import parasent_tokenize, edit_text, get_essay_body, process_sents_b4_struc,process_sents_after_struc # File containing my own functions. This version of the functions uses cosine similarity, no edge if edge == 0, AND uses two arrays to speed up building of the graph. 
from se_struc_v3 import find_and_label_headings,find_and_label_section_sents
from se_graph_v3 import make_sentence_graph_nodes, add_sentence_graph_edges, find_sentence_graph_scores
"""
This file contains several long functions which specify the order
in which the essay text will be pre-processed, and how the results of
that will be processed so as to produce and analyse the sentence
graphs. The procedure for the key word/phrase graphs is not in here
but is in the file ke_all.py. This file does not contain the
functions for carrying out all the pre-processing and the sentence
graph processing. Those are in files se_preprocess.py, se_struc.py,
se_graph.py.
Function names:
def pre_process_text(text0,nf,nf2,dev):
def pre_process_struc(text,ass_q_long_words,nf,nf2,dev):
def process_essay_se(text, parasenttok, section_labels,nf, nf2, dev):
"""
# Function: pre_process_text_se(text0,nf,nf2,dev)
# Carries out some of the text processing that is necessary before the graph can be constructed from the essay's sentences.
# Called by se_main.py.
def pre_process_text(text0,nf,nf2,dev):
#def pre_process_essay(text0,nf,nf2,dev,model):    
    # EDIT TEXT
    text = edit_text(text0) # This makes a number of changes to the raw input text before tokenisation to reduce errors by the sentence splitter and to determine how hyphens are dealt with.   
    #print 'After edit_text:', text[:300]

    # PARAGRAPH- AND SENTENCE- TOKENISE TEXT
    text = parasent_tokenize(text)

    # GET ESSAY BODY
    b_last,parasenttok, len_refs, refsheaded, late_wc, appendixheaded = get_essay_body(text,nf,dev)     # Find the body of the essay, being everything after the bibliography. Also note features concerning refs, word count, appendix.

    # DO SOME PRE-PROCESSING OF TEXT BEFORE STRUCTURE ANALYSIS
    proc_text_b4_struc,wordtok_text = process_sents_b4_struc(parasenttok)

    return proc_text_b4_struc,parasenttok,wordtok_text,b_last,len_refs,refsheaded,late_wc,appendixheaded

# Function: pre_process_struc(text,ass_q_long_words,nf,nf2,dev):
# Labels each sentence with its structural function.
# Also POS-tags, lower-cases, removes stop words, and gets lemmas.
# Relies on pre_process_text_se being done first.
# Called by se_main.py

def pre_process_struc(text,ass_q_long_words,nf,nf2,dev):

    # FIND AND LABEL HEADINGS
    # Find and label as 'heading' all the paragraphs that are probably headings.
    # (Currently the sentence scores are worked out without the headings included in the sums.)
    # Happens before lowercasing in case we use letter case as a clue.
    # Happens before removing stop words because some sentences become very short if you remove all the stop words from them, and so can get mistaken for headings.
    text50, headings = find_and_label_headings(text,ass_q_long_words,nf2,dev)
    #print 'After find_and_label_headings:'
    #print text50[:5]    

    # FIND AND LABEL SECTION SENTENCES
    text77,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last = find_and_label_section_sents(text50,headings,nf,nf2,dev)

    # DO FURTHER PRE-PROCESSING OF TEXT NOW THAT YOU HAVE DONE THE STRUCTURE RECOGNITION
    text,number_of_words = process_sents_after_struc(text77)
    
    return text,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,number_of_words




# Function: process_essay_se(text, parasenttok, section_labels,nf, nf2, dev):
# Carries out all procedures relating to drawing of sentence graph
# and analysing edges and weights and calculating global weightnscores of nodes.
# Called by se_main.py.
def process_essay_se(text, parasenttok, section_labels,nf, nf2, dev):
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
    scores_array = dict.fromkeys(gr_se.nodes(),1.0/len(gr_se.nodes()))

    # CALCULATE THE KEY-NESS SCORES
    ranked_global_weights,reorganised_array = find_sentence_graph_scores(gr_se,myarray,scores_array,nf2,dev)
        
    return gr_se, ranked_global_weights, reorganised_array                      
    #return gr_se, ranked_global_weights, reorganised_array, graphtime                      

    # Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
