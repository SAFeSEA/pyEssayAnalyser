import re
import itertools
#from pygraph.classes.exceptions import AdditionError
#import networkx as nx
#from nltk.stem.lancaster import LancasterStemmer


"""
Function names (in addition to the functions that are imported):
get_essay_body(text,nf)
tidy_up_latin9(text)
filter_unwanted_words(tagged)
unique_everseen(iterable)
add_all_node_edges(gr, text)
keywords2trigrams(keywords, text)
keywords2bigrams(keywords, text)
sort_betweenness_scores(betweenness_scores, nf)
"""

# Function: Get the body of an essay.
# Currently this gets all that occurs before the bibliography
#(actually before the last occurrence of the term 'references' (or ...)). 
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
# I have tried various ways of using a disjunction for this, but have not yet succeeded.
def get_essay_body(text,nf=None):
    if 'References' in text:
        a = text.rfind('References') # Find the LAST occurrence of 'References', not the first, in case there is a contents page or other xref.
        #a = text.index("References") # Find the FIRST occurrence of 'References'.
        b = text[:a] # Get all the text of the essay occurring before the bibliography (the body).
        return b    
    elif 'REFERENCES' in text:
        a = text.rfind("REFERENCES") 
        b = text[:a] 
        return b
    elif 'Reference' in text: # One essay I looked at had the bibliography section title: 'Reference list'.
        a = text.rfind("Reference") 
        b = text[:a] 
        return b
    elif 'REFERENCE' in text: # One essay I looked at had: 'REFERENCE'.
        a = text.rfind("REFERENCE") 
        b = text[:a] 
        return b          
    elif 'Bibliography' in text:
        a = text.rfind("Bibliography") 
        b = text[:a] 
        return b
    else:
        if nf is not None:
            nf.write('\n********* Cannot find a references section. *********\n') 
        return text # If none of those terms are in text, just return text.
                        
# Function: Replaces some non-ASCII characters with an ASCII substitute.
# Also reformats some terms that use a full stop for abbreviation.
def tidy_up_text(text):
    counter = 0
    text = [re.sub('^i\.e\.', "ie", w) for w in text] # 
    text = [re.sub('^e\.g\.', "eg", w) for w in text] # 'e.g.' with 'eg'
    text = [re.sub('^e-', "e", w) for w in text] # 'e-' with 'e'
    temp_6 = [re.sub('\\xfc', "o", w) for w in text] # 'u umlaut' 
    temp_5 = [re.sub('\\xf6', "o", w) for w in temp_6] # 'o umlaut' 
    temp_4 = [re.sub('\\xb9', "", w) for w in temp_5] # footnote marker     
    temp_3 = [re.sub('\\xe9', "e", w) for w in temp_4] # 'e accute' 
    temp_2 = [re.sub('\\xa3', "GBP ", w) for w in temp_3] # British pound sign
    temp_1 = [re.sub('\\xa0', " ", w) for w in temp_2] 
    return temp_1

# Function: Removes tokens that have the POS categories that you are not interested in,
# i.e., those tokens/words that you don't want to become nodes in your graph.
# Also removes words you don't want that are not removed by the stop words procedure.

def filter_unwanted_words(tagged, tags=['CD','LS','MD','RB','RBR','RBS','SYM','WRB']):
#def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):    
    temp = [item for item in tagged if item[1] not in tags]
    mylist = ['et', 'al', 'eg', 'ie', 'etc', 'may', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
              'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
              '&' ]
    return [item for item in temp if item[0] not in mylist]

# Function: Replaces each word with its stem. This needs a lot of thought concerning when it
# should be done, and what should then be returned to the user.
##def get_word_stems(text):
##    st = LancasterStemmer()
##    mylist = []
##    for w in text:
##        temp = st.stem(w[0])
##        mylist.append((temp, w[1]))
##    print 'This is mylist', mylist
##    return mylist


# Function: Lists unique elements, preserving order. Remember all elements ever seen.
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

# Function: Adds the appropriate edges between nodes you have already added
# to your graph. Given one POS-tagged token/vertex i, up to how far away
# in the POS-tagged list (how many tokens away) from that token are you
# going to look  for a token/vertex j to connect to i? This function currently
# says start at position 0 (first token) for i, finish at position 1 (2-1) for j
# (so the immediately following token), add the edge i->j to the graph, then
# increment start and finish positions and repeat.
def add_all_node_edges(gr, text):
    window_start = 0
    window_end = 2
    while 1:
        window_words = text[window_start:window_end]
        if len(window_words) == 2:
            #print window_words
            try: # 'add_edge' is defined in 'pygraph\classes\digraph'
                gr.add_edges_from([(window_words[0][0], window_words[1][0])])                                
            except ValueError: 	
                # AdditionError is a class defined in 'pygraph\classes\exceptions'
                # Stops an edge being added where there already is one.
                #print 'already added %s, %s' % ((window_words[0][0], window_words[1][0]))
                True				
        else:
            break
        window_start += 1
        window_end += 1

# Function: Takes a list of keywords and looks for trigrams
# composed of them in a word-tokenised text.
def keywords2trigrams(keywords, text):
        win_start = 0
        win_end = 3
        mylist = []
        mylist2 = []
        mylist3 = []
        while 1:
                win_words = text[win_start:win_end] # text[0:3] which is really text[0:3-1]
                if len(win_words) == 3:
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
                else:
                        break            
        #return mylist # Return those phrases that occur at least 2 times
        return mylist2 # Return those phrases that occur at least 2 times
        #return mylist3 # Return those phrases that occur at least 3 times

# Function: Takes a list of keywords and looks for bigrams
# composed of them in a word-tokenised text.		
def keywords2bigrams(keywords, text):
        win_start = 0
        win_end = 2        
        mylist = []
        mylist2 = []
        mylist3 = []
        while 1:
                win_words = text[win_start:win_end] # text[0:3] which is really text[0:3-1]
                if len(win_words) == 2:    
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

def sort_betweenness_scores(betweenness_scores, nf=None):
    temp0 = betweenness_scores.items()
    temp1 = [(x,y) for (y,x) in temp0]
    temp1.sort()
    list.reverse(temp1)
    return temp1

    
