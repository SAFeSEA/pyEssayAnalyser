import networkx as nx # This is for implementing networks/graphs

from time import time # For calculating processing times

from nltk.tokenize import LineTokenizer # "tokenizer that divides a string into substrings by treating any single newline character as a separator."
from nltk import PunktSentenceTokenizer # The standard sentence tokeniser used by NLTK
from nltk.tag import pos_tag

from se_preprocess_v3 import * # File containing my own functions. This version of the functions uses cosine similarity, no edge if edge == 0, AND uses two arrays to speed up building of the graph. Results are in results_4a.
from se_struc_v3 import *
from se_graph_v3 import *
from se_print_v3 import *
"""
This file contains several long functions which specify the order in which the essay text will be pre-processed, and how the results of that will be processed so as to produce and analyse the sentence graphs.
The procedure for the key word/phrase graphs is not in here but is in the file ke_all.py.
This file does not contain the functions for carrying out all the pre-processing and the sentence graph processing. Those are in files se_preprocess.py, se_struc.py, se_graph.py.
Function names:
# Function: pre_process_text(text0,nf,nf2,dev)
# Function: pre_process_struc(text,nf,nf2,dev):
# Function: pre_process_shorttext(ass_q,dev)
# Function: process_essay_se(text, parasenttok, nf, nf2, dev)
"""
# Function: pre_process_text_se(text0,nf,nf2,dev)
# Carries out some of the text processing that is necessary before the graph can be constructed from the essay's sentences.
# Called by se_main.py.
def pre_process_text(text0,nf,nf2,dev):
#def pre_process_essay(text0,struc_feedback,nf,nf2,dev,model):    
    # Get the body of the essay. 
    # Currently this is everything occurring before the references section but it needs improvement/refinment.

    # Split the essay body on whitespace so that you can correct the latin9 encoding before sentence splitting. 
    # Latin9 encoding puts questions marks everywhere, which confuses the sentence splitter. I reverse this split before sentence tokenisation. 
    text = re.split(r' ', text0)
    #print 'After re.split:'
    #print text[:300]

    # xxxx Note, this used to be 'tidy_up_latin9'. It is now making only one change to the text. Left in in case I need it for Unicode.
    text = edit_text_detail(text)    
    #print 'After edit_text_detail:'
    #print text[:300]

    # Following latin9 tidy-up, un-split the body of the essay ready for sentence splitting.
    temp2 = ' '.join(text) 

    # NVL : IMPORTANT ! 
    # NVL : NEED TO CONVERT TEXT TO STRING (UTF-8)
    # NVL : OTHERWISE YOU HAVE UNICODE TEXT (NOT SURE WHY YET) 
    #temp3 = temp2.encode('utf8')        

    # Paragraph-tokenise the result.
    # This results in having quotation marks as paragraph delimiters.
    paratok = LineTokenizer().tokenize(temp2)

    #x = [w for w in paratok if not w.startswith(u'\\')]  # xxxx temporary for processing a latex file
    #paratok = [w for w in x if not w.startswith(u'%')] # xxxx temporary for processing a latex file
    
    # Sentence-tokenise the result.
    # This results in having quotation marks as sentence delimiters, and preserves the paragraph delimiters by using square brackets.
    temp3 = [PunktSentenceTokenizer().tokenize(item) for item in paratok]     # xxxx normal NLTK sentence splitter   
    #parasenttok = sentence_tokenize(model,paratok) # This calls a sentence splitter that uses a model. The model takes a few seconds to load.
    
    #print '###############################################'
    #print '###############################################'
    b_last,parasenttok, len_refs, refsheaded, late_wc, appendixheaded = get_essay_body(temp3,nf,dev)

    #process_sents(print_function_name, parasenttok)  # xxxx only for printing function names.

    #process_sents(print_unicode_name, parasenttok) # xxx only for printing unicode codes.

    #print 'After parasenttok:'
    #print parasenttok
    #print '\n\n\n~~~~~~~~~~~refs_heading_present: ', refs_heading_present

    
    # Word-tokenise the result.           
    wordtok_text = word_tokenize(parasenttok)
    #print 'Before punc removed:'
    #print wordtok_text[:5]


    # Remove all word-tokens that contain punctuation marks or series of punctuation marks. 
    # This is done because we are not interested in the frequency or usage of punctuation apart from to divide text up into sentences, which has been done by now. 
    #text4 = remove_punc_fm_sents(wordtok_text)
    text4 = process_sents(remove_punc_fm_sents, wordtok_text)
    #print 'After punc removed:'
    #print text4[:5]

    #number_of_words = count_words(text4)
    
    # For each sentence that contains only words which contain numbers, label the sentence as a numeric sentence.
    # Numeric sentences can be module names, entries in tables, list enumerators, etc.
    # Numeric sentences are not returned to the user as important sentences, but they are included in the derivation of the scores.
    # I do not remove them at the beginning, because I do not yet know how interesting/significant numeric sentences are.
    text = process_sents(find_and_label_numeric_sents, text4)

    return text,parasenttok,wordtok_text,b_last,len_refs,refsheaded,late_wc,appendixheaded

# Function: pre_process_struc(text,nf,nf2,dev):
# Labels each sentence with its structural function.
# Also POS-tags, lower-cases, removes stop words, and gets lemmas.
# Relies on pre_process_text_se being done first.
# Called by se_main.py

def pre_process_struc(text,ass_q_long_words,nf,nf2,dev):

    # Find and label as 'heading' all the paragraphs that are probably headings.
    # Currently the sentence scores are worked out with the headings included in the sums, but the headings are not included in the final ranked list returned to the user. 
    # This is because the content of the headings is important, but the headings themselves cannot be key sentences.
    # Happens before lowercasing in case we use letter case as a clue.
    # Happens before removing stop words because some sentences become very short if you remove all the stop words from them, and so can get mistaken for headings.
    text50 = find_and_label_headings(text,ass_q_long_words)
    #print 'After find_and_label_headings:'
    #print text50[:5]


    # Derive from the text all the headings you have found, each with its index.
    someheadings = get_headings(text50)

    # Use the headings you have found so far to see if there are any headings you have missed. This tends to only derive additional headings if there is a 'contents' page.
    headings = get_more_headings_using_contents(text50, someheadings)

    # Set variables 'section_names' and 'section_labels'. Orders match.
    section_names = ['AssQ','Title','Headings', 'Introduction', 'Conclusion', 'Summary', 'Preface', 'Numerics', 'Punctuation']
    section_labels = ['#-s:q#','#-s:t#','#-s:h#','#+s:i#', '#+s:c#', '#+s:s#', '#+s:p#', '#-s:n#', '#-s:p#']
    
    # Find the indices of the first and last paragraphs of the conclusion section.
    ((c_first, c_last),title_indices,conclheaded) = find_section_paras(text50, 'Conclusion', headings, nf, nf2, dev)

    #print '\n\n###########This is c_first, c_last, ##############', c_first, c_last

    # Label the conclusion sentences using the indices you have just found.
    text50a = label_section_sents(text50, 'Conclusion', section_names, section_labels, c_first, c_last)        

    # Find the indices of the first and last paragraphs of the summary section (if there is one).
    ((first, last),(title_first1,title_last1),headingQ) = find_section_paras(text50, 'Summary', headings, nf, nf2, dev)
    # Label the summary sentences using the indices you have just found.    
    text51 = label_section_sents(text50a, 'Summary', section_names, section_labels, first, last)

    # Find the indices of the first and last paragraphs of the preface section (if there is one).    
    ((first, last),(title_first2,title_last2),headingQ) = find_section_paras(text50, 'Preface', headings, nf, nf2, dev)
    # Label the preface sentences using the indices you have just found.
    text52 = label_section_sents(text51, 'Preface', section_names, section_labels, first, last)
       
    # Find the indices of the first and last paragraphs of the introduction section.
    ((i_first, i_last),(title_first3,title_last3),introheaded) = find_section_paras(text50,'Introduction', headings, nf, nf2, dev)        
    # Label the introduction sentences using the indices you have just found.
    text53 = label_section_sents(text52, 'Introduction', section_names, section_labels, i_first, i_last)
    
    # The title will typically appear before the summary if there is one, and before the preface if there is one.
    # But introductions typically follow summaries and prefaces. So we need to look for a title in each case
    # and choose the first one that succeeds.
    if title_first1 != []:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first1, title_last1)
    elif title_first2 != []:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first2, title_last2)
    else:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first3, title_last3)
        

    number_of_words = count_words(text77)

    # Part-of-speech tag the word-tokenised essay.
    text77 = process_sents(pos_tag, text77)

    # xxxx Don't delete. This was added specifically to test the system against Mihalcea's paper example. I was trying to reproduce her input text, but there weren't enough details in the paper.
    text77 = process_sents(remove_unwanted_pos,text77)
    

    # Put all word-tokens into lower case. 
    # This is done so that the same word token represented in different cases will be counted as the same word. Note that this is done after sentence splitting in case capitalisation of sentence-initial words is used by sentence splitter.
    #text7 = lowercase_sents(text77)
    text7 = process_sents(lowercase_sents, text77)

    # Remove all word-tokens that are stop words. 
    # This is done because we are not interested in the frequency or usage of stop words, and because stop words are typically the most frequent words in prose. E.g., we don't want sentence N being returned as the most representative sentence in the text based on how the word 'the' is used.        
    #text = remove_stops_fm_sents(text7)        
    text = process_sents(remove_stops_fm_sents, text7)
    #print text[:5]

    text = process_sents(get_lemmas, text)
    
    return text,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,number_of_words


# Function: pre_process_shorttext(ass_q,dev)
# Get the lemmas of the assignment question so the question can be compared to the essay for overlap.
# Called by se_main.py.

def pre_process_shorttext(ass_q,dev):
    ass_q,a01,a02,a03,a04,a05,a06,a07 = pre_process_text(ass_q,[],[],[]) 
    # Finish processing of assignment title (without doing all the structural analysis)
    temp = process_sents(pos_tag, ass_q)
    temp = process_sents(lowercase_sents, temp)
    temp = process_sents(remove_stops_fm_sents, temp)
    temp = process_sents(remove_unwanted_pos,temp)
    ass_q_lemmd = process_sents(get_lemmas, temp) # Get the list of all the lemmas in the assignment question.
    ass_q_short = [[ass_q_lemmd[0][0]]] # The short version of the assignment question is the first sentence of the long version. But need to preserve sentence,para, and text structure.
    #print '\n\n~~~~~~~~~~~THIS IS ass_q_short in pre_process_shorttext~~~~~~~~~~~~\n', ass_q_short
    ass_q_words = []
    for para in temp: # Get rid of the pos_tag to make a simpler structure for find_and_label_headings
        mylist1 = []
        for sent in para:
            temp2 = [i[0] for i in sent]
            # Also need to do some further pre-processing included in get_lemmas.
            temp2 = [w for w in temp2 if not re.match('^[o0-9]+$',w)] # Gets rid of single letter 'o' (used as a bullet point) and integers.
            temp2 = [w for w in temp2 if not re.match(u'\u2022',w[0])] # Gets rid of bullet points.
            mylist1.append(temp2)
        ass_q_words.append(mylist1)
    #ass_q_words = [x for y in ass_q_words for x in y] # Unnest paragraph level of nesting in ass_q
    #print '\n\n~~~~~~~~~~~THIS IS ass_q_lemmd~~~~~~~~~~~~\n', ass_q_lemmd
    #print '\n\n~~~~~~~~~~~THIS IS ass_q_words~~~~~~~~~~~~\n', ass_q_words
##    temp = [x for y in ass_q for x in y] # Unnest paragraph level of nesting in text
##    temp2 = [x[1:] for x in temp] # Get rid of structure label at head of each sentence
##    ass_q = [x for y in temp2 for x in y] # Unnest sentence level of nesting
    ass_q_lemmd2 = []   # Get the list of unique lemmas in the assignment question.
    mylist3 = []
    for para in ass_q_lemmd:
        mylist = []
        for sent in para:
            temp = [w[1] for w in sent[1:] if w[1] not in mylist3]
            mylist.append(temp)
            mylist3.extend(temp)
        ass_q_lemmd2.append(mylist)
    #print '\n\n~~~~~~~~~~~THIS IS ass_q_lemmd2~~~~~~~~~~~~\n', ass_q_lemmd2        
    return ass_q_words, ass_q_lemmd, ass_q_lemmd2, ass_q_short


# Function: process_essay_se(text, parasenttok, nf, nf2, dev)
# Carries out all procedures relating to drawing of graph and analysing edges and weights and calculating global weight scores of nodes.
# Called by se_main.py.
def process_essay_se(text, parasenttok, nf, nf2, dev):
    # Initialise an empty associative array (Python dict) that will hold the sentence- and word- tokenised sentences, each associated with an index key. 
    # This is done partly so that we can build a graph using numbers as nodes instead of actual sentences as nodes.
    myarray = {}  
    
    # xxxx dummy added for testing. remove later.
    struc_labels = ['#-s:h#', '#-s:n#', '#-s:p#', '#-s:t#', '#-s:q#','#+s:i#', '#+s:c#', '#+s:s#', '#+s:p#', '#dummy#']        

    # Fill array 'myarray' with the fully processed version of the text, one sentence per entry in the array.
    # Each sentence is thus associated with an array key number which represents its position in the text.
    fill_sentence_array(myarray, text, struc_labels)

    # Add each original unprocessed sentence to 'myarray' at the appropriate key point, so they can be returned in the user feedback later.
    # 'Unprocessed' means following latin9 cleanup, after sentence tokenisation, but before word tokenisation and all the other pre-processing
    add_to_sentence_array(myarray, parasenttok) 
    
    # Now we start to build the graph in which the index key to each sentence (from 'myarray') is a node representing that sentence. 
    # We build a graph so that we can work out how strongly connected each sentence is to every other sentence in the graph/text on the basis of similarity of pairs of sentences.

    # Initiate an empty directed graph 'gr_se'.
    # A graph of class 'directed graph' meaning edges are directed, i.e., an edge points like an arrow from one node to another node. This class and 'nx' are from the package 'networkx' which needs to be imported at the start.
    # We use a directed graph encoded in a backwards direction (a node can only point to an earlier node) following some discussion on the penultimate page of (Mihalcea and Tarau, 2005). 
    gr_se=nx.DiGraph() # xxxx Note you do not need to change this in order to test an undirected graph. The changes are made at the point you add the edges to the graph.

    # Add the appropriate nodes to the empty graph.	
    # 'list(myarray)' lists only the keys from 'myarray', so this adds the keys from 'myarray' as nodes to the graph 'gr_se' that we have already defined and filled with the essay's sentences, one per key/node.
    gr_se.add_nodes_from(list(myarray)) 
                
    # Initialise some empty arrays.
    myWarray = {} 
    myCarray = {}

    # Fill one array with the unique words in each sentence (i.e., remove repetitions) and fill the other array with their numbers of occurrences. There is one entry in each array for each sentence.            
    # This is done to speed up the graph-building process. In an essay with 280 sentences, every sentence is compared to every sentence that precedes it, that's about 39,200 comparisons. The arrays are used as look-up tables by the cosine similarity function that measures the similarity of a pair of sentences.
    make_graph_building_arrays(myarray, myWarray, myCarray)
    # Add all the appropriate weighted and directed edges to the graph that you have already initiated, and to which you have added the appropriate nodes. This requires comparison of pairs of sentences/nodes in order to calculate the weight of the edge that joins them.
    add_all_node_edges(gr_se,myWarray,myCarray,nf2,dev)
    
    #print '\n\nThis is sample_gr_se', sample_gr_se

    #print 'Writing weighted edge list'
    #nx.write_weighted_edgelist(gr_se, 'test.weighted.edgelist.txt') # For graphics purposes. This writes out all the nodes and edges with weights to a text file in current working dir. Used it for graph making.    
    
    #possible_number_of_edges = ((len(myarray))**2)/2
    
    graphtime = time() # Set current time to a variable for later calculations

    # Initialise an array with WSVi score set to 1/graph_size (no. nodes) for all nodes.
    # The decision to use this number to seed scores_array is copied directly from pagerank.py. Beware the problem of massive numbers coming up in WSVi scores if initial scores are too high.
    scores_array = dict.fromkeys(gr_se.nodes(),1.0/len(gr_se.nodes()))
    
    # And finally we get to calculate the WSVi global weight score for each node in the graph using parameters set above.
    # This function relies on all the processing done so far (the building of a directed graph with weighted edges using an essay as input).    
    find_all_gw_scores(gr_se, scores_array, nf2, dev)        
    # Add the WSVi scores to the array created earlier that contains the original text before word-tokenisation. For printing the results out.       
    update_array(myarray,scores_array)

    reorganised_array = reorganise_array(myarray)
    
    # Make a structure containing the results, putting the WSVi rank first, 
    ranked_global_weights = sort_ranked_sentences(reorganised_array)
    
    return gr_se, ranked_global_weights, reorganised_array, graphtime                      

