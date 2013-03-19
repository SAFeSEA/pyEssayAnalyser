import networkx as nx # This is for implementing networks/graphs
"""
This file contains the functions for building and analysing the sentence graph.
Functions names:
# Function: add_item_to_array(myarray, num, item)
# Function: add_to_sentence_array(myarray, text)
# Function: fill_sentence_array(myarray, text, struc_labels)
# Function: make_scores_array
# Function: make_graph_building_arrays(myarray, myWarray, myCarray)
# Function: find_cosine_similarity(counter1,counter0,myWarray,myCarray,dev)
# Function: add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray,dev)
# Function: add_all_node_edges(gr,myWarray,myCarray,nf2,dev)
# Function: find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i)
# Function: find_all_gw_scores(gr, scores_array, nf2, dev, d = .85, max_iterations = 100, min_delta = 0.00001)
# Function: update_array(myarray,scores_array)
# Function: reorganise_array(myarray)
# Function: sort_ranked_sentences(mylist)

"""
# Function: add_item_to_array(myarray, num, item)
# Add single item 'item' as a new item in 'myarray',
# or as a detail of an existing item. 
# Called by 'fill_sentence_array' and 'make_graph_building_arrays' and 'update_array'.
def add_item_to_array(myarray, num, item):
    if myarray.has_key(num): # If num is one of the keys already in the array...
        myarray[num].append(item) # append 'item' (add 'item' as a detail to an already existing entry).
    else:
        myarray[num] = [item] # Otherwise add this item as new entry in the array.

# Function: add_to_sentence_array(myarray, text)
# Add each original sentence as a detail to an entry in the 'myarray'
# initialised and filled earlier. This is done so that we can return the original
# sentence to the user in the results.
# Called by process_essay_se in se_procedure.py
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
# Called by process_essay_se in se_procedure.py
def fill_sentence_array(myarray, text, struc_labels):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            #if sent != [] and sent[0] != '#-s:p#' and sent[0] != '#-s:n#' and sent[0] != '#-s:h#' and sent[0] != '#-s:t#' and sent[0] != '#dummy#':            
            if sent != [] and sent[0][0] != '#dummy#':
                place = struc_labels.index(sent[0][0]) # Get the label of the sentence
                label = struc_labels[place]
                temp = sent[1:] # Get everything in the sent after the label                                
                add_item_to_array(myarray, counter, temp) # Add the sent to the array
                add_item_to_array(myarray, counter, label) # add the label to the array at the same key
            elif sent != [] and sent[0][0] == '#dummy#': # I am keeping 'dummy' for the time being but may get rid of it. Everything is labelled 'dummy' in the first instance, but I could label everything '#+s#'.
                temp = sent[1:]                
                add_item_to_array(myarray, counter, temp)
                add_item_to_array(myarray, counter, '#+s#')                  
            counter += 1
                
# Function:  make_graph_building_arrays(myarray, myWarray, myCarray)
# Fill the empty array 'myWarray' with the unique lemmas for each sentence
# and fill the other empty array 'myCarray' with their numbers of occurrences.
# There is one entry in 'myWarray' for each sentence. Each entry contains every
# unique lemma in that sentence. Similarly there is one entry in 'myCarray' for
# each sentence. Each entry is the number of occurrences of the lemma that occurs
# in that same position in 'myWarray'.
# Called by process_essay_se in se_procedure.py.
def make_graph_building_arrays(myarray, myWarray, myCarray):
    sentencecounter = 0
    while 1:
        #if sentencecounter == 246:    
        if sentencecounter <= len(myarray)-1:
            tidysent = myarray[sentencecounter][0]
            label = myarray[sentencecounter][1]           
            if tidysent == []:
                add_item_to_array(myWarray, sentencecounter, '$$$$EMPTY_SENT_TOKEN$$$$')
                add_item_to_array(myCarray, sentencecounter, 0)
            # xxxx This para takes punctuation, numbers, headings, and title out of the graph. Done now to make visual graphics of graph. May keep.
            elif label == '#-s:p#' or label == '#-s:n#' or label == '#-s:h#' or label == '#-s:t#':
                add_item_to_array(myWarray, sentencecounter, '$$$$NOT_A_TRUE_SENTENCE$$$$')
                add_item_to_array(myCarray, sentencecounter, 0)
            else:
                wordcounter = 0
                monitorlist = []
                for w in tidysent:
                    if w[1] not in monitorlist:
                        c = sum(1 for w in tidysent if w[1] == tidysent[wordcounter][1])
                        add_item_to_array(myWarray, sentencecounter, w[1])
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
    return result 


# Function: add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray,dev)
# Add weighted and directed 'to' edges for one node in a graph
# that you have already initiated, and to which you have added the appropriate nodes.
# Called by add_all_node_edges.
# If the calculated similarity weight is zero, do not add an edge.
# I have tried a number of different ways of calculating the weight of an edge.
# Currently I am using cosine similarity.
def add_one_nodes_edges(gr, counter1, counter0,myWarray,myCarray,dev):
    counterA = 0 # For counting zero-weight edges
    while 1:
        if counter1 <= (len(myWarray) - 1) and counter1 != counter0: # Stop looping when counter1 (instantiated earlier) reaches the total number of sentences and make sure 'from' and 'to' nodes are not the same node.
            weight = float(find_cosine_similarity(counter1,counter0,myWarray,myCarray,dev))
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
            return counterA # For this node (counter0), return the number of edges added with weight == 0. For monitoring.

# Function: add_all_node_edges(gr,myWarray,myCarray,nf2,dev)
# Add all the weighted and directed edges to a graph that you have already initiated,
# and to which you have already added the appropriate nodes.
# Note that this involves finding which nodes should be joined by an edge, which in turn
# requires every pair of nodes/sentences in the graph to be compared in order to derive
# a similarity score. That part is carried by 'add_one_nodes_edges'.
# Called by process_essay_se in se_procedure.py.
def add_all_node_edges(gr,myWarray,myCarray,nf2,dev):    
    mylist = []
    counter1 = 0
    counter0 = 0
    while 1:
        if counter0 <= (len(myWarray) - 1) and counter1 > counter0: # Stop looping when the counter reaches the total number of sentences
            # ... plus the first/'from' node in a pair must be greater (later in the text/graph) than the second/'to' node in this case to reflect directedness: later nodes can point to earlier ones, but not vice versa
            zeroweights = add_one_nodes_edges(gr, counter1, counter0, myWarray,myCarray,dev) # Add all the edges for one node (the 'to' node)
            mylist.append(zeroweights) # For counting zero-weight edges
            counter0 += 1 # Increment the 'to' node
        elif counter1 <= counter0: # If the 'from' node is smaller/= the 'to' node
            counter1 += 1
        else:
            break
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
    list0 = gr.predecessors(Vi) # Find out which nodes point to Vi, i.e., ALL its predecessors.
    if list0 == []: # If Vi has no predecessors 
        WSVi = min_value # Set WSVi to the minimum value
        return WSVi # Return the minimum value as the WSVi global weight score result
    else:    
        for Vj in list0: # For each node Vj that points to Vi
            w = gr[Vj][Vi]['weight'] # Get the weight of the edge Vj->Vi from the graph
            WoutVj = gr.out_degree(Vj,weight='weight') # Find each edge Vj->Vk that points out of Vj and sum their weights to give WoutVj.
            # (We know that at least one edge points out of Vj, the one towards Vi, so no need for empty list alternative)
            WSVj = scores_array[Vj] # Get the most recent WS score from 'scores_array' for Vj (these are seeded right at the beginning with an arbitrary value)
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
# Called by process_essay_se in se_procedure.py.
def find_all_gw_scores(gr, scores_array, nf2, dev, d = .85, max_iterations = 100, min_delta = 0.00001):
    nodes = gr.nodes() # Make a list of the graph's nodes
    graph_size = len(nodes) # Find the size of the graph, meaning the number of the graph's nodes. 
    min_value = (1.0-d)/graph_size # Set a minimum WSVi score value for nodes without inbound links, i.e., = .15/graph_size. This idea is taken directly from pagerank.py.
    #for i in range(3):  # Set low for testing purposes.
    for i in range(max_iterations):  # Only go round this loop max_iterations (100) times for each node.
        diff = 0 # Set a variable to keep track of the size of the difference between this score and the score in previous iteration.
        #list.reverse(nodes)
        for Vi in nodes: # For each node Vi in the graph...
            WSVi = find_global_weight_score(Vi, gr, d, min_value, graph_size, scores_array, i) # ...find its global weight score, i carried for printing/debugging.
            diff += abs(scores_array[Vi] - WSVi) # Increment 'diff' with the difference between this score and the score calculated in the last iteration.
            scores_array[Vi] = WSVi # Update the scores_array with this new score value in place of the old one.
        if diff < min_delta: # If the difference between this score and score in previous iteration is less than .00001 (min_delta)...
            if dev == 'DGF':
                print 'Final iteration number:'
                print i+1
            break # ... stop
    return scores_array

# Function: update_array(myarray,scores_array)
# Add the WSVi scores to the array created right at the beginning
# that contains the processed and the original sentences. For printing the results out.
# Called by process_essay_se in se_procedure.py.
def update_array(myarray,scores_array):
    temp = list(myarray)
    for Vi in temp:         
        WSVi = scores_array[Vi] # Get the score for Vi from the scores array
        add_item_to_array(myarray,Vi,WSVi) # And add it to 'myarray'  
            
# Function: reorganise_array(myarray)
# Make a structure containing the results presented with the WSVi score
# first, then the array key, then the original sentence.
# Called by process_essay_se in se_procedure.py.
def reorganise_array(myarray):
    mylist = []
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
    return mylist

# Function: sort_ranked_sentences(mylist)
# The array has now been turned into a list for results purposes.
# This function now removes from the list all items labelled as 'not a sentence': '#-s...#'
# Then sorts the remaining sentences into descending WSVi rank order. 
# Returns the list of true sentences in descending rank order.
# Called by process_essay_se in se_procedure.py.
def sort_ranked_sentences(mylist):
    temp = [item for item in mylist if item[2] == '#-s:p#' or item[2] == '#-s:n#' or item[2] == '#-s:h#' or item[2] == '#-s:t#']
    sorted_list = [item for item in mylist if item not in temp]
    sorted_list.sort() # ... and sort the structure according to its first argument (WSVi score)
    list.reverse(sorted_list)
    return sorted_list
