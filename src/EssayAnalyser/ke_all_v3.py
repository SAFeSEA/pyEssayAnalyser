import re
import itertools
import networkx as nx
#import codecs
from operator import itemgetter
#from pygraph.algorithms.pagerank import pagerank


#from decimal import getcontext, Decimal
#from betweenness import *    '''@todo remove it '''

# The following 5 packages are sometimes used just to see how they compare with the results of this program.
##from nltk.collocations import BigramCollocationFinder
##from nltk.metrics import BigramAssocMeasures
##from nltk.collocations import TrigramCollocationFinder
##from nltk.metrics import TrigramAssocMeasures
##from nltk.probability import FreqDist

''' @todo: check betweenness_centrality; I believe it is the same as in Networkx
'''
from networkx.algorithms.centrality.betweenness import betweenness_centrality

"""
This file contains all the functions that do the key word and key
phrase analysis, apart from the NLP pre-processing of the text.
The principal procedure function 'process_essay_ke' and the results
function 'get_essay_stats_ke' in this file are called in se_main.py.
Function names:
def flatten(nested_list):
def unique_everseen(iterable, key=None):
def add_item_to_array_ke(myarray_ke, num, item):
def add_all_node_edges_ke(gr_ke, text):
def keywords2ngrams(keywords,text,n):
def keywords2ngrams_i(keywords, sent, n):
def sort_betweenness_scores(betweenness_scores, nf):
def cf_ass_q_keylemmas(ass_q,keylemmas,scoresNfreqs):
def cf_ngrams_section(keywords,ngrams,text_se,label):
def process_essay_ke(text,wordtok_text,nf,nf2,dev):
def debora_write_results_ke(text_ke,text_se,gr_ke,di,myarray_ke,threshold_ke,\
def get_essay_stats_ke(text_se,gr_ke,di,myarray_ke,keylemmas,keywords,\
"""

# Function: flatten(nested_list)
# To flatten a list of lists (nested lists) and/or nested tuples
# Called by 
def flatten(nested_list):
    mylist = []
    for item in nested_list:
        if type(item) in (list, list): # type(item) in (list, tuple) for flattening tuples  
            mylist.extend(flatten(item))
        else:
            mylist.append(item)
    return mylist

# Function: unique_everseen(iterable, key=None)
# Lists unique elements, preserving order. Remembers all elements ever seen.
# Note: This is being used to derive the word set from the text.
# This function is copied from an internet source. 
# Called by 'process_essay_ke' (in this file).
def unique_everseen(iterable, key=None):
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

# Function: add_item_to_array_ke(myarray_ke, num, item)
# Add single item 'item' as a new item in 'myarray_ke',
# or as a detail of an existing item. 
# Used to put lists of inflections into an array with their lemma as the key.
# Called by 'process_essay_ke' (in this file).
def add_item_to_array_ke(myarray_ke, num, item):
    if myarray_ke.has_key(num): # If num is one of the keys already in the array...
        myarray_ke[num].append(item) # append 'item' (add 'item' as a detail to an already existing entry).
    else:
        myarray_ke[num] = item # Otherwise add this item as new entry in the array.
        
# Function: add_all_node_edges_ke(gr_ke, text)
# Adds the appropriate edges between nodes already added to the graph.
# to your graph. Given one POS-tagged token/vertex i, up to how far away
# in the POS-tagged list (how many tokens away) from that token are you
# going to look  for a token/vertex j to connect to i? This function currently
# says start at position 0 (first token) for i, finish at position 1 (2-1) for j
# (so the immediately following token), add the edge i->j to the graph, then
# increment start and finish positions and repeat.
# Mihalcea (Textrank paper) says that a window of 2 gives the best results.
# Note that while 'text' is the original text with a bit of pre-processing,
# the nodes in the graph are the lemmas of the words in the text,
# and the edges are drawn to link the lemmas.
# Called by 'process_essay_ke' (in this file).
def add_all_node_edges_ke(gr_ke, text):
    window_start = 0
    window_end = 2
    while 1:
        window_words = text[window_start:window_end]
        if len(window_words) == 2:
            try: # 'add_edge' is defined in 'pygraph\classes\digraph'
                gr_ke.add_edges_from([(window_words[0][1], window_words[1][1])]) # add the edges between the key lemmas not the inflected real words
            except Exception as e: 	# AdditionError is a class defined in 'pygraph\classes\exceptions'
	    #except AdditionError, e:
                '''
                @todo: Cannot find AdditionError, replaced it by Exception
                '''    
				# Stops an edge being added where there already is one.
                #print 'already added %s, %s' % ((window_words[0][0], window_words[1][0]))
                True				
        else:
            break
        window_start += 1
        window_end += 1


# Function: keywords2ngrams(keywords,text,n)
# Takes a list of keywords and looks for ngrams composed of them in a para-sent-word-tok text(where n is specified to a value).
# Calls keywords2ngrams_i to deal with one sentence at a time.
# Updates text to a new version that does not contain the found ngrams.
# This is so that in subsequent calls of keywords2ngrams to find n-grams of a smaller size,
# the same phrases are not collected again.
# Also counts the occurrences of the ngrams and inserts the count into a tuple with the ngram.
# Returns a list of ngram tuples after removing duplicates.
# Called by 'process_essay_ke' (in this file).
def keywords2ngrams(keywords,text,n):
    mylist = []
    newtext = []
    for para in text:
        for sent in para:
            ngrams,newsent = keywords2ngrams_i(keywords, sent, n) # make n-grams out of sequences of key words that occur within-sentence
            if ngrams != []:
                mylist.append(ngrams)
                i = para.index(sent) # Get the position of the sentence in the paragraph
                list.remove(para,sent) # Remove the sentence from the paragraph
                para.insert(i,newsent) # Insert the new sentence (with the ngram phrase deleted) where you deleted the old one. Note that this update the text variable.
    mylist = [x for y in mylist for x in y] # Unnest - get rid of the paragraph nesting to make a straight list of n grams. Don't use 'flatten', because you still need lists of ngrams.
    tuples = []
    for ngram in mylist:
        y = sum(1 for x in mylist if x == ngram) # Count the occurrences of this ngram in the full list of ngrams == occurrences in text
        tuples.append((ngram,y)) # Put each ngram in a tuple with its number of occurrences. # [(['course', 'production'], 1), (['disabled', 'students'], 4),
    mylist3 = []
    for item in tuples:
        if item not in mylist3: # and item[1] > 1: # Get rid of duplicate ngrams. xxxx new condition. Only collect ngrams that occur more than once.
            mylist3.append(item) 
        else:
            mylist3 = mylist3
    result = sorted(mylist3, key = itemgetter(1))
    list.reverse(result)
    return result,text

# Function: keywords2ngrams_i(keywords, sent, n)
# Takes a list of keywords and looks for ngrams composed of them in a single word-tok sentence (where n is specified to a value)
# Note that this is indeed looking for n-grams of key words, not of key lemmas. Key words are different from key lemmas.
# Called by keywords2ngrams with one sentence.
# During processing, the input sentence is replaced by a revised sentence that does not contain the found n-gram.
# This is so that in subsequent calls of keywords2ngrams to find n-grams of a smaller size,
# the same phrases are not collected again.
def keywords2ngrams_i(keywords, sent, n):
    win_start = 0
    win_end = n
    mylist = []
    mylist2 = []
    mylist3 = []
    while 1:
        win_words = sent[win_start:win_end] # sent[0:3] which is really sent[0:3-1]        
        if len(win_words) == n:
            if n == 4:
                if win_words[0] in keywords and win_words[1] in keywords and win_words[2] in keywords and win_words[3] in keywords:                    
                    mylist.append(win_words) # add this n-gram to the growing list for output
                    del sent[win_start:win_end] # delete this n-gram from sent to make a new sentence
                else:
                    mylist = mylist
                win_start += 1
                win_end += 1    
            elif n == 3:
                if win_words[0] in keywords and win_words[1] in keywords and win_words[2] in keywords:
                    mylist.append(win_words)
                    del sent[win_start:win_end]
                else:
                    mylist = mylist
                win_start += 1
                win_end += 1
            elif n == 2:
                if win_words[0] in keywords and win_words[1] in keywords:                    
                    mylist.append(win_words)
                    del sent[win_start:win_end]
                else:
                    mylist = mylist
                win_start += 1
                win_end += 1                
        else:
            break    
    return mylist, sent 
    
# Function: sort_betweenness_scores(betweenness_scores, nf)
# Sort the key lemmas in descending order of importance.
# Called by 'process_essay_ke' (in this file).
def sort_betweenness_scores(betweenness_scores, nf):
    #print betweenness_scores
    temp0 = betweenness_scores.items()
    temp1 = [x for x in temp0]
    temp = sorted(temp1, key = itemgetter(1))
    list.reverse(temp)
    return temp


# Function: cf_ass_q_keylemmas(ass_q,keylemmas,scoresNfreqs)
# Compares the assignment question lemmas with the found key lemmas.
# Returns the sum of the frequencies of the key lemmas that occur in the the list of assignment question lemmas (sum_freq_kls_in_ass_q)
# as well as a list of those key lemmas (kls_in_ass_q).
# Called by debora_results_ke (in this file).
def cf_ass_q_keylemmas(ass_q,keylemmas,scoresNfreqs):
    temp = [x for y in ass_q for x in y] # Unnest paragraph level of nesting in text
    temp2 = [x[1:] for x in temp] # Get rid of structure label at head of each sentence
    ass_q = [x for y in temp2 for x in y] # Unnest sentence level of nesting
    kls_in_ass_q = []
    mylist3 = []
    for mytuple in ass_q: # 
        if mytuple[1] in keylemmas:
            for item in scoresNfreqs:
                if item[0] == mytuple[1] and item not in mylist3: # Use mylist3 to prevent adding duplicates
                    kls_in_ass_q.append(item) # ('accessibility', 0.10632945238775138, 2, 12)
                    mylist3.append(item)
    mylist = []
    for item in kls_in_ass_q:
        mylist.append(item[3])
    sum_freq_kls_in_ass_q = sum(mylist)
    #print '\n\n~~~~~~~~~~~THIS IS kls_in_ass_q, in cf_ass_q_keylemmas~~~~~~~~~~~~\n', kls_in_ass_q
    return kls_in_ass_q, sum_freq_kls_in_ass_q


# Function: cf_ngrams_section(keywords,ngrams,text_se,label)
# Makes some comparisons between the sentences that constitute the introduction, 
# and the found n-grams (that are made of key words)
# Returns the count of n-grams that are in the introduction.
# Does something similar for 'conclusion' sentences. 
# Called by debora_results_ke (in this file).
def cf_ngrams_section(keywords,ngrams,text_se,label):
    temp = [x for y in text_se for x in y] # Unnest paragraph level of nesting in text
    if label == '#+s:i#':
        temp = [item for item in temp if item[0][0] == '#+s:i#'] # [('#+s:i#', 'NN'), ('report', 'report'), ('outlines', 'outline'), ('main', 'main'),
    elif label == '#+s:c#':
        temp = [item for item in temp if item[0][0] == '#+s:c#'] # [('#+s:i#', 'NN'), ('report', 'report'), ('outlines', 'outline'), ('main', 'main'),
    else:
        temp = temp
    if ngrams != []:
        n = len(ngrams[0][0]) # Get the length of the ngram (could be 2,3,4...)
    else:
        n = 0
    temp = [x[1:] for x in temp] # Get rid of structure label at head of each sentence
    text = [x for y in temp for x in y] # Unnest sentence level of nesting
    counterA = 0
    counterB = 1
    intro_phrases = []
    while 1:
        if counterB <= len(text)-1 and n == 2: # xxxx Note that this is set up only to deal with bigrams. 
            temp = [text[counterA][0],text[counterB][0]] # xxxx If I want to do trigrams or other n-grams, I need to change this to deal with longer phrases.
            intro_phrases.append(temp)
            counterA +=1
            counterB +=1
        else:
            break
    mylist = []
    for item in ngrams:
        if item[0] in intro_phrases:
            mylist.append(item)
    #print '\n\n~~~~~~~~~~~~~~~THIS IS mylist of found ngrams:', mylist
    count1 = sum(1 for item in mylist)   # The number of distinct key bigrams found in the assignment question or intro or concl
    temp = [item[1] for item in mylist]
    count2 = sum(temp)  # The total number of those bigrams in the whole essay
    return count1,count2
    

# Function: process_essay_ke(text,wordtok_text,nf,nf2,dev)  
# Derive key lemmas
def process_essay_ke(text,wordtok_text,nf,nf2,dev):
    #print '\n\n\n text', text
    # These lines are needed to map the essay's nested and labelled structure into something simpler,
    # because we don't need the paragraph and sentence structure information to derive the key lemmas.
    # Currently I am not deriving/carrying the index number for each key word and each n-gram.
    temp = [x for y in text for x in y] # Unnest paragraph level of nesting in text

    # Temporarily playing around with using only TRUE sentences to derive key words. This because I am now attempting to exclude the assignment question from the true sentences.
    # I suppose I could include headings if the results are strange??
    # 24/07/2013 Now I have added twp classes of what I have hitherto called 'headings',
    # two of which I want to include in the key word graph: table entries '#-s:e#' and short bullet points '#-s:b#'.

    mylabels = ['#+s#','#+s:i#','#+s:c#','#+s:s#','#+s:p#', '#-s:e#', '#-s:b#'] # '#dummy#',
    temp = [x for x in temp if x[0][0] in mylabels]
    temp2 = [x[1:] for x in temp] # Get rid of structure label at head of each sentence
    text = [x for y in temp2 for x in y] # Unnest sentence level of nesting  

    # Get the lemma set for the essay.
    unique_lemma_set = unique_everseen([x[1] for x in text ])

    myarray_ke = {} # Initiate an array 
    
    for item in unique_lemma_set:  # item: fox
        temp = [w[0] for w in text if item == w[1]] # temp: ['foxes', 'foxes', 'foxes', 'fox', 'foxes', 'foxes', 'foxes', 'fox']
        add_item_to_array_ke(myarray_ke, item, temp)

    # Initiate an empty directed graph 'gr_ke' of 'digraph' class  
    gr_ke=nx.DiGraph()
    #gr_ke=nx.Graph() # xxxx for non-directed graph testing
    
    # Add nodes to the directed graph 'gr_ke', one node for each unique lemma.
    # If you are filtering out certain parts of speech, or stop words, or..., you will add a node only for those remaining unique words.
    gr_ke.add_nodes_from(unique_lemma_set)
   
    # Add directed edges to the graph to which you have alreaded added nodes. 
    # A directed (and unweighted) edge is added from each node to the node whose corresponding inflected lemma follows it in the prepared text.
    # Note that, owing to the repetition of lemmas in the text, some nodes will have many edges linking them, while many will have only one.
    add_all_node_edges_ke(gr_ke,text)   

##    # Calculate the betweenness centrality score for each node in the graph.
    betweenness_scores = betweenness_centrality(gr_ke)    
    # 'calculated_page_rank' is the unsorted set of all scores, each with its word.
    # 'pagerank' is imported from 'pygraph\algorithms\pagerank', which also sets various parameters (damping factor, initial scores, minimum score, etc.) 
    #calculated_page_rank = pagerank(gr_ke, nf) # pagerank version
    
##    # Sort the scores into order.
    di = sort_betweenness_scores(betweenness_scores, nf) # Leave this in for the betweenness centrality version.
    #di = sorted(calculated_page_rank.iteritems(), key=itemgetter(1)) # pagerank version
    #list.reverse(di) # pagerank version


    # How many of the key lemmas are key as opposed to not key? TextRank paper says a third of unique wordset are key words.
    # Get only those key lemmas that have a score greater than x and that are in the top y per cent of words ranked by score 
    a = len(di)
    y = 0.20 # y is going to be the percentage threshold. .03 will get us the top 3 per cent.
    x = 0.03 # x is going to be the score threshold. 0.1 will get us every word that scores more than 0.1.
    #x = 0.01 # xxxx for Seale text book. For larger texts you need a lower threshold otherwise not many key words.
    #print a, y, x
    threshold_ke = (y,x)
    b = int(a * y)
    temp = di[0:b]
    #print temp # xxxx Check this when testing pagerank version
    keylemmas = []
    for item in temp:  # 'item' has pair structure: ('students', 0.3138429126331271)
        if item[1] > x:
            keylemmas.append(item[0])        
    # Get a flat list of all the key words that actually appear in the text (not the key lemmas)
    #print myarray_ke
    keywords = []
    for item in keylemmas:
        #print item
        wordlist = myarray_ke[item] # by looking up in myarray_ke the values of the key lemmas
        monitorlist = []
        for w in wordlist:
            if w not in monitorlist:
                keywords.append(w)
                monitorlist.append(w)
            else:
                monitorlist.append(w)

    # Make key phrases by looking for series of key words in original text (that is, after word-tokenisation but before punc and stops are removed). Don't repeat counts of the same phrase when a larger n-gram contains a smaller one.
    quadgram_keyphrases,newtext = keywords2ngrams(keywords,wordtok_text,4)
    trigram_keyphrases,newtext = keywords2ngrams(keywords,newtext,3)
    bigram_keyphrases,newtext = keywords2ngrams(keywords,newtext,2)
    return text, gr_ke,di,myarray_ke,keylemmas, keywords,bigram_keyphrases, trigram_keyphrases, quadgram_keyphrases, threshold_ke


def debora_write_results_ke(text_ke,text_se,gr_ke,di,edges_over_sents,myarray_ke,threshold_ke,\
                     keylemmas,keywords,fivemostfreq,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                     scoresNfreqs,avfreqsum,\
                     uls_in_ass_q_long,kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
                     kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
                     kls_in_tb_index, sum_freq_kls_in_tb_index,
                     bigrams_in_intro1,bigrams_in_intro2,\
                     bigrams_in_concl1,bigrams_in_concl2,\
                     bigrams_in_assq1,bigrams_in_assq2,\
                     all_bigrams,topbetscore,nf,nf2):
    nf.write('\nNumber of key lemmas (with threshold_ke ')
    nf.write(str(threshold_ke))
    nf.write(') :\n')
    nf.write(str(len(keylemmas)))
    nf.write('\n')
    
    nf.write('\nList of key lemmas (in rank order):\n')
    s = str(keylemmas)
    c = s.decode('unicode-escape')
    nf.write(c)
    nf.write('\n')
    
    nf.write('\nList of distinct key words (the inflected forms of the key lemmas):\n')
    s = str(keywords)
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')    
##    topbetscore = scoresNfreqs[0][1]
##    nf.write('\nTop betw score:')
##    nf.write(str(topbetscore))
##    nf.write('\n')    
    nf.write('\nList of the five most freq lemmas: \n')
    s = str(fivemostfreq)
    c = s.decode('unicode-escape')
    nf.write(c)
    nf.write('\n')
    
    nf.write('\nMean avg freq of five most freq lemmas: ')
    s = str(avfreqsum)
    c = s.decode('unicode-escape')
    nf.write(c)
    nf.write('\n')

    nf.write('\nList of distinct quadgrams:\n') #  (seqs of within-sentence key words)
    s = str(quadgram_keyphrases)
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')
    
    nf.write('\nList of distinct trigrams:\n')
    s = str(trigram_keyphrases)
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')
    
    nf.write('\nList of distinct bigrams:\n')
    s = str(bigram_keyphrases)
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')
    
    nf.write('\nNo. key lemmas occurring in ass_q_long: ')
    s = str(len(kls_in_ass_q_long))
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')
    
    nf.write('\nList of essay key lemmas (+ freq) in ass_q_long:\n')
    s = str(kls_in_ass_q_long)
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')
    
    nf.write('\nSum of frequencies of key lemmas in ass_q_long: ')
    s = str(sum_freq_kls_in_ass_q_long)
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')

    nf.write('\nList of key lemmas (+ freq) occurring in ass_q_short:\n')
    s = str(kls_in_ass_q_short)
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')
    
    nf.write('\nSum of frequencies of key lemmas in ass_q_short: ')
    s = str(sum_freq_kls_in_ass_q_short)
    c = s.decode('unicode-escape')
    nf.write(c)        
    nf.write('\n')

    nf.write("\nNumber of the essay's key lemmas occurring in the text book index: ")
    s = str(len(kls_in_tb_index))
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')    

    nf.write("\nList of the essay's key lemmas that occur in the text book index:\n")
    s = str(kls_in_tb_index)
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')

    nf.write("\nSum of frequencies of the essay's key lemmas that occur in the text book index: ")
    s = str(sum_freq_kls_in_tb_index)
    c = s.decode('unicode-escape')
    nf.write(c)
    nf.write('\n')
    
    nf.write('Number of bigrams in the introduction section: ')
    s = str(bigrams_in_intro1)
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')

    nf.write('Number of bigrams in the conclusion section: ')
    s = str(bigrams_in_concl1)
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')


    s = str(scoresNfreqs)
    s = re.sub('\),'   ,  ',\n'   , s)
    s = re.sub('\)'    ,  ''   , s)
    s = re.sub('\s\('  ,  ''   , s)
    s = re.sub('\('  ,  ''   , s)
    #s = re.sub('\''  ,  ''   , s)
    s = re.sub('\['  ,  ''   , s)
    s = re.sub('\]'  ,  ''   , s)
    nf.write('\nAll lemmas: lemma, rank, betw score, freq\n')
    c = s.decode('unicode-escape')
    nf.write(c)    
    nf.write('\n')   
    nf.write('\n*******************************************************\n\n')


    ###########WRITE TO SUMMARY FILE###################
    ###################
    ###################
    ## FULL SET
    ###################
    ###################
    nf2.write('key lemmas; ') 
    nf2.write(str(len(keylemmas)))
    nf2.write('; ')   
    nf2.write('ke centr thrshld; ') #(20,.03) # Centrality score threshold_ke expressed as '(percentage_of_true_sents, centrality_score)' tuple defining what qualifies as a key lemma
    nf2.write(str(threshold_ke))
    nf2.write('; ')
    nf2.write('all lemmas; ')
    nf2.write(str(len(di)))
    nf2.write('; ')
    nf2.write('no name; ')
    if avfreqsum > 0:
        x = (float(edges_over_sents)/float(avfreqsum))*float(len(di))
    else:
        x = 'nil'
    nf2.write(str(x))
    nf2.write('; ') 
    nf2.write('key words; ') #(20 & >= .03%)
    nf2.write(str(len(keywords)))
    nf2.write('; ')
    nf2.write('avfreq top5freq; ') # Average frequency of the top five most frequent lemmas
    #nf2.write('avfreq top3freq; ') # xxxx Average frequency of the top THREE most frequent lemmas    
    nf2.write(str(avfreqsum))
    nf2.write('; ')    
    nf2.write('distinct bigrams; ') # the number of different bigrams made up from key words
    nf2.write(str(len(bigram_keyphrases)))
    nf2.write('; ')
    x = sum(item[1] for item in bigram_keyphrases) # the total number of bigrams made up from key words including repetitions of bigrams.
    nf2.write('sum freq bigrams; ')
    nf2.write(str(x))
    nf2.write('; ')
##    nf2.write('bigrams in intro; ')
##    nf2.write(str(bigrams_in_intro1))
##    nf2.write('; ')
##    nf2.write('bigrams in concl; ')
##    nf2.write(str(bigrams_in_concl1))
##    nf2.write('; ')
    #nf2.write('ul in ass_q_long; ') # Number of unique lemmas appearing in ass_q_long # Added for abstract analyses
    #nf2.write(str(uls_in_ass_q_long))
    #nf2.write('; ')
    nf2.write('kls in ass_q_long; ') # Number of key lemmas also appearing in the ass_q_long
    nf2.write(str(len(kls_in_ass_q_long)))
    nf2.write('; ')
    nf2.write('sum freq kls_in_ass_q_long; ') # Sum of frequencies of key lemmas that appear in the ass_q_long
    nf2.write(str(sum_freq_kls_in_ass_q_long))
    nf2.write('; ')
    nf2.write('bigrams in ass_q; ') # 'Total number of key bigrams in the essay that also occur in the assignment question
    nf2.write(str(bigrams_in_assq2))
    nf2.write('; ')
##    nf2.write('kls in ass_q_short; ') # Number of key lemmas also appearing in the ass_q_short
##    nf2.write(str(len(kls_in_ass_q_short)))
##    nf2.write('; ')
##    nf2.write('sum freq kls_in_ass_q_short; ') # Sum of frequencies of key lemmas that appear in the ass_q_short
##    nf2.write(str(sum_freq_kls_in_ass_q_short))
##    nf2.write('; ')
    nf2.write("kls_in_tb_index; ") # Number of the essay's key lemmas occurring in the text book index
    nf2.write(str(len(kls_in_tb_index)))
    nf2.write('; ')
    nf2.write('sum_freq_kls_in_tb_index; ') # Sum of frequencies of the essay's key lemmas that occur in the text book index
    nf2.write(str(sum_freq_kls_in_tb_index)) 
    nf2.write('; ')
    nf2.write('ke top centr score; ')
    if len(scoresNfreqs)>0: # edge case condition
        x = scoresNfreqs[0][1]
        topbetscore = round(x,3)
    else:
        topbetscore = 'nil'
    nf2.write(str(topbetscore))
    nf2.write('\n') 


##    ###################
##    ###################
##    ## PARTIAL SET
##    ###################
##    ###################
##    nf2.write('key lemmas; ') 
##    nf2.write(str(len(keylemmas)))
##    nf2.write('; ')   
####    nf2.write('ke centr thrshld; ') #(20,.03) # Centrality score threshold_ke expressed as '(percentage_of_true_sents, centrality_score)' tuple defining what qualifies as a key lemma
####    nf2.write(str(threshold_ke))
####    nf2.write('; ')
##    nf2.write('all lemmas; ')
##    nf2.write(str(len(di)))
##    nf2.write('; ')          
####    nf2.write('key words; ') #(20 & >= .03%)
####    nf2.write(str(len(keywords)))
####    nf2.write('; ')
##    nf2.write('avfreq top5freq; ') # Average frequency of the top five most frequent lemmas
##    nf2.write(str(avfreqsum))
##    nf2.write('; ')    
##    nf2.write('distinct bigrams; ') # the number of different bigrams made up from key words
##    nf2.write(str(len(bigram_keyphrases)))
##    nf2.write('; ')
##    x = sum(item[1] for item in bigram_keyphrases) # the total number of bigrams made up from key words including repetitions of bigrams.
##    nf2.write('sum freq bigrams; ')
##    nf2.write(str(x))
##    nf2.write('; ')
####    nf2.write('bigrams in intro; ')
####    nf2.write(str(bigrams_in_intro1))
####    nf2.write('; ')
####    nf2.write('bigrams in concl; ')
####    nf2.write(str(bigrams_in_concl1))
####    nf2.write('; ')
##    #nf2.write('ul in ass_q_long; ') # Number of unique lemmas appearing in ass_q_long # Added for abstract analyses
##    #nf2.write(str(uls_in_ass_q_long))
##    #nf2.write('; ')
##    nf2.write('kls in ass_q_long; ') # Number of key lemmas also appearing in the ass_q_long
##    nf2.write(str(len(kls_in_ass_q_long)))
##    nf2.write('; ')
##    nf2.write('sum freq kls_in_ass_q_long; ') # Sum of frequencies of key lemmas that appear in the ass_q_long
##    nf2.write(str(sum_freq_kls_in_ass_q_long))
##    nf2.write('; ')
##    nf2.write('bigrams in ass_q; ') # 'Total number of key bigrams in the essay that also occur in the assignment question
##    nf2.write(str(bigrams_in_assq2))
##    nf2.write('; ')
####    nf2.write('kls in ass_q_short; ') # Number of key lemmas also appearing in the ass_q_short
####    nf2.write(str(len(kls_in_ass_q_short)))
####    nf2.write('; ')
####    nf2.write('sum freq kls_in_ass_q_short; ') # Sum of frequencies of key lemmas that appear in the ass_q_short
####    nf2.write(str(sum_freq_kls_in_ass_q_short))
####    nf2.write('; ')
##    nf2.write("kls_in_tb_index; ") # Number of the essay's key lemmas occurring in the text book index
##    nf2.write(str(len(kls_in_tb_index)))
##    nf2.write('; ')
##    nf2.write('sum_freq_kls_in_tb_index; ') # Sum of frequencies of the essay's key lemmas that occur in the text book index
##    nf2.write(str(sum_freq_kls_in_tb_index)) 
##    nf2.write('; ')
####    nf2.write('ke top centr score; ')
####    if len(scoresNfreqs)>0: # edge case condition
####        x = scoresNfreqs[0][1]
####        topbetscore = round(x,3)
####    else:
####        topbetscore = 'nil'
####    nf2.write(str(topbetscore))
##    nf2.write('\n') 
##
##    # nf2.write('\n__________________________________________________\n')
##
##
##    s = str(scoresNfreqs)
##    s = re.sub('\),'   ,  ',\n'   , s)
##    s = re.sub('\)'    ,  ''   , s)
##    s = re.sub('\s\('  ,  ''   , s)
##    s = re.sub('\('  ,  ''   , s)
##    s = re.sub('\''  ,  ''   , s)
##    s = re.sub('\['  ,  ''   , s)
##    s = re.sub('\]'  ,  ''   , s)
##    #nf2.write(s)
##    #nf2.write('\n')
##
##    s = str(keylemmas)
##    c = s.decode('unicode-escape')
##    nf2.write(c)
##    nf2.write('\n')
##    #nf2.write('\nList of distinct bigrams:\n')
####    nf2.write('\n')
####    s = str(bigram_keyphrases)
####    c = s.decode('unicode-escape')
####    nf2.write(c)        
####    nf2.write('\n\n')

# Function: debora_get_stats_ke
# Called by top_level_procedure in main.py.
# Does arithmetic to get results that we are interested in.  
def get_essay_stats_ke(text_se,gr_ke,di,myarray_ke,keylemmas,keywords,\
                        bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases,\
                        ass_q_long_words, ass_q_long_lemmd, ass_q_long_lemmd2,ass_q_short_lemmd,\
                        tb_index_lemmd, tb_index_lemmd2):
                        #ass_q_long,ass_q_short):
                    
    # For each lemma, make a tuple containing the lemma, its centrality score, its centrality ranking, and its frequency.
    z = len(di)
    nums = range(z)
    counter = 0    
    scoresNfreqs = []
    #print '\n\n\n\n\n#############This is myarray_ke', myarray_ke # Yes, the hyphenated forms are in the array

    while 1:
        if counter <= len(di)-1:
            lemma = di[counter][0]
            freqlemma = len(myarray_ke[lemma]) # The frequency of the inflected forms of this lemma in the essay is the length of the list of inflected forms associated with this lemma in the array
            # [('student', 0.3328931614802702, 0, 38), ('use', 0.18376249760232427, 1, 22), ('tool', 0.15331752034879637, 2, 14)
            temp = (lemma,di[counter][1],nums[counter],freqlemma)
            scoresNfreqs.append(temp)
            counter+=1
        else:
            break       

    temp = sorted(scoresNfreqs, key = itemgetter(3))
    list.reverse(temp)
    fivemostfreq = temp[:5]
    freqs = [item[3] for item in fivemostfreq]
    avfreqsum = sum(freqs)/5 # xxxxx Changed it to 3 to see what difference it makes in TMA02

    # cf_ass_q_keylemmas is called three times: (i) with long assignment q; (ii) short assignment q; (iii) textbook index

    # xxx Note that  cf_ass_q_keylemmas is not being called in the openEssayist version, so I am just giving
    # dummy values here to avoid having to make a lot of changes.

##    kls_in_ass_q_long, sum_freq_kls_in_ass_q_long = cf_ass_q_keylemmas(ass_q_long_lemmd,keylemmas,scoresNfreqs)
##    kls_in_ass_q_short, sum_freq_kls_in_ass_q_short = cf_ass_q_keylemmas(ass_q_short_lemmd,keylemmas,scoresNfreqs)    
##    kls_in_tb_index, sum_freq_kls_in_tb_index = cf_ass_q_keylemmas(tb_index_lemmd,keylemmas,scoresNfreqs)

    kls_in_ass_q_long = []
    sum_freq_kls_in_ass_q_long  = 0
    kls_in_ass_q_short = []
    sum_freq_kls_in_ass_q_short = 0
    kls_in_tb_index = []
    sum_freq_kls_in_tb_index = 0 

    flat_ass_q_long_lemmd2 = flatten(ass_q_long_lemmd2)
    uls_in_ass_q_long = sum(1 for item in flat_ass_q_long_lemmd2)
 
    bigrams_in_intro1, bigrams_in_intro2 = cf_ngrams_section(keywords,bigram_keyphrases,text_se,'#+s:i#')
    bigrams_in_concl1, bigrams_in_concl2 = cf_ngrams_section(keywords,bigram_keyphrases,text_se,'#+s:c#')
    bigrams_in_assq1,bigrams_in_assq2 = cf_ngrams_section(keywords,bigram_keyphrases,ass_q_long_lemmd,'#dummy#')
    
    #print 'This is bigram_keyphrases:\n', bigram_keyphrases
    all_bigrams = sum(item[1] for item in bigram_keyphrases) # the total number of bigrams made up from key words including repetitions of bigrams.
    if len(scoresNfreqs)>0: # edge case condition
        x = scoresNfreqs[0][1]
        topbetscore = round(x,3)
    else:
        topbetscore = 'nil'
    return scoresNfreqs,fivemostfreq,avfreqsum,\
           uls_in_ass_q_long,kls_in_ass_q_long,sum_freq_kls_in_ass_q_long,\
           kls_in_ass_q_short,sum_freq_kls_in_ass_q_short,\
           kls_in_tb_index, sum_freq_kls_in_tb_index,\
           bigrams_in_intro1,bigrams_in_intro2,\
           bigrams_in_concl1,bigrams_in_concl2,\
           bigrams_in_assq1,bigrams_in_assq2,\
           all_bigrams,topbetscore

# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
