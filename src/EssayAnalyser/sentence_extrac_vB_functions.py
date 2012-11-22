import re # For regular expressions
#import math 
#import random # Needed if I seed scores_array with random numbers instead of the same number
from nltk.corpus import stopwords # For removing uninteresting words from the text
#from nltk import PunktSentenceTokenizer 
from nltk.tokenize import WordPunctTokenizer # Word tokeniser that separates punctuation marks from words

""""
Functions:
get_essay_body(text,nf)
restore_quote(text, counter)
tidy_up_latin9(text)
word_tokenize(text)
remove_punc_fm_sents(text)
count_words(text)
lowercase_sents(text)
remove_stops_fm_sents(text)
remove_numeric_sents(text)
label_headings(text)
add_item_to_array(myarray, num, item)
add_to_sentence_array(myarray, text)
fill_sentence_array(myarray, text)
make_graph_building_arrays(myarray, myWarray, myCarray)
find_cosine_similarity(counter1,counter0, myWarray, myCarray)
add_one_nodes_edges(gr, counter1, counter0, myWarray, myCarray)
add_all_node_edges(gr,myWarray,myCarray,nf2)
find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i)
find_all_gw_scores(gr, d, max_iterations, min_value, min_delta, graph_size, nodes, scores_array, nf, nf2)
update_array(myarray,scores_array)
rank_weight_scores(myarray, nf, nf2)
"""

# Function: Get the body of an essay.
# Currently this gets all that occurs before the bibliography
#(actually before the last occurrence of the term 'references' (or ...)). 
# Note: This v simple procedure needs changing/improving.
# E.g., we want to skip over title, author name, contents page, etc.
# E.g., this will match the last occurrence of 'References' (or ...) anywhere
# in the document, inc. within the references or the essay body.
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
# I have tried various ways of using a disjunction for this, but have not yet succeeded.
def get_essay_body(text,nf):
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
        nf.write('\n********* Cannot find a references section. *********\n') 
        return text # If none of those terms are in text, just return text.

# Function: Reinstate the SECOND of a pair of quotation marks.
# Note: Be careful to skip over word-initial question marks,
# which are the beginning of embedded quotations.
# Called by 'tidy_up_latin9'.
def restore_quote(text, counter):
    while 1:
        if counter <= len(text)-1:        
            x = text[counter]
            if not x.startswith('?'): # We need the 'not x.startswith...' because there may be an embedded quotation and we are looking for the closing speech/question mark of a pair.
                if x.endswith('?.'): # For 'dizzy?.' cases
                    y = re.sub('\?.', "'.", x) 
                    list.remove(text, x) # Substitute the new string you have made for the old string.
                    list.insert(text, counter, y) # (There must be a better way of doing this.)
                    return text             
                elif x.endswith('?,'): # "dizzy?," becomes "dizzy',"
                    y = re.sub('\?,', "',", x)
                    list.remove(text, x)
                    list.insert(text, counter, y)
                    return text             
                elif x.endswith('?;'): # "dizzy?;" becomes "dizzy';" 
                    y = re.sub('\?;', "';", x)
                    list.remove(text, x)
                    list.insert(text, counter, y)
                    return text             
                elif x.endswith('?:'): # "dizzy?:" becomes "dizzy':"
                    y = re.sub('\?:', "':", x)
                    list.remove(text, x)
                    list.insert(text, counter, y)
                    return text             
                elif x.endswith('?'):  # "dizzy?" becomes "dizzy'" and "that??" becomes "that?'".      
                    y = re.sub('\?$', "'", x)
                    list.remove(text, x)
                    list.insert(text, counter, y)
                    return text           
                else: # If x doesn't start with '?' but doesn't have any of these endings, try the next word
                    counter += 1
            else: # If x does start with '?', try the next word
                counter += 1
        else:
            break # Stop when you get to the end of the text.
                        
# Function: Text saved in encoding Latin9 substitutes a question mark for
# curly speech marks and curly apostrophes and en-dashes and em-dashes.
# This function replaces dashes with hyphens and puts back apostrophes and speech marks.
# It does not cover every case, but it does a reasonable job.
def tidy_up_latin9(text):
    counter = 0
    temp_1 = [re.sub('\\xa0', " ", w) for w in text]
    temp_0 = [re.sub('\t', " ", w) for w in temp_1] # Just getting rid of tab characters that are attached to words
    temp = [re.sub('\?t$', "'t", w) for w in temp_0] # Apostrophe: "don?t" becomes "don't"
    temp0 = [re.sub('^\?$', "--", w) for w in temp]   # Em-dashes and en-dashes: 'access ? enrolment' becomes 'access -- enrolment'
    temp1 = [re.sub('\?s$', "'s", w) for w in temp0]   # Apostrophe: "Frankenstein?s" becomes "Frankenstein's"
    while 1: # Now deal with quotation marks (that come in pairs), starting with the first of the pair here.
        if counter <= len(temp1): # Note that you cannot now just replace every question mark with a quotation mark, because some questions marks really are questions marks.
            for x in temp1:
                if x.startswith('?'):
                    place = temp1.index(x) # Find the position of x in the text
                    y = re.sub('^\?', "'", x) # Deal with the word-initial question mark. "?lost?", and, "?dizzy?." become "'lost?", 'and', "'dizzy?."
                    list.remove(temp1, x) # Substitute the new string you have made for the old string
                    list.insert(temp1, place, y)
                    restore_quote(temp1, place) # Find where the closing quote (qmark) of the pair should be and put quote mark back 
                    counter += 1 
                else:
                    counter += 1
        else:
            break
    return temp1

# Function: Word-tokenise a paragraph-sentence-tokenised text.
# There are different word tokenisers available in NLTK. This one
# "divides a text into sequences of alphabetic and non-alphabetic characters".
# This means that punctuation marks are represented as separate tokens from
# the words they adjoin.
# This tokeniser uses quotation marks as word delimiters.
# In the output square brackets are now used to delimit paragraphs AND sentences.
def word_tokenize(text):
    mylist = []
    for para in text:
         temp = [WordPunctTokenizer().tokenize(t) for t in para]
         mylist.append(temp)
    return mylist
 

# Function: Remove from a para-sent-word-tok text all word-tokens that are
# punctuation marks or series of punctuation marks. 
def remove_punc_fm_sents(text):
    mylist2 = []
    for para in text:
        mylist1 = []    # Note: be careful to make sure you put this in the right place to preserve the bracketing correctly
        for sent in para:
            temp = [w for w in sent if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', w)]
            mylist1.append(temp)
        mylist2.append(mylist1)
    return mylist2

# Function: Count the words in a text.
# This is done after word tokenisation and after removal of punctuation.
def count_words(text):
    mylist = []
    for para in text:
        for sent in para:
            x = sum(1 for w in sent)
            mylist.append(x)
    y = sum(mylist)
    return y
    
# Function: For each sentence in a para-sent-word-tok text,
# put all word tokens into lower case.
def lowercase_sents(text):
    mylist2 = []
    for para in text:
        mylist1 = []
        for sent in para:
            temp = [str.lower(w) for w in sent]
            mylist1.append(temp)
        mylist2.append(mylist1)
    return mylist2

# Function: For each sentence in a para-sent-word-tok text,
# remove all word tokens that are stopwords
# (uninteresting and usually very frequent words).
def remove_stops_fm_sents(text):
    eng_stopwords = stopwords.words('english') # Get the English stopwords from NLTK corpus
    mylist2 = []
    for para in text:
        mylist1 = []
        for sent in para:
            temp = [w for w in sent if w not in eng_stopwords]
            mylist1.append(temp)
        mylist2.append(mylist1)
    return mylist2

# Function: From each sentence that contains only one word token
# remove that single word if it contains numbers (resulting in an empty sentence)
def remove_numeric_sents(text):
    mylist2 = []
    for para in text:
        mylist1 = []
        for sent in para:
            if len(sent) == 1:
                temp = [w for w in sent if not re.search('[0-9]+',w)]
                mylist1.append(temp)
            else:
                mylist1.append(sent)               
        mylist2.append(mylist1)
    #print mylist2
    return mylist2

        
# Function: For each paragraph that contains only one sentence,
# if the sentence contains less than 5 words, it may well be a heading.
#(It could also be a bullet point. Watch this.)
# Label headings so that later on you can exclude them from the results
# returned to the user, but don't exclude them from the ranking calculations.
def label_headings(text):
    mylist2 = []
    for para in text:
        mylist1 = []
        if len(para) == 1: # If the paragraph has exactly one sentence in it
            for sent in para:
                if len(sent) <= 4: #...and that sentence has less than 4 words in it
                    temp = ['*-s*'] + sent
                    mylist1.append(temp) # put it in a list for removal from the rankings later after scores have been calculated
                    #print temp
                else:
                    mylist1.append(sent)
            mylist2.append(mylist1)        
        else:
            mylist2.append(para)
                    #print sent            
    #print 'This is label_headings: ', mylist2[:20]
    return mylist2

# Function: Add single item 'item' as a new item in 'myarray',
# or as a detail of an existing item. Called by 'fill_sentence_array'.
# Called by 'fill_sentence_array' and 'make_graph_building_arrays' and 'update_array'.
def add_item_to_array(myarray, num, item):
    if myarray.has_key(num): # If num is one of the keys already in the array...
        myarray[num].append(item) # append 'item' (add 'item' as a detail to an already existing entry).
    else:
        myarray[num] = [item] # Otherwise add this item as new entry in the array.

# Function: Add each original sentence as a detail to an entry in the 'myarray'
# initialised and filled earlier. This is done so that we can return the original
# sentence to the user in the results.
def add_to_sentence_array(myarray, text):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            add_item_to_array(myarray, counter, sent)  # Add the counter'th sentence to the array with counter as its key
            counter += 1        

# Function: Add each word-tokenised sentence as an entry in the empty 'myarray'
# initialised earlier. This is done partly so that each sentence has an index/key
# pointing to it, so that we can build a graph using numbers as nodes instead of
# actual sentences as nodes.
def fill_sentence_array(myarray, text):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            if sent != [] and sent[0] == '*-s*':
                temp = sent[1:]
                add_item_to_array(myarray, counter, temp)
                add_item_to_array(myarray, counter, '*-s*')  # Add the counter'th sentence to the array with counter as its key
            else:
                add_item_to_array(myarray, counter, sent)
                add_item_to_array(myarray, counter, '*+s*')  # Add the counter'th sentence to the array with counter as its key                
            counter += 1

# Function: Seed the empty 'scores_array' with randomly generated scores.
# This is an alternative to seeding it with the same score for every node.
##def make_scores_array(scores_array, nodes, random_scores):
##    counter = 0
##    for x in nodes:
##        scores_array[x] = random_scores[counter]
##        counter += 1        

# Function: Find the length of the longest sentence in a sent-word-tokenised text. 
# I was thinking about using this in the calculation of edge weights.
# Note that this is old and assumes no paragraph tokenisation.
##def find_longest_sentence(senttok):
##    mylist = []
##    for x in senttok:  # For each sentence in the sentence-tokenised text
##        a = senttok.index(x)        
##        y = len(x)
##        mylist.append((y, x, a))
##    mylist.sort
##    return mylist[0]


# Function: Fill the empty array 'myWarray' with the unique words for each sentence
# and fill the other empty array 'myCarray' with their numbers of occurrences.
# There is one entry in 'myWarray' for each sentence. Each entry contains every
# unique word in that sentence. Similarly there is one entry in 'myCarray' for
# each sentence. Each entry is the number of occurrences of the word that occurs
# in that same position in 'myWarray'.
def make_graph_building_arrays(myarray, myWarray, myCarray):
    sentencecounter = 0
    while 1:
        #if sentencecounter == 246:    
        if sentencecounter <= len(myarray)-1:
            tidysent = myarray[sentencecounter][0]
            #print tidysent, '\n'    
            if tidysent == []:
                add_item_to_array(myWarray, sentencecounter, '$$$$EMPTY_SENT_TOKEN$$$$')
                add_item_to_array(myCarray, sentencecounter, 0)
                # print '\n *********Sentence number', sentencecounter, 'is now empty ***********'
            else:
                wordcounter = 0
                monitorlist = []
                for w in tidysent:
                    #print 'this is w: ', w
                    if w not in monitorlist:
                        c = sum(1 for w in tidysent if w == tidysent[wordcounter])
                        #print 'total: ', c
                        add_item_to_array(myWarray, sentencecounter, w)
                        #print '\nIf clause:This is myWarray: ', myWarray
                        add_item_to_array(myCarray, sentencecounter, c)
                        #print '\nIf clause:This is myCarray: ', myCarray
                        monitorlist.append(w)
                        wordcounter += 1
                    else:
                        wordcounter += 1
            sentencecounter += 1
        elif sentencecounter > len(myarray)-1:
            break   
    #print '\nThis is myWarray: ', myWarray
    #print '\nThis is myCarray: ', myCarray
    
# Function: Calculate the similarity of a pair of sentences using cosine similarity
# as a distance measure. Called by 'add_one_nodes_edges'.
# Relies on two arrays 'myWarray' and 'myCarray' created earlier on. This function
# looks up the count values in 'myCarray' rather than counting each word in each
# sentence for every pairwise comparison. Doing it that way speeds up the program
# considerably for a 6K-word essay. It uses the word and count values in the two
# arrays to create a pair of vectors, one for each sentence in the pair.
# Basic cosine similarity algorithm:
#  1 Take the dot product of vectors s1 and s0.
#  2 Calculate the magnitude of Vector s1.
#  3 Calculate the magnitude of Vector s0.
#  4 Multiply the magnitudes of s1 and s0.
#  5 Divide the dot product of s1 and s0 by the product of the magnitudes of s1 and s0.
def find_cosine_similarity(counter1,counter0,myWarray,myCarray):
    vector_s1 = []
    vector_s0 = [] 
    printlist1 = [] # For monitoring
    printlist0 = []
    for w in myWarray[counter1]: # For each word w in sent1 (a sentence)...
        listposition_x = myWarray[counter1].index(w) # Get the list position of w in sent1 from the Word array
        score_x = myCarray[counter1][listposition_x] # Get the score for w in sent 1 from the Count array
        if w in myWarray[counter0]: # If word w is also in sent0...
            #print 'Looking up w in array to get count: ', w
            listposition_y = myWarray[counter0].index(w) # Get the list position of w in sent 0 from the Word array
            score_y = myCarray[counter0][listposition_y] # Get the score for w in sent 0 from the Count array
            vector_s1.append(score_x) # Add the score for sent1 to a list (a vector)
            vector_s0.append(score_y) # And again for sentence 0
            printlist1.append((w,score_x)) # For sent1, add the word and its score to a list for printing out
            printlist0.append((w,score_y)) # And the same for sent0
        else: # Otherwise (if word w is not in sent0)...
            #print 'Looking up w in array to get count: ', w
            #print 'This is array for sent1: ', sent1
            vector_s1.append(score_x)  # Add the found score to the vector for sent1
            vector_s0.append(0) # and add zero as the score for that word to the vector for sent0
            printlist1.append((w,score_x)) # Update the printing lists in a similar way. For monitoring.
            printlist0.append((w,0))
    for w in myWarray[counter0]: # Now repeat the process for sent0, but...
        if w not in myWarray[counter1]: # make sure this word has not already been dealt with above in processing for sent1...
            #print 'Looking up w in array to get count: ', w
            listposition_y = myWarray[counter0].index(w) # Get the list position of w in sent0 from the Word array
            score_y = myCarray[counter0][listposition_y] # Get the score for w in sent0 from the Count array                
            vector_s1.append(0) # Add zero as the score for this word to the vector for sent1
            vector_s0.append(score_y) # And add the found score to the vector for sent0
            printlist1.append((w,0)) # Update the printing lists in a similar way. For monitoring.
            printlist0.append((w,score_y))
    #print printlist1
    #print printlist0        
    #print 'Vectors:',
    #print vector_s0
    #if counter1 == 246:
        #print myWarray[counter1]
        #print vector_s1
        #print vector_s0
    mydotproduct = sum(p*q for p,q in zip(vector_s1, vector_s0)) # Get the dot product of the two vectors
    if mydotproduct == 0: # To speed up the process. If mydotproduct is 0 (no similarity), no need to do any further sums with it. Profiler revealed that 'sum' was being called rather a lot.
        #print '\n ********* mydotproduct == 0 *********'
        result = 0
    else:
        temp1 = sum(p**2 for p in vector_s1) # Get the magnitude of each vector
        temp2 = sum(p**2 for p in vector_s0)
        magnitude_of_s1 = temp1**(1.0/2) 
        magnitude_of_s0 = temp2**(1.0/2)
        product_of_magnitudes = magnitude_of_s1 * magnitude_of_s0 # Get the product of the magnitudes
    # Stray punctuation marks can become sentence tokens which then become empty lists when punc is removed.
    # ... which makes the product of magnitudes zero. In these cases, there is no similarity, so weight will == 0
        if product_of_magnitudes == 0:
        #    print 'succeeds 2'
        #    result = 0
            print '\n ********* product of magnitudes for these sentences equals zero *********'
            print myWarray[counter1], myWarray[counter0]
        else:
            result = mydotproduct / product_of_magnitudes # Cosine similarity
    #print 'Cosine similarity:',
    #print result 
    return result 


# Function: Add weighted and directed 'to' edges for one node in a graph
# that you have already initiated, and to which you have added the appropriate nodes.
# Called by add_all_node_edges.
# If the calculated similarity weight is zero, do not add an edge.
# I have tried a number of different ways of calculating the weight of an edge.
# Currently I am using cosine similarity.
def add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray):
    counterA = 0 # For counting zero-weight edges
    while 1:
        if counter1 <= (len(myWarray) - 1) and counter1 != counter0: # Stop looping when counter1 (instantiated earlier) reaches the total number of sentences and make sure 'from' and 'to' nodes are not the same node.
            weight = float(find_cosine_similarity(counter1,counter0,myWarray,myCarray))
            if weight > 0:
                gr.add_weighted_edges_from([(counter1,counter0,weight)]) # Add the current edge with the weight you have calculated. Uses imported NetworkX.
                #print 'This edge has been added to the graph:'
                #print [(counter1,counter0,weight)]
            elif weight == 0: # Count the number of zero-weight edges you are making (for monitoring)
                counterA += 1
            counter1 += 1
        elif counter1 == counter0: # If the 'from' and 'to' nodes are the same node, increment the 'from' node and carry on (don't join a node to itself).
            counter1 += 1
        else:
            #break
            return counterA # For this node (counter0), return the number of edges added with weight == 0. For monitoring.

# Function: Generate a list of random numbers smaller than 1, one random number per graph node.
##def random_scores_finder(nodes):
##    mylist = []
##    for x in nodes:
##        y = random.random()
##        mylist.append(y)
##    #print mylist
##    return mylist

# Function: Add all the weighted and directed edges to a graph that you have already initiated,
# and to which you have already added the appropriate nodes.
# Note that this involves finding which nodes should be joined by an edge, which in turn
# requires every pair of nodes/sentences in the graph to be compared in order to derive
# a similarity score. That part is carried by 'add_one_nodes_edges'.
def add_all_node_edges(gr,myWarray,myCarray,nf2):    
    mylist = []
    counter1 = 0
    counter0 = 0
    while 1:
        if counter0 <= (len(myWarray) - 1) and counter1 > counter0: # Stop looping when the counter reaches the total number of sentences
            # ... plus the first/'from' node in a pair must be greater (later in the text/graph) than the second/'to' node in this case to reflect directedness: later nodes can point to earlier ones, but not vice versa
            zeroweights = add_one_nodes_edges(gr, counter1, counter0, myWarray,myCarray) # Add all the edges for one node (the 'to' node)
            mylist.append(zeroweights) # For counting zero-weight edges
            counter0 += 1 # Increment the 'to' node
        elif counter1 <= counter0: # If the 'from' node is smaller/= the 'to' node
            counter1 += 1
        else:
            break
    sumzeroweights = sum(mylist) # Just keeping tabs on how many zero-weight edges there are.
    #print '\nNumber of sentence pair comparisons with edge weight 0 (sentence pairs with no similarity): ',
    #print sumzeroweights
    nf2.write(str(sumzeroweights))
    nf2.write(': Number of sentence pair comparisons with edge weight 0 (sentence pairs with no similarity)\n')
    


# Function: Find the global weight score WSVi for one node Vi in graph gr.
# Called by 'find_all_gw_scores'.
# The equation this function is based on is on the second page of (Mihalcea and Tarau, 2004).
# Vi is a single node in the graph.
# d is damping factor set to .85.
# graph_size is the number of nodes in the graph.
# 'min_value' is (1.0-d)/graph_size.
# i is just for monitoring.
def find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i):  
    #print 'Iteration:'
    #print i
    #print 'For Vi:'
    #print Vi
    score = 0 # Set a temporary score to zero to enable calculations of the rhs of the TextRank equation
    list0 = gr.predecessors(Vi) # Find out which nodes point to Vi, i.e., ALL its predecessors.
    if list0 == []: # If Vi has no predecessors 
        WSVi = min_value # Set WSVi to the minimum value
        #print 'If clause: No nodes point to this Vi so WSVi set to minimum value:'
        #print WSVi
        #print '\n'
        return WSVi # Return the minimum value as the WSVi global weight score result
    else:    
        for Vj in list0: # For each node Vj that points to Vi
            w = gr[Vj][Vi]['weight'] # Get the weight of the edge Vj->Vi from the graph
            WoutVj = gr.out_degree(Vj,weight='weight') # Find each edge Vj->Vk that points out of Vj and sum their weights to give WoutVj.
            # (We know that at least one edge points out of Vj, the one towards Vi, so no need for empty list alternative)
            WSVj = scores_array[Vj] # Get the most recent WS score from 'scores_array' for Vj (these are seeded right at the beginning with an arbitrary value)
            #print 'This is the most recent WSVj score:'
            #print WSVj
            #print 'in the calculation of WSVi for this node Vj:'
            #print Vj
            score = score + ( (gr[Vj][Vi]['weight'] * WSVj) / WoutVj )    # Do the rhs of the TextRank equation calculation               
    WSVi = ((1 - d) + (d * score))/graph_size # Do the final calculations 
    #rank += d * scores_array[Vj] / len(gr.successors(Vj) # The 'pagerank.py' version here for comparison (edges not weighted)
    return WSVi

# Function: Find the global weight score WSVi for all nodes Vi in the graph gr.
# Do this by first setting WSVi scores for all nodes to some arbitrary value
#(done before we get to here, 'scores_array' has been filled with arbitrary scores).
# Then call 'find_global_weight_score' for each Vi to get a new value for WSVi,
# and update 'scores_array' with the new value.
# It is necessary to set arbitrary values in the first instance because the
# procedure for finding a WSVi score requires you to find a WSVi score, i.e.,
# it is recursive. So you need some values in order to be able to start.
# The arbitrary values move closer towards the real values at every iteration
# until an inconsequential difference is made by further iterations.
def find_all_gw_scores(gr, d, max_iterations, min_value, min_delta, graph_size, nodes, scores_array, nf, nf2):
    #for i in range(3):  # Set low for testing purposes.
    for i in range(max_iterations):  # Only go round this loop max_iterations (100) times for each node.
        #print i
        diff = 0 # Set a variable to keep track of the size of the difference between this score and the score in previous iteration.
        #list.reverse(nodes)
        for Vi in nodes: # For each node Vi in the graph...
            WSVi = find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i) # ...find its global weight score, i carried for printing/debugging.
            diff += abs(scores_array[Vi] - WSVi) # Increment 'diff' with the difference between this score and the score calculated in the last iteration.
            scores_array[Vi] = WSVi # Update the scores_array with this new score value in place of the old one.
        if diff < min_delta: # If the difference between this score and score in previous iteration is less than .00001 (min_delta)...
            print 'Total number of sentences:'
            print len(nodes)
            print 'Final iteration number:'
            print i+1
            print '_____________________________________________'
            #nf2.write('Total number of sentences:')         
            #nf2.write(str(len(nodes)))
            #nf2.write('\n')                                    
            nf2.write('\nFinal iteration number:')                      
            nf2.write(str(i+1))
            nf2.write('\n')                    
            break # ... stop
    return scores_array

# Function: Add the WSVi scores to the array created right at the beginning
# that contains the processed and the original sentences. For printing the results out.
def update_array(myarray,scores_array):
    temp = list(myarray)
    #for Vi in nodes:
    for Vi in temp:         
        #print '\nThis is update_array: ', temp[Vi]
        WSVi = scores_array[Vi] # Get the score for Vi from the scores array
        add_item_to_array(myarray,Vi,WSVi) # And add it to 'myarray'  
            
# Function: Make a structure containing the results presented with the WSVi score
# first, then the array key, then the original sentence.
def rank_weight_scores(myarray, nf, nf2):
    mylist = []
    mylist2 = []
    counter = 0
    while 1:
        if counter <= len(myarray)-1:
            temp = myarray.items() # Retrieve the contents of the array in a different format.
                     # rank               # array key       # category           # original sentence  # processed sentence
            temp1 = (round(temp[counter][1][3],7), temp[counter][0], temp[counter][1][1], temp[counter][1][2], temp[counter][1][0] ) # Put rank first, then key, then category label, then original sentence (before word tokenisation ff.), then processed sentence.
            mylist.append(temp1)
            counter += 1
        else:
            break
    temp0 = [(a,b,c,d,e) for (a,b,c,d,e) in mylist if c == '*-s*'] # Print the headings to the essay results file.
    s = str(temp0) # Map headings list to a string
    w = re.sub('\]\),', ']),\n', s) # Add a new line at the end of every result.
    y = re.sub('\"\),', '\'),\n', w) # Be careful...
    nf.write('\n\nWhole paragraphs that are probably not sentences (headings, captions, ...): \n')
    nf.write(y)
    temp2 = [(a,b,c,d,e) for (a,b,c,d,e) in mylist if e != []] # Remove the now-empty sentences from the rankings    
    temp3 = [(a,b,c,d,e) for (a,b,c,d,e) in temp2 if c != '*-s*'] # Remove the array entries labeled 'heading' from the results to be returned to the user
    temp3.sort() # ... and sort the structure according to its first argument (WSVi score)
    list.reverse(temp3)
    for (a,b,c,d,e) in temp3: # Get only the sentence key numbers from the sorted scores list...
        mylist2.append(b)
    nf.write('\n\nRanked sentence order: (currently includes title (if the essay gives one) but not empty sentences (following processing) or headings, captions, ...)\n') 
    nf.write(str(mylist2)) # ...and write them to the results file so you can see the order at a glance.
    nf2.write('\nRanked sentence order:\n') 
    nf2.write(str(mylist2)) # ...and write them to the summary file as well.
    nf2.write('\n\nHighest-scoring sentence:')
    nf2.write('\n')
    nf2.write(str(temp3[0]))
    nf2.write('\nOne of the lowest-scoring sentence (usually more than one):')
    nf2.write('\n')
    temp4 = len(temp3)
    temp5 = temp4-1
    nf2.write(str(temp3[temp5]))
    nf2.write('\n')
    return temp3    

# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>














        
