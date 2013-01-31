import re
import itertools
import networkx as nx
#from pygraph.classes.exceptions import AdditionError
from nltk.tag import pos_tag
from nltk.tokenize import WordPunctTokenizer 
from nltk.corpus import stopwords
#from nltk.stem.lancaster import LancasterStemmer
from operator import itemgetter
#from betweenness import *

# The following 5 packages are being used just to see how they compare with the results of this program.
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import TrigramAssocMeasures
from nltk.probability import FreqDist

from networkx.algorithms.centrality.betweenness import betweenness_centrality
from networkx.readwrite import json_graph

from EssayAnalyser import _apiLogger #, _tempDir
from operator import itemgetter


"""
Function names:
# Function: get_essay_body
# Function: tidy_up_text
# Function: filter_unwanted_words
# Function: unique_everseen
# Function: add_all_node_edges_ke
# Function: keywords2ngrams
# Function: sort_betweenness_scores
# Function: pre_process_essay_ke  
# Function: process_essay_ke  
# Function: debora_results_ke
"""

# Function: get_essay_body
# Currently this gets all that occurs before the bibliography
#(actually before the last occurrence of the term 'references' (or ...)). 
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
# I have tried various ways of using a disjunction for this, but have not yet succeeded.
def get_essay_body(text,nf,dev):
    if 'References' in text:
        a = text.rfind('References') # Find the LAST occurrence of 'References', not the first, in case there is a contents page or other xref.        
        b = text[:a] # Get all the text of the essay occurring before the bibliography (the body).
        return b, 'yes'    
    elif 'REFERENCES' in text:
        a = text.rfind("REFERENCES") 
        b = text[:a] 
        return b, 'yes'
    elif 'Reference' in text: # One essay I looked at had the bibliography section title: 'Reference list'.
        a = text.rfind("Reference") 
        b = text[:a] 
        return b, 'yes'
    elif 'REFERENCE' in text: # One essay I looked at had: 'REFERENCE'.
        a = text.rfind("REFERENCE") 
        b = text[:a] 
        return b, 'yes'         
    elif 'Bibliography' in text:
        a = text.rfind("Bibliography") 
        b = text[:a] 
        return b, 'yes'
    else:
        if dev == 'DGF':
            print '\n********* Cannot find a references section. *********\n'
            nf.write('\n********* Cannot find a references section. *********\n')
        return text, 'no' # If none of those terms are in text, just return text.                        

# Function: tidy_up_text
# Replaces some non-ASCII characters with an ASCII substitute.
# Also reformats some terms.
# The 'restore_quote' procedure is commented out because it's not necessary and so 'restore_quote' is also missing from this file.
# Returns updated text.
def tidy_up_text(text):
    counter = 0
    text = [re.sub('^i\.e\.', "ie", w) for w in text] # 'i.e.' with 'ie'
    text = [re.sub('^e\.g\.', "eg", w) for w in text] # 'e.g.' with 'eg'
    text = [re.sub('^e-', "e", w) for w in text] # 'e-' with 'e'    
    text = [re.sub('\n\?$', "\n* ", w) for w in text] # paragraph-initial question mark followed by whitespace replaced with paragraph marker then a star then a space
    text = [re.sub('\\xfc', "o", w) for w in text] # 'u umlaut' 
    text = [re.sub('\\xf6', "o", w) for w in text] # 'o umlaut' 
    text = [re.sub('\\xb9', "", w) for w in text] # footnote marker     
    text = [re.sub('\\xe9', "e", w) for w in text] # 'e accute' 
    text = [re.sub('\\xa3', "GBP ", w) for w in text] # British pound sign
    text = [re.sub('\\xa0', " ", w) for w in text] 
    text = [re.sub('\t', " ", w) for w in text] # Just getting rid of tab characters that are attached to words
    text = [re.sub('\r', " ", w) for w in text] # Just getting rid of '\r' characters that are attached to words
    text = [re.sub('\n', "", w) for w in text] # Just getting rid of '\n' characters that are attached to words    
    text = [re.sub('\?t$', "'t", w) for w in text] # Apostrophe: "don?t" becomes "don't"
    text = [re.sub('^\?$', "--", w) for w in text]   # Em-dashes and en-dashes: 'access ? enrolment' becomes 'access -- enrolment'
    text = [re.sub('\?s$', "'s", w) for w in text]   # Apostrophe: "Frankenstein?s" becomes "Frankenstein's"
    text = [re.sub('^p\.$', "p", w) for w in text]   # change 'p.' to 'p'
    text = [re.sub(u'\u2022', "*", w) for w in text]
    text = [re.sub(u'\u2019', "'", w) for w in text]
    text = [re.sub(u'\u2018', "'", w) for w in text]
    text = [re.sub(u'\u201c', "\"", w) for w in text]
    text = [re.sub(u'\u201d', "\"", w) for w in text]
    
    return text

# Function: filter_unwanted_words
# Removes tokens that have the POS categories that you are not interested in,
# i.e., those tokens/words that you don't want to become nodes in your graph.
# Also removes words you don't want that are not removed by the stop words procedure.
def filter_unwanted_words(tagged, tags=['CD','LS','MD','RB','RBR','RBS','SYM','WRB']):
#def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):    
    temp = [item for item in tagged if item[1] not in tags]
    mylist = ['et', 'al', 'eg', 'ie', 'etc', 'may', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
              'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
              '&' ]
    return [item for item in temp if item[0] not in mylist]

# Function: get_word_stems
# Replaces each word with its stem. This needs a lot of thought concerning when it
# should be done, and what should then be returned to the user.
##def get_word_stems(text):
##    st = LancasterStemmer()
##    mylist = []
##    for w in text:
##        temp = st.stem(w[0])
##        mylist.append((temp, w[1]))
##    print 'This is mylist', mylist
##    return mylist


# Function: unique_everseen
# Lists unique elements, preserving order. Remember all elements ever seen.
# Note: This is being used to derive the wordset from the text.
# This function is copied from an internet source. I think this is something that
# NLTK has a built-in function for but I'm going to keep this one for the time
# being because I'm trying to learn new Python ways of doing things.
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

# Function: add_all_node_edges_ke
# Adds the appropriate edges between nodes you have already added
# to your graph. Given one POS-tagged token/vertex i, up to how far away
# in the POS-tagged list (how many tokens away) from that token are you
# going to look  for a token/vertex j to connect to i? This function currently
# says start at position 0 (first token) for i, finish at position 1 (2-1) for j
# (so the immediately following token), add the edge i->j to the graph, then
# increment start and finish positions and repeat.
def add_all_node_edges_ke(gr, text):
    window_start = 0
    window_end = 2
    while 1:
        window_words = text[window_start:window_end]
        if len(window_words) == 2:
            #print window_words
            try: # 'add_edge' is defined in 'pygraph\classes\digraph'
                gr.add_edges_from([(window_words[0][0], window_words[1][0])])                                
            except ValueError, e: 	# AdditionError is a class defined in 'pygraph\classes\exceptions'
					# Stops an edge being added where there already is one.
                #print 'already added %s, %s' % ((window_words[0][0], window_words[1][0]))
                True				
        else:
            break
        window_start += 1
        window_end += 1

# Function: get_ngrams
# Takes a list of keywords and looks for ngrams (where n is specified to a value)
# composed of them in a word-tokenised text.
# Needs improvement.
def keywords2ngrams(keywords, text, n):
    win_start = 0
    win_end = n
    mylist = []
    mylist2 = []
    mylist3 = []
    while 1:
        win_words = text[win_start:win_end] # text[0:3] which is really text[0:3-1]
        if len(win_words) == n:
            if n == 3:
                if win_words[0] in keywords and win_words[1] in keywords and win_words[2] in keywords:
                    if win_words not in mylist:
                        mylist.append(win_words)
                    elif win_words not in mylist2:
                        mylist2.append(win_words)
                    elif win_words not in mylist3:
                        mylist3.append(win_words)
                    else:
                        mylist = mylist
                win_start += 1
                win_end += 1
            elif n == 2:
                if win_words[0] in keywords and win_words[1] in keywords:
                    if win_words not in mylist:
                        mylist.append(win_words)
                    elif win_words not in mylist2:
                        mylist2.append(win_words)
                    elif win_words not in mylist3:
                        mylist3.append(win_words)
                    else:
                        mylist = mylist
                win_start += 1
                win_end += 1                
        else:
            break            
    #return mylist # Return those phrases that occur at least 2 times
    return mylist2 # Return those phrases that occur at least 2 times
    #return mylist3 # Return those phrases that occur at least 3 times
    


# Function: sort_betweenness_scores
# Sort the keywords in descending order of importance.
def sort_betweenness_scores(betweenness_scores, nf):
    temp0 = betweenness_scores.items()
    temp1 = [(x,y) for (y,x) in temp0]
    temp1.sort()
    list.reverse(temp1)
    return temp1

# Function: pre_process_essay_ke  
# Do all text processing necessary before keywords are identified.
def pre_process_essay_ke(text0,nf,nf2,dev):
    # Get the body of the essay. 
    # Currently this is everything occurring before the references section but it needs improvement/refinment.
    text1, refs_comment = get_essay_body(text0,nf,dev)     

    # Split the essay body on whitespace so that you can correct some the encoding. Although this isn't needed for sentence splitting, it is needed for the correction of some characters. I have just copied the same function from the sentence splitting program.
    text2 = re.split(r' ', text1)

    # Deal with odd characters in the text.		
    
    temp1 = tidy_up_text(text2)    
    
    # Following latin9 tidy-up, un-split the body of the essay ready for sentence splitting.
    temp2 = ' '.join(temp1) 

    # Word-tokenise the body of the essay (splits off punctuation marks as well).
    wordtok_text = WordPunctTokenizer().tokenize(temp2)
    
    # Part-of-speech tag the word-tokenised essay.
    text3 = pos_tag(wordtok_text)
    
    # Remove tokens that are punctuation marks or series of punc marks.        
    text4 = [w for w in text3 if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'\"!,;:/-]+', w[0])]

    # Put essay into lower case.
    text5 = [(w[0].lower(),w[1]) for w in text4]

    # Get the English stopwords from NLTK corpus.
    eng_stopwords = stopwords.words('english')

    # Remove the stopwords.
    finished_text = [(w[0],w[1]) for w in text5 if w[0] not in eng_stopwords]

    return finished_text, wordtok_text

# Function: process_essay_ke  
# Derive keywords
def process_essay_ke(text,wordtok_text,nf,nf2,dev):
    # Grab only the tokens that you want.
    text = filter_unwanted_words(text)

    # Replace each word with its stem. Note: Whether and when to stem needs serious thought.
    #text = get_word_stems(text7)

    # Get the wordset for the essay.
    unique_word_set = unique_everseen([x[0] for x in text])

    # Initiate an empty directed graph 'gr' of 'digraph' class  
    # Digraphs are directed graphs built of nodes and directed edges.
    gr=nx.DiGraph() 
    
    # Add nodes to the directed graph 'gr', one node for each unique word.
    # If you are filtering out certain parts of speech, you will add a node only for those remaining unique words.
    gr.add_nodes_from(list(unique_word_set)) # Leave this in for the betweenness centrality version.
    
    # Add directed edges to the graph to which you have alreaded added nodes. 
    # A directed (and unweighted) edge is added from each node/word to the word/node that follows it in the prepared text.
    add_all_node_edges_ke(gr, text)

    # Calculate the betweenness centrality score for each node in the graph.
    betweenness_scores = betweenness_centrality(gr)        
    
    # Sort the scores into order.
    di = sort_betweenness_scores(betweenness_scores, nf) # Leave this in for the betweenness centrality version.

    # Get the ranked words but without the scores.	
    words = [item[1] for item in di]

    # How many words are in the wordset? And then divide that by some integer. TextRank paper says a third of wordset are keywords.
    x = len(words)

    # Set var 'keywords' to the top x of the ranked words.
    keywords = words[:x]

    # Make key phrases by looking for series of key words in original text (that is, after word-tokenisation but before punc and stops are removed).
    trigram_keyphrases = keywords2ngrams(keywords,wordtok_text,3)
    bigram_keyphrases = keywords2ngrams(keywords,wordtok_text,2)

    return text, di,keywords, bigram_keyphrases, trigram_keyphrases, gr

# Function: debora_results_ke
# Print results that I am interested in.  
def debora_results_ke(filtered_text, di,keywords,bigram_keyphrases,trigram_keyphrases,nf,nf2):
    # The next few lines are using the NLTK tools. This is done to make a comparisons.

    # Remove the POS tags from the fully processed text.
    t4 = [w[0] for w in filtered_text] # Remove the tags so that the collocation finder is working on plain tokenised text that has the same content as the keywords text.

    # Run some NLTK analyses to compare with your results.
    bcf = BigramCollocationFinder.from_words(t4)
    bicolls = bcf.nbest(BigramAssocMeasures.likelihood_ratio, 200)

    tcf = TrigramCollocationFinder.from_words(t4)
    tricolls = tcf.nbest(TrigramAssocMeasures.likelihood_ratio, 200)

    fdist = FreqDist(t4)    
    freqdist = fdist.keys()

    # Write the results of executing your Python program to the new file you created earlier.
    nf.write('\nTop 50 key words in descending order of importance:\n\n')
    nf.write(str(keywords[:50]))
    nf.write('\n\n')        

    #nf2.write('\n')
    #nf2.write('Top 50 key words in descending order of importance:')
    #nf2.write('\n')
    #nf2.write(str(keywords[:50]))
    #nf2.write('\n')        

    nf.write('\nStraight frequency distribution (from NLTK) for comparison:\n\n')
    nf.write(str(freqdist[:50]))
    nf.write('\n\n')
    
    nf.write('\nAll bigram key phrases that occur at least twice:\n\n')
    nf.write(str(bigram_keyphrases))
    nf.write('\n\n')        

    nf2.write('\n')        
    nf2.write('All bigram key phrases that occur at least twice:\n')
    nf2.write(str(bigram_keyphrases))
       
    nf2.write('\n\nAll trigram key phrases that occur at least twice:\n')
    nf2.write(str(trigram_keyphrases))        
    nf2.write('\n\n*******************************************************\n\n')
    
    nf.write('\nAll trigram key phrases that occur at least twice:\n\n')
    nf.write(str(trigram_keyphrases))        
    nf.write('\n\n')

    nf.write('\nTop 10 trigram collocations (from NLTK) for comparison:\n\n')
    nf.write(str(tricolls[:10]))
    nf.write('\n\n')        

    s = str(di) # Map the results into a string so you can write the string to the output file
    w = re.sub('\'\),', '\'),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    y = re.sub('\"\),', '\'),\n', w) # Be careful, because Python sometimes uses double quotes instead of single ones    
    nf.write('\nKey words and their scores:\n\n')
    nf.write(y)    


# Needs improvement.
def keywords2ngramsNVL(keywords, text, n):
    win_start = 0
    win_end = n
    mylist = []
    mylist2 = {}
    
    keywords1 = [w[0] for w in keywords]
    keywords2 = [w[1] for w in keywords]
    keywords3 = []
    if n == 3:
        keywords3 = [w[2] for w in keywords]
    while 1:
        win_words = text[win_start:win_end] # text[0:3] which is really text[0:3-1]
        if len(win_words) == n:
            if n == 3:
                if win_words[0] in keywords1 and win_words[1] in keywords2 and win_words[2] in keywords3:
                    if win_words not in mylist:
                        mylist.append(win_words)
                        mylist2[''.join(win_words)] = {'ngram':win_words,'count':1}
                        print win_words
                    else:
                        elt = mylist2[''.join(win_words)]['count']
                        mylist2[''.join(win_words)]['count'] = elt + 1;
                        print win_words
                win_start += 1
                win_end += 1
            elif n == 2:
                if win_words[0] in keywords1 and win_words[1] in keywords2:
                    if win_words not in mylist:
                        #_apiLogger.info(">> split : %s" % win_words)
                        mylist.append(win_words)
                        mylist2[''.join(win_words)] = {'ngram':win_words,'count':1};
                    else:
                        elt = mylist2[''.join(win_words)]['count']
                        mylist2[''.join(win_words)]['count'] = elt + 1;
                        #_apiLogger.info(">> split : %s (%d)" %( win_words, n+1))
                win_start += 1
                win_end += 1                
        else:
            break            
    #return mylist # Return those phrases that occur at least 2 times
    return mylist2 # Return those phrases that occur at least 2 times
    #return mylist3 # Return those phrases that occur at least 3 times


def nicolas_results_ke(text0):

    processed_text, wordtok_text = pre_process_essay_ke(text0,None,None,'NVL')

    filtered_text, di,keywords, bigram_keyphrases, trigram_keyphrases, gr = process_essay_ke(processed_text, wordtok_text, None,None,'NVL')


    # Get frequency distribution
    t4 = [w[0] for w in filtered_text] # Remove the tags so that the collocation finder is working on plain tokenised text that has the same content as the keywords text.
    fdist = FreqDist(t4)    
    freqdist = fdist.keys()

    # Count the number of occurences of n-grams
    tt2 = keywords2ngramsNVL(bigram_keyphrases,wordtok_text,2)
    tt3 = keywords2ngramsNVL(trigram_keyphrases,wordtok_text,3)

    # Get an associative array out of the keywords list    
    mapkeyscore = {}
    for (score, word) in di:
        mapkeyscore[word] = score

    # build a list of n-grams with their score and count
    list2grams = []
    for win_words in bigram_keyphrases:
        gg = ''.join(win_words)
        kk = tt2[gg]['count']
        i1 = mapkeyscore[win_words[0]]
        i2 = mapkeyscore[win_words[1]]
        list2grams.append({'ngram':win_words,'count':kk,'score':[i1,i2]})

    list3grams = []
    for win_words in trigram_keyphrases:
        gg = ''.join(win_words)
        kk = tt3[gg]['count']
        i1 = mapkeyscore[win_words[0]]
        i2 = mapkeyscore[win_words[1]]
        i3 = mapkeyscore[win_words[2]]
        list3grams.append({'ngram':win_words,'count':kk,'score':[i1,i2,i3]})

    list1grams = []
    for win_words in keywords[:25]:
        kk = fdist[win_words]
        i1 = mapkeyscore[win_words]
        list1grams.append({'ngram':[win_words],'count':kk,'score':[i1]})

    data1 = json_graph.adjacency_data(gr)
    data2 = json_graph.node_link_data(gr)
    
    essay = {}
    
    essay['keywords'] = list1grams
    essay['freqdist'] = freqdist[:25]
    #essay['bigram_keyphrases'] = bigram_keyphrases[:]
    #essay['trigram_keyphrases'] = trigram_keyphrases
    essay['bigrams'] = list2grams[:]
    essay['trigrams'] = list3grams[:]
    #essay['di'] = di
    essay['graph_adjacency'] = data1
    essay['graph_node_link'] = data2
 
    return essay