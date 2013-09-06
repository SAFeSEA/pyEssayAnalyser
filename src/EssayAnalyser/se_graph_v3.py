#import networkx as nx # This is for implementing networks/graphs
#import itertools
#import re
from operator import itemgetter

"""
This file contains the functions for building and analysing the sentence graph.
Functions names:
def add_item_to_array(myarray, num, item):
def add_to_sentence_array(myarray, text):
def fill_sentence_array(myarray, text, struc_labels):
def make_edge_weights_arrays(myarray, myWarray, myCarray):
def find_cosine_similarity(counter1,counter0,myWarray,myCarray,dev):
def add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray,dev):
def add_all_node_edges(gr,myWarray,myCarray,nf2,dev):    
def find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i):  
def find_all_gw_scores(gr, scores_array, nf2, dev, d = .85, max_iterations = 100, min_delta = 0.0000000001):
def update_array(myarray,scores_array):
def reorganise_array(myarray):
def sort_ranked_sentences(mylist):
def make_sentence_graph_nodes(myarray,text,section_labels,parasenttok):
def add_sentence_graph_edges(gr_se,myarray,myWarray,myCarray,nf2,dev):
def find_sentence_graph_scores(gr_se,myarray,scores_array,nf2,dev):
def sample_nodes_for_figure(graph,nodes,cat):
"""
# Function: add_item_to_array(myarray, num, item)
# Add single item 'item' as a new item in 'myarray',
# or as a detail of an existing item. 
# Called by 'fill_sentence_array' and 'make_edge_weights_arrays' and 'update_array'.
def add_item_to_array(myarray, num, item):
    if myarray.has_key(num): # If num is one of the keys already in the array...
        myarray[num].append(item) # append 'item' (add 'item' as a detail to an already existing entry).
    else:
        myarray[num] = [item] # Otherwise add this item as new entry in the array.

# Function: add_to_sentence_array(myarray, text)
# Add each original sentence as a detail to an entry in the 'myarray'
# initialised and filled earlier. This is done so that we can return the original
# sentence to the user in the results.
# Called by make_sentence_graph_nodes in this file.
def add_to_sentence_array(myarray, text):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            add_item_to_array(myarray, counter, sent)  # Add the counter'th sentence to the array with counter as its key
            counter += 1        


# Function: fill_sentence_array(myarray, text, struc_labels)
# Add each word-tokenised sentence as an entry in the empty 'myarray'
# initialised earlier. This is done partly so that each sentence has an index/key
# pointing to it, so that we can build a graph using numbers as nodes instead of
# actual sentences as nodes. The structure label of each sentence is also added
# to the array entry of that sentence.
# Called by make_sentence_graph_nodes in this file.
# xxxx Now that I am labelling the 'discussion' before I get to this point, I am simplifying this rule.
# Everything goes into the array with the label it has gained by this point.
def fill_sentence_array(myarray, text, struc_labels):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            if sent != []:            
                place = struc_labels.index(sent[0][0]) # Get the label of the sentence
                label = struc_labels[place]
                temp = sent[1:] # Get everything in the sent after the label
                add_item_to_array(myarray, counter, temp) # Add the sent to the array
                add_item_to_array(myarray, counter, label) # add the label to the array at the same key
                counter += 1
            else:
                counter += 1


##def fill_sentence_array(myarray, text, struc_labels):
##    counter = 0 # Sentence counter to add as key in array
##    for para in text:
##        for sent in para:
##            #if sent != [] and sent[0] != '#-s:p#' and sent[0] != '#-s:n#' and sent[0] != '#-s:h#' and sent[0] != '#-s:t#' and sent[0] != '#-s:q#' and sent[0] != '#dummy#':            
##            if sent != [] and sent[0][0] != '#dummy#' and sent[0][0] != '#+s#':  # If sent is anything but a true sentence
##                place = struc_labels.index(sent[0][0]) # Get the label of the sentence
##                label = struc_labels[place]
##                temp = sent[1:] # Get everything in the sent after the label
##                add_item_to_array(myarray, counter, temp) # Add the sent to the array
##                add_item_to_array(myarray, counter, label) # add the label to the array at the same key
##            # Everything is labelled 'dummy' in the first instance. Here things still labelled 'dummy' are relabelled '#+s#' for 'true sentence'.                
##            elif sent != [] and (sent[0][0] == '#dummy#' or sent[0][0] == '#+s#'): # I am keeping 'dummy' for the time being but may get rid of it. 
##                temp = sent[1:]
##                add_item_to_array(myarray, counter, temp)
##                add_item_to_array(myarray, counter, '#+s#')                  
##            counter += 1            
            
# Function:  make_edge_weights_arrays(myarray, myWarray, myCarray)
# Fill the empty array 'myWarray' with the unique lemmas for each sentence
# and fill the other empty array 'myCarray' with their numbers of occurrences.
# There is one entry in 'myWarray' for each sentence. Each entry contains every
# unique lemma in that sentence. Similarly there is one entry in 'myCarray' for
# each sentence. Each entry is the number of occurrences of the lemma that occurs
# in that same position in 'myWarray'.
# Called by add_sentence_graph_edges in this file.
#['#-s:q#','#-s:t#','#-s:s#','#-s:h#','#-s:H#','#-s:b#',
# '#-s:e#','#-s:c#','#-s:d#','#-s:l#','#+s:i#','#+s:c#',
# '#+s#', '#dummy#', '#+s:p#','#-s:n#','#-s:p#']

def make_edge_weights_arrays(myarray, myWarray, myCarray):
    sentencecounter = 0
    while 1:
        #if sentencecounter == 246:    
        if sentencecounter <= len(myarray)-1:
            tidysent = myarray[sentencecounter][0]
            label = myarray[sentencecounter][1]           
            if tidysent == []:
                add_item_to_array(myWarray, sentencecounter, '$$$$EMPTY_SENT_TOKEN$$$$')
                add_item_to_array(myCarray, sentencecounter, 0)
            # xxxx This para takes punctuation '#-s:p#',
            # numerics '#-s:n#', special headings '#-s:h#', title '#-s:t#',
            # assignment question sentences '#-s:q#', general headings '#-s:H#', list itemisers '#-s:b#',
            # and table entries '#-s:e#' and captions'#-s:c#'  out of the sentence graph.
            # Long bullet points are earlier labelled as true sentences.
            elif (label == '#-s:p#' or label == '#-s:n#'
                  or label == '#-s:h#' or label == '#-s:t#'
                  or label == '#-s:q#' or label == '#-s:H#' or label == '#-s:s#'
                  or label == '#-s:d#' or label == '#-s:l#' 
                  or label == '#-s:b#' or label == '#-s:e#' or label == '#-s:c#'
                  or label == '#dummy#'): # Currently including abstract/preface in sentence graph
                  #or label == '#+s:p#' or label == '#dummy#'): # xxxx this line commented out for RANLP because I need abstract to be included in graphs. Sections following conclusion are unrecognised and labelled 'dummy'..                    
                add_item_to_array(myWarray, sentencecounter, '$$$$NOT_A_TRUE_SENTENCE$$$$')
                add_item_to_array(myCarray, sentencecounter, 0)
            else:
                wordcounter = 0
                monitorlist = []
                for w in tidysent:
                    if w[1] not in monitorlist:
                        c = sum(1 for w in tidysent if w[1] == tidysent[wordcounter][1])
                        #add_item_to_array(myWarray, sentencecounter, w[0]) # fill myWarray with the words
                        add_item_to_array(myWarray, sentencecounter, w[1]) # fill myWarray with the lemmas
                        add_item_to_array(myCarray, sentencecounter, c)
                        monitorlist.append(w[1])
                        wordcounter += 1
                    else:
                        wordcounter += 1
            sentencecounter += 1
        elif sentencecounter > len(myarray)-1:
            break   

# Function: find_cosine_similarity(counter1,counter0,myWarray,myCarray,dev)
# Calculate the similarity of a pair of sentences using cosine similarity
# as a distance measure. 
# Called by 'add_one_nodes_edges'.
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
def find_cosine_similarity(counter1,counter0,myWarray,myCarray,dev):
    vector_s1 = []
    vector_s0 = [] 
    printlist1 = [] # For monitoring
    printlist0 = []
    for w in myWarray[counter1]: # For each word w in sent1 (a sentence)...
        listposition_x = myWarray[counter1].index(w) # Get the list position of w in sent1 from the Word array
        score_x = myCarray[counter1][listposition_x] # Get the score for w in sent 1 from the Count array
        if w in myWarray[counter0]: # If word w is also in sent0...
            listposition_y = myWarray[counter0].index(w) # Get the list position of w in sent 0 from the Word array
            score_y = myCarray[counter0][listposition_y] # Get the score for w in sent 0 from the Count array
            vector_s1.append(score_x) # Add the score for sent1 to a list (a vector)
            vector_s0.append(score_y) # And again for sentence 0
            printlist1.append((w,score_x)) # For sent1, add the word and its score to a list for printing out
            printlist0.append((w,score_y)) # And the same for sent0
        else: # Otherwise (if word w is not in sent0)...
            vector_s1.append(score_x)  # Add the found score to the vector for sent1
            vector_s0.append(0) # and add zero as the score for that word to the vector for sent0
            printlist1.append((w,score_x)) # Update the printing lists in a similar way. For monitoring.
            printlist0.append((w,0))
    for w in myWarray[counter0]: # Now repeat the process for sent0, but...
        if w not in myWarray[counter1]: # make sure this word has not already been dealt with above in processing for sent1...
            listposition_y = myWarray[counter0].index(w) # Get the list position of w in sent0 from the Word array
            score_y = myCarray[counter0][listposition_y] # Get the score for w in sent0 from the Count array                
            vector_s1.append(0) # Add zero as the score for this word to the vector for sent1
            vector_s0.append(score_y) # And add the found score to the vector for sent0
            printlist1.append((w,0)) # Update the printing lists in a similar way. For monitoring.
            printlist0.append((w,score_y))
    mydotproduct = sum(p*q for p,q in zip(vector_s1, vector_s0)) # Get the dot product of the two vectors
    if mydotproduct == 0: # To speed up the process. If mydotproduct is 0 (no similarity), no need to do any further sums with it. Profiler revealed that 'sum' was being called rather a lot.
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
            if dev == 'DGF':
                print '\n ********* product of magnitudes for these sentences equals zero *********'
                print myWarray[counter1], myWarray[counter0]
        else:
            result = mydotproduct / product_of_magnitudes # Cosine similarity
    #print myWarray[counter1], myCarray[counter1], '\n'        
    return result 


# Function: add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray,dev)
# Add weighted and directed 'to' edges for one node in a graph
# that you have already initiated, and to which you have added the appropriate nodes.
# Called by add_all_node_edges.
# If the calculated similarity weight is zero, do not add an edge.
# I have tried a number of different ways of calculating the weight of an edge.
# Currently I am using cosine similarity.
# xxxx Note that, rather than an undirected graph, I was using
# a combination of a bias towards the beginning (backwards-directed)
# and a bias towards the end (forwards-directed).
# This meant that there were two edges going between all linked nodes, which was hardly ideal.
# I did this, because the original TextRank equation relies on the directed nature of edges.
# I have now changed the code to produce an undirected graph.
# I have had to amend the TextRank algorithm accordingly.
# Instead of 'predecessors' and 'out-degree' I am using 'neighbours' and 'degree'.
# The results of using an undirected graph with the amended TextRank algorithm
# are exactly the same as using a directed graph biased in both directions by using two sets of directed edges,
# Processing times for the directed version and the undirected version are very similar.
# For TMA01 essays, directed is slightly faster than undirected.
# For EMA essays (much longer), undirected is slightly faster than directed.

def add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray,dev):
    counterA = 0 # For counting zero-weight edges
    while 1:
        if counter1 <= (len(myWarray) - 1) and counter1 != counter0: # Stop looping when counter1 (instantiated earlier) reaches the total number of sentences and make sure 'from' and 'to' nodes are not the same node.
            weight = float(find_cosine_similarity(counter1,counter0,myWarray,myCarray,dev))
            if weight > 0:
                gr.add_weighted_edges_from([(counter1,counter0,weight)]) # xxxx @directedness - both 'directed backards' and 'undirected'. Add the current edge with the weight you have calculated. This line adds the backwards-directed edges for the current node (counter0).
                #gr.add_weighted_edges_from([(counter0,counter1,weight)]) # xxxx Do not delete. This line adds forwards-directed edges in a directed graph. The above line adds backwards edges.  Directed graph version.
            elif weight == 0: # Count the number of zero-weight edges you are making (for monitoring)
                counterA += 1
            counter1 += 1
        elif counter1 == counter0: # If the 'from' and 'to' nodes are the same node, increment the 'from' node and carry on (don't join a node to itself).
            counter1 += 1
        else:
            return counterA # For this node (counter0), return the number of edges added with weight == 0. For monitoring.

# Function: add_all_node_edges(gr,myWarray,myCarray,nf2,dev)
# Add all the weighted and directed edges to a graph that you have already initiated,
# and to which you have already added the appropriate nodes.
# Note that this involves finding which nodes should be joined by an edge, which in turn
# requires every pair of nodes/sentences in the graph to be compared in order to derive
# a similarity score. That part is carried out by 'add_one_nodes_edges'.
# Called by add_sentence_graph_edges in this file.
def add_all_node_edges(gr,myWarray,myCarray,nf2,dev):    
    mylist = []
    counter1 = 0
    counter0 = 0
    zeroweights = []
    while 1:
        if counter0 <= (len(myWarray) - 1) and counter1 > counter0: # Stop looping when the counter reaches the total number of sentences
            # ... plus the first/'from' node in a pair must be greater (later in the text/graph) than the second/'to' node in this case to reflect directedness: later nodes can point to earlier ones, but not vice versa
            zeroweights = add_one_nodes_edges(gr, counter1, counter0, myWarray,myCarray,dev) # Add all the edges for one node (the 'to' node)
            counter0 += 1 # Increment the 'to' node
        elif counter1 <= counter0: # If the 'from' node is smaller/= the 'to' node
            counter1 += 1
        else:
            break
    mylist.append(zeroweights) # For counting zero-weight edges
    #print gr.edges() # Nicolas, this will show you the edges so you can see the difference that edge direction makes.
    if mylist == [[]]: # edge case condition. If no zeroweight edges. Otherwise sum below will fail.
        mylist = []
    sumzeroweights = sum(mylist) # Just keeping tabs on how many zero-weight edges there are.
    


# Function: find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i)
# Find the global weight score WSVi for one node Vi in graph gr.
# Called by 'find_all_gw_scores'.
# The equation this function is based on is on the second page of (Mihalcea and Tarau, 2004).
# Vi is a single node in the graph.
# d is damping factor set to .85.
# graph_size is the number of nodes in the graph.
# 'min_value' is (1.0-d)/graph_size.
# i is just for monitoring.
def find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i):  
    score = 0 # Set a temporary score to zero to enable calculations of the rhs of the TextRank equation
    list0 = gr.predecessors(Vi) # xxxx @directedness 'directed'. Do not delete. Find out which nodes point to Vi, i.e., ALL its predecessors. Directed graph.
    #list0 = gr.neighbors(Vi) # xxxx @directedness 'undirected'. Find out which nodes link Vi to other nodes, i.e., ALL its NEIGHBOURS. 
    if list0 == []: # If Vi has no predecessors 
        WSVi = min_value # Set WSVi to the minimum value
        #print 'If clause: No nodes point to this Vi so WSVi set to minimum value:'
        #print '\n'
        return WSVi # Return the minimum value as the WSVi global weight score result
    else:    
        for Vj in list0: # For each node Vj that points to Vi
            w = gr[Vj][Vi]['weight'] # Get the weight of the edge Vj->Vi from the graph
            WoutVj = gr.out_degree(Vj,weight='weight') # xxxx @directedness 'directed'. Do not delete. Find each edge Vj->Vk that points out of Vj and sum their weights to give WoutVj. Directed graph version.
            #WoutVj = gr.degree(Vj,weight='weight') # xxxx @directedness 'undirected' Find each edge Vj->Vk that links Vj to other nodes and sum their weights to give WoutVj. Undirected graph.
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

# Function: find_all_gw_scores(gr, scores_array, nf2, dev, d = .85, max_iterations = 100, min_delta = 0.00001)
# Find the global weight score WSVi for all nodes Vi in the graph gr.
# Do this by first setting WSVi scores for all nodes to some arbitrary value
#(done before we get to here, 'scores_array' has been filled with arbitrary scores).
# Then call 'find_global_weight_score' for each Vi to get a new value for WSVi,
# and update 'scores_array' with the new value.
# It is necessary to set arbitrary values in the first instance because the
# procedure for finding a WSVi score requires you to find a WSVi score, i.e.,
# it is recursive. So you need some values in order to be able to start.
# The arbitrary values move closer towards the real values at every iteration
# until an inconsequential difference is made by further iterations.
# We also set some parameters.
# Set 'damping factor' 'd' to .85 as per (Mihalcea and Tarau, 2004) paper and (Brin and Page 1998). 
# Mihalcea presents a justification for using the same value for 'd' as PageRank uses, but I am not yet completely convinced by it.
# Set a threshold 'max_iterations' to constrain the number of times find_all_gw_scores is consecutively called in order to calculate the WSVi scores.
# Set a value 'min_delta' to help measure how different the current WSVi score is from the WSVi score at the last iteration.
# Called by find_sentence_graph_scores in this file.
#def find_all_gw_scores(gr, scores_array, nf2, dev, d = .85, max_iterations = 100, min_delta = 0.00001):
def find_all_gw_scores(gr, scores_array, nf2, dev, d = .85, max_iterations = 100, min_delta = 0.0000000001):
    nodes = gr.nodes() # Make a list of the graph's nodes
    graph_size = len(nodes) # Find the size of the graph, meaning the number of the graph's nodes. 
    try:
        min_value = (1.0-d)/graph_size # Set a minimum WSVi score value for nodes without inbound links, i.e., = .15/graph_size. This idea is taken directly from pagerank.py.
    except ZeroDivisionError:
        print '\nZero division error: no nodes in graph\n'
        min_value = (1.0-d)/1
    #for i in range(3):  # Set low for testing purposes.
    for i in range(max_iterations):  # Only go round this loop max_iterations (100) times for each node.
        #print '######################################'
        #print '############ iteration number#########'
        #print i, '\n'
        counter = 0
        diff = 0 # Set a variable to keep track of the size of the difference between this score and the score in previous iteration.
        #list.reverse(nodes) # xxxx temporary switch for testing
        for Vi in nodes: # For each node Vi in the graph...
            WSVi = find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i) # ...find its global weight score, i carried for printing/debugging.
            #if Vi < 100:
                #print '\nNode', Vi
                #print 'This is min_delta', min_value
                #print 'This is the old diff', diff
                #print 'This is the old WSVi score)', scores_array[Vi]
                #print 'This is the new WSVi score)', WSVi
            diff += abs(scores_array[Vi] - WSVi) # Increment 'diff' with the difference between this score and the score calculated in the last iteration.
            # Note that 'diff' is the sum of _all_ the differences for _every_ node in this iteration. Only when the sum of these is very small is convergence achieved.
            scores_array[Vi] = WSVi # Update the scores_array with this new score value in place of the old one.
            #if Vi < 100:
                #print 'This is the new diff, which is incremented by the old WSVi score minus the new WSVi score', diff
                #print 'This is min_delta', min_delta 
            counter += 1
        if diff < min_delta: # If the difference between this score and score in previous iteration is less than .00001 (min_delta)...
            if dev == 'DGF':
                print '############ iteration number#########', i
                #print 'SUCCEEDS: diff < min_delta', diff, min_delta
            break # ... stop
    return scores_array

# Function: update_array(myarray,scores_array)
# Add the WSVi scores to the array created right at the beginning
# that contains the processed and the original sentences. For printing the results out.
# Called by find_sentence_graph_scores in this file.
def update_array(myarray,scores_array):
    temp = list(myarray)
    for Vi in temp:         
        WSVi = scores_array[Vi] # Get the score for Vi from the scores array
        add_item_to_array(myarray,Vi,WSVi) # And add it to 'myarray'  
            
# Function: reorganise_array(myarray)
# Make a structure containing the results presented with the WSVi score
# first, then the array key, then the original sentence.
# Called by find_sentence_graph_scores in this file.
# {0: [[(u'introduction', u'introduction')], ('#-s:h#', '0'), u'Introduction', 0.0025862068965517245], 
def reorganise_array(myarray):
    #print '\n\n\nreorganise_array'
    #print myarray
    mylist = []
    counter = 0
    while 1:
        if counter <= len(myarray)-1: # 0: [[(u'introduction', u'introduction')], '#-s:h#', u'Introduction', 0.0025862068965517245]
            temp = myarray.items() # Retrieve the contents of the array in a different format.
                     # rank               # array key       # category           # original sentence  # processed sentence
            #temp1 = (round(temp[counter][1][3],7), temp[counter][0], temp[counter][1][1], temp[counter][1][2], temp[counter][1][0] ) # xxxx do not delete. Put rank first, then key, then category label, then original sentence (before word tokenisation ff.), then processed sentence.
            temp1 = ( temp[counter][1][3], temp[counter][0], temp[counter][1][1], temp[counter][1][2], temp[counter][1][0] ) #  xxxx Switch to the above line if you want to round off the scores. Be careful because very large texts get much lower scores, and rounding can render all scores equal.
            mylist.append(temp1)
            counter += 1
        else:
            break
    #for item in mylist:
    #    print item
    return mylist

# Function: sort_ranked_sentences(mylist)
# The array has now been turned into a list for results purposes.
# This function now removes from the list all items except for introduction, discussion, conclusion items.
# Then sorts the remaining sentences into descending WSVi rank order. 
# Returns the list of true sentences in descending rank order.
# Called by find_sentence_graph_scores in this file.
def sort_ranked_sentences(mylist):
    mylist = [item for item in mylist if item[2] == '#+s#' or item[2] == '#+s:i#' or item[2] == '#+s:c#' or item[2] == '#+s:p#'] # or item[2] == '#dummy#' # xxxx 'dummy' and '+s:p' included for RANLP. # or item[2] == '#-s:h#']  # or item[2] == '#-s:t#'or item[2] == '#-s:q#']
    mylist.sort() # ... and sort the structure according to its first argument (WSVi score)
    list.reverse(mylist)
    #values = set(map(lambda x:x[1], mylist)) # This routine groups the things sorted into lists if they have the same sort value
    #newlist = [[y for y in mylist if y[1]==x] for x in values]
    return mylist

# Function: make_sentence_graph_nodes(myarray,text,section_labels,parasenttok):
def make_sentence_graph_nodes(myarray,text,section_labels,parasenttok):
    fill_sentence_array(myarray, text, section_labels) # Fill array 'myarray' with the fully processed version of the text, one sentence per entry in the array. Each sentence is thus associated with an array key number which represents its position in the text.
    add_to_sentence_array(myarray, parasenttok)     # Add each original unprocessed sentence to 'myarray' at the appropriate key point, so they can be returned in the user feedback later. 'Unprocessed' means following tidy-up, after sentence tokenisation, but before word tokenisation and all the other pre-processing

# Function: add_sentence_graph_edges(gr_se,myarray,myWarray,myCarray,nf2,dev):
# Add all the appropriate weighted and directed edges to the
# graph that you have already initiated, and to which you have
# added the appropriate nodes. This requires comparison of pairs
# of sentences/nodes in order to calculate the weight of the edge
# that joins them.   
def add_sentence_graph_edges(gr_se,myarray,myWarray,myCarray,nf2,dev):
    make_edge_weights_arrays(myarray, myWarray, myCarray)
    add_all_node_edges(gr_se,myWarray,myCarray,nf2,dev)

# Function: find_sentence_graph_scores(gr_se,myarray,scores_array,nf2,dev):   
def find_sentence_graph_scores(gr_se,myarray,scores_array,nf2,dev):
    find_all_gw_scores(gr_se, scores_array, nf2, dev)
    update_array(myarray,scores_array)
    reorganised_array = reorganise_array(myarray)
    ranked_global_weights = sort_ranked_sentences(reorganised_array)
    return ranked_global_weights,reorganised_array
    
# Function: sample_nodes_for_figure(graph,nodes,cat)
# Derives a smaller sample graph from the main graph
# for the purposes of making a graphic.
# Called both to make a smaller sentence graph and a smaller key word graph.
# In the case of the sentence graph, 'nodes' is the true sentences.
# There are too many key sentences to make a nice figure, so these are cut down in a systematic way.
# In the case of the the key word graph, 'nodes' is the key lemmas.
# These are also cut down but in a different way from the key sentences.
def sample_nodes_for_figure(graph,nodes,cat):
    #if cat == 'se':
        #print graph.nodes() # xxxx do not delete
        #print nodes # xxxx do not delete
    #all_edges = graph.edges(data = True) # Get a list of all the graph's edges (expressed like '(21, 47, {'weight': 0.2891574659831202})')
    mylist = []
    for item in nodes:
        successors = len(graph.successors(item)) # xxxx Do not delete. Get the length of the list of successors for each node. Directed graph version.
        #successors = len(graph.neighbors(item)) # xxxx Get the length of the list of neighbours for each node. Undirected version.
        #print 'Number of neighbours for node: ', item, ' : ', successors
        if successors > 2: #>= 0:  # > 2 # Currently I am including nodes that don't have any successors, so they would appear in the graph as unconnected nodes.
            mylist.append([item,successors])
    #print mylist # [17, 45], [18, 39], [19, 45],
    temp0 = sorted(mylist, key = itemgetter(1)) # Sort the list of nodes in order of length of list of successors    
    list.reverse(temp0) # Re-sort from greatest to smallest so that the sample graph contains the node with the most successors
    #temp1 = [i[0] for i in temp0] # Make a new list with just the nodes in.
    temp1 = [i[0] for i in mylist] # Make a new list with just the nodes in.
    if cat == 'se': # If this function is called to sample the sentence graph
        #temp2 = temp1[::4] # Get every Nth node item in temp1, starting with the first. These are going to be the nodes in the sentence sample graph.
        #x = (len(nodes) / 6)# + (len(nodes) / 4)
        #y = x*5
        #temp2 = nodes[x:y] # gets the middle 2/3 portion of the essay (so without the intro and the concl)
        #temp2 = temp1
        #temp2 = nodes
        temp2 = temp1
    elif cat == 'ke': # If this function is called to sample the key word graph
        #x = len(nodes)#/3
        temp2 = nodes # Get the top third of the key lemmas sorted in order of centrality score. These are going to be the nodes in the key word sample graph.
    graph_sample = graph.subgraph(temp2) # Make a subgraph using only the nodes you want for the figure
    return graph_sample
