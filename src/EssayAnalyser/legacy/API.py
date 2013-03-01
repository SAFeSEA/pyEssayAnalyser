'''  Handlers for the various API routes

@package API
@author: Nicolas Van Labeke (https://github.com/vanch3d)
@date: 22 Nov 2012
@version: 0.1
'''

from flask import request, jsonify
from uuid import uuid4

''' version 1 of essayAnalyser '''
import sentence_extrac_vB_functions as sentence
import keywords_functions_betweenness_v8 as keyword

''' version 2 of essayAnalyser '''
import sentence_extrac_v2_functions as sentence2
import keywords_functions_betweenness_v8b as keyword2

''' version 3 of essayAnalyser '''


from nltk.tokenize import LineTokenizer # "tokenizer that divides a string into substrings by treating any single newline character as a separator."
from nltk import PunktSentenceTokenizer # The standard sentence tokeniser used by NLTK
from nltk import FreqDist
import networkx as nx # This is for implementing networks/graphs

from nltk.tag import pos_tag
from nltk.tokenize import WordPunctTokenizer 
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import TrigramAssocMeasures
from networkx.algorithms.centrality.betweenness import betweenness_centrality

from EssayAnalyser import _apiLogger #, _tempDir
from time import time
#from EssayAnalyser import _eaTagger, se_main_v3
from operator import itemgetter
from nltk.data import load


## Process and segment the given text (string)
# @param text0: The text (string) to be processed
# @return: text,parasenttok (arrays)
#
def get_segmented_text(text0):
    
    text0 = unicode(text0)
    # Get the body of the essay. 
    # Currently this is everything occurring before the references section but it needs improvement/refinment.
    text1 = sentence.get_essay_body(text0)     

    # Split the essay body on whitespace so that you can correct the latin9 encoding before sentence splitting. 
    # Latin9 encoding puts questions marks everywhere, which confuses the sentence splitter. I reverse this split before sentence tokenisation. 
    text2 = sentence.re.split(r' ', text1)

    # Convert latin9-encoded text back into something very similar to the original text.        
    # Latin9 encoding substitutes a question mark for MS Word curly speech marks and curly apostrophes and en-dashes and em-dashes. Function 'tidy_up_latin9' replaces em- and en-dashes with hyphens and puts back apostrophes and speech marks.
    temp1 = sentence.tidy_up_latin9(text2)    

    # Following latin9 tidy-up, un-split the body of the essay ready for sentence splitting.
    temp2 = ' '.join(temp1) 
        
    # NVL : IMPORTANT ! 
    # NVL : NEED TO CONVERT TEXT TO STRING (UTF-8)
    # NVL : OTHERWISE YOU HAVE UNICODE TEXT (NOT SURE WHY YET) 
        
    # Paragraph-tokenise the result.
    # This results in having quotation marks as paragraph delimiters.
    paratok = LineTokenizer().tokenize(temp2)
    #print '\n\nThis is paratok: ', paratok[:10]

    
    # Sentence-tokenise the result.
    # This results in having quotation marks as sentence delimiters, and preserves the paragraph delimiters by using square brackets.
    parasenttok = [PunktSentenceTokenizer().tokenize(item) for item in paratok]        
                #print '\n\nThis is parasenttok: ', parasenttok[:30]            
                #m = sbd.load_sbd_model('C:/Python27/splitta.1.03/model_nb/', use_svm=False) # Playing with a different sentence splitter
                #senttok = sbd.sbd_text(m, temp2)

    # Word-tokenise the result.           
    text3 = sentence.word_tokenize(parasenttok)
    
    #f =1/0
    #print '\n\nThis is text3 after word tokenisation: ', text3[:30]

    # Remove all word-tokens that are punctuation marks or series of punctuation marks. 
    # This is done because we are not interested in the frequency or usage of punctuation apart from to divide text up into sentences, which has been done by now. 
    text4 = sentence.remove_punc_fm_sents(text3)
    #print '\n\nThis is text4 after punc removed: ', text4[:30]

    # Get all the paragraphs that are probably headings and set to a var for later.
    # Currently the sentence scores are worked out with the headings included in the sums, but the headings are not included in the final ranked list returned to the user. 
    # This is because the content of the headings is important, but the headings themselves cannot be key sentences.
    text5 = sentence.label_headings(text4)

    # Put all word-tokens into lower case. 
    # This is done so that the same word token represented in different cases will be counted as the same word. Note that this is done after sentence splitting in case capitalisation of sentence-initial words is used by sentence splitter.
    text6 = sentence.lowercase_sents(text5)
    #print '\n\nThis is text5 after lowercase: ', text5[:30]

    # Remove all word-tokens that are stop words. 
    # This is done because we are not interested in the frequency or usage of stop words, and because stop words are typically the most frequent words in prose. E.g., we don't want sentence N being returned as the most representative sentence in the text based on how the word 'the' is used.        
    text7 = sentence.remove_stops_fm_sents(text6)
    #print '\n\nThis is text after stops removed: ', text[:30]

    # From each sentence that contains only one word token, remove that single word if it contains numbers (resulting in an empty sentence)
    # This is done because we are probably not interested in sentences that are numbers (often entries in tables, list enumerators, etc.)), though this needs thought.
    # Note that I do not currently remove words that contain or constitute numbers when there are other 'proper' words in the sentence. This is because numbers are often used to convey content, they are not only used to delineate structure (e.g., list enumerators)
    # Note that I do not currently remove sentences and paragraphs that have by now become empty (owing to punctuation and stopwords and numbers being removed), because we need to remember the structure of the original document for the results.
    # Ho
    text = sentence.remove_numeric_sents(text7)
    return text,parasenttok
    
##
#
#
def process_essay():
    text0 = request.form['text']        # NVL : the text of the essay is extracted from the FORM part of the REQUEST, as received by the API
    
    
    # NVL : build the data structure for the JSON output
    essay = {}
    essay['essayID'] = str(uuid4())     # NVL : generate a random UUID for the essay (converted to string)

    text,parasenttok = get_segmented_text(text0)
    
    _apiLogger.info("text segmented:\t" + str(parasenttok))

    # Initialise an empty associative array (Python dict) that will hold the sentence- and word- tokenised sentences, each associated with an index key. 
    # This is done partly so that we can build a graph using numbers as nodes instead of actual sentences as nodes.
    myarray = {}  

    # Fill array 'myarray' with the fully processed version of the text, one sentence per entry in the array.
    # Each sentence is thus associated with an array key number which represents its position in the text.
    sentence.fill_sentence_array(myarray, text)

    # Add each original unprocessed sentence to 'myarray' at the appropriate key point, so they can be returned in the user feedback later.
    # 'Unprocessed' means following latin9 cleanup, after sentence tokenisation, but before word tokenisation and all the other pre-processing
    sentence.add_to_sentence_array(myarray, parasenttok) 

    # Now we start to build the graph in which the index key to each sentence (from 'myarray') is a node representing that sentence. 
    # We build a graph so that we can work out how strongly connected each sentence is to every other sentence in the graph/text on the basis of similarity of pairs of sentences.

    # Initiate an empty directed graph 'gr'.
    # A graph of class 'directed graph' meaning edges are directed, i.e., an edge points like an arrow from one node to another node. This class and 'nx' are from the package 'networkx' which needs to be imported at the start.
    # We use a directed graph encoded in a backwards direction (a node can only point to an earlier node) following some discussion on the penultimate page of (Mihalcea and Tarau, 2005). 
    gr=nx.DiGraph() 

    # Add the appropriate nodes to the empty graph.    
    # 'list(myarray)' lists only the keys from 'myarray', so this adds the keys from 'myarray' as nodes to the graph 'gr' that we have already defined and filled with the essay's sentences, one per key/node.
    gr.add_nodes_from(list(myarray)) 
    _apiLogger.info("nodes:\t" + str(gr.nodes()))

                
    # Initialise some empty arrays.
    myWarray = {} 
    myCarray = {}

    # Fill one array with the unique words in each sentence (i.e., remove repetitions) and fill the other array with their numbers of occurrences. There is one entry in each array for each sentence.            
    # This is done to speed up the graph-building process. In an essay with 280 sentences, every sentence is compared to every sentence that precedes it, that's about 39,200 comparisons. The arrays are used as look-up tables by the cosine similarity function that measures the similarity of a pair of sentences.
    sentence.make_graph_building_arrays(myarray, myWarray, myCarray)

    # Add all the appropriate weighted and directed edges to the graph that you have already initiated, and to which you have added the appropriate nodes. This requires comparison of pairs of sentences/nodes in order to calculate the weight of the edge that joins them.
    sentence.add_all_node_edges(gr,myWarray,myCarray)
    number_of_edges = len(gr.edges())
    
    _apiLogger.info("" + str(number_of_edges) + "\t: Total number of edges in the graph (pairs of sentences with some similarity)")
    possible_number_of_edges = ((len(myarray))**2)/2    
    _apiLogger.info("" + str(possible_number_of_edges) + " : Half the square of the number of sentences")

    _apiLogger.info("" + str(number_of_edges) + "\t: Total number of edges in the graph (pairs of sentences with some similarity)")
    _apiLogger.info("edges:\t" + str(gr.edges()))


    # Now we set some parameters to enable the calculation of the global weight score WSVi for each node Vi.

    # Set 'damping factor' d to .85 as per (Mihalcea and Tarau, 2004) paper and (Brin and Page 1998). 
    # Mihalcea presents a justification for using the same value for 'd' as PageRank uses, but I am not yet completely convinced by it.
    d = .85 

    # Set a threshold to constrain the number of times find_all_gw_scores is consecutively called in order to calculate the WSVi scores.
    max_iterations = 100 

    # Set a value to help measure how different the current WSVi score is from the WSVi score at the last iteration.
    min_delta = 0.00001 

    # Find the size of the graph, meaning the number of the graph's nodes. 
    graph_size = len(gr.nodes()) 

    # Set a minimum WSVi score value for nodes without inbound links, i.e., = .15/graph_size. 
    # This idea is taken directly from pagerank.py.
    min_value = (1.0-d)/graph_size 

    # Make a list of the graph's nodes for later use.
    nodes = gr.nodes()    

    # Initialise an array with WSVi score set to 1/graph_size (no. nodes) for all nodes.
    # The decision to use this number to seed scores_array is copied directly from pagerank.py. Beware the problem of massive numbers coming up in WSVi scores if initial scores are too high.
    scores_array = dict.fromkeys(nodes,1.0/graph_size)

    # These three lines should be commented in if I want to use random scores to seed 'scores_array' with. And the above line commented out.
    #random_scores = random_scores_finder(nodes)
    #scores_array = {}
    #make_scores_array(scores_array, nodes, random_scores)
    
    # And finally we get to calculate the WSVi global weight score for each node in the graph using parameters set above.
    # This function relies on all the processing done so far (the building of a directed graph with weighted edges using an essay as input).
    sentence.find_all_gw_scores(gr, d, max_iterations, min_value, min_delta, graph_size, nodes, scores_array)

    # Add the WSVi scores to the array created earlier that contains the original text before word-tokenisation. For printing the results out.       
    sentence.update_array(myarray,scores_array)
    
    # Make a structure containing the results, putting the WSVi rank first, then the array key, then the original sentence, for printing out.                
    ranked_global_weights = sentence.rank_weight_scores(myarray)

    # Write detailed results to the essay results file.        
    #s = str(ranked_global_weights) # Map the results into a string so you can write the string to the output file
    #w = re.sub('\'\),', '\'),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    #w = sentence.re.sub('\]\),', ']),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    #y = sentence.re.sub('\"\),', '\'),\n', w) # Be careful, because Python sometimes uses double quotes instead of single ones          

    # NVL : get the different pieces into the JSON data structure
    essay['parasenttok'] = parasenttok

    stats = {}
    stats['paragraphs'] = str(len(parasenttok))
    stats['sentences'] =  sum(w for w in [len(x) for x in parasenttok]) 
    stats['words'] = str(sentence.count_words(text))
    stats['nodes'] = str(len(nodes))
    stats['edges'] = str(number_of_edges)

    essay['stats'] = stats
    
    mylist2 = []
    
    top_ranked_global_weights = ranked_global_weights[:10]
    
    for (a,b,c,d,e) in top_ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        mylist2.append((a,b,c))
        
    essay['ranked'] = mylist2
    _apiLogger.info("test:\t")
   
    # NVL : return the JSON object
    return jsonify(essay)
    #return render_template('essay.html', essay=essay)

def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def process_dispersion():
    text0 = request.form['text']        # NVL : the text of the essay is extracted from the FORM part of the REQUEST, as received by the API
    #text0a = text0.encode('utf8')
    #text0b = text0.decode('utf8')
    
        
    # NVL : build the data structure for the JSON output
    essay = {}
    essay['essayID'] = str(uuid4())     # NVL : generate a random UUID for the essay (converted to string)
  
    # return the filtered text and paragraph/sentence structure  
    text,parasenttok = get_segmented_text(text0)

    # segment the whole paragraph/sentence
    paratk = sentence.word_tokenize(parasenttok)
 
    # flatten both lists
    fpara  = flatten(paratk)
    ftext  = flatten(text)

    # do a cumulative count of the words in each paragraph    
    parcount = []
    shift=0
    for para in sentence.word_tokenize(parasenttok):
        cnt = shift + sentence.count_words([para])
        shift = cnt
        parcount.append(cnt)

    # compute the frequency distribution of the text
    fdist = FreqDist(word for word in ftext)

    # export the JSON data structure
    essay['text'] = fpara       # full text (as flattened paras
    essay['count'] = parcount   # word count per paragraph 

    essay['keyword'] = fdist.keys()[:50]    # keywords ordered by frequency
    essay['ranking'] = fdist.values()[:50]  # frequency
    
    # create the dispersion data
    points = [[x,y+1] for x in range(len(fpara))
                    for y in range(len(essay['keyword']))
                    if fpara[x].lower()  == essay['keyword'][y].lower() ]
    if points:
        x, y = zip(*points)
    else:
        x = y = ()

    essay['points'] = points
    #print  essay
    #return jsonify([])
    # return the data structure
    # In JSON mode, return the JSON structure
    # In HTML mode, render the template
    
    return jsonify(essay)
    #return render_template('dispersion.html', essay=essay)
    
def get_essay(essayID):
    pass

def process_keyword():
    text0 = request.form['text']        # NVL : the text of the essay is extracted from the FORM part of the REQUEST, as received by the API

    proctime = time() # Set current time to a variable for later calculations
    _apiLogger.info(">> START : %s" % (time() - proctime,))
    proctime = time() 
   
    
    # Get the body of the essay. 
    # Currently this is everything occurring before the references section but it needs improvement/refinment.
    text1 = keyword.get_essay_body(text0)     
    _apiLogger.info(">> get_essay_body : %s" % (time() - proctime,))
    proctime = time() 

        # Split the essay body on whitespace so that you can correct some the encoding. Although this isn't needed for sentence splitting, it is needed for the correction of some characters. I have just copied the same function from the sentence splitting program.
        # Latin9 encoding puts questions marks everywhere, which confuses the sentence splitter. I reverse this split before sentence tokenisation. 
    text2 = keyword.re.split(r' ', text1)
    _apiLogger.info(">> split : %s" % (time() - proctime,))
    proctime = time() 

        # Convert latin9-encoded text back into something very similar to the original text.        
        # Latin9 encoding substitutes a question mark for MS Word curly speech marks and curly apostrophes and en-dashes and em-dashes. Function 'tidy_up_latin9' replaces em- and en-dashes with hyphens and puts back apostrophes and speech marks.
    temp1 = keyword.tidy_up_text(text2)    
    _apiLogger.info(">> tidy_up_text : %s" % (time() - proctime,))
    proctime = time() 
    
    #f = 11/0

        # Following latin9 tidy-up, un-split the body of the essay ready for sentence splitting.
    temp2 = ' '.join(temp1) 


        # Word-tokenise the body of the essay (splits off punctuation marks as well).
    text2 = WordPunctTokenizer().tokenize(temp2)
    _apiLogger.info(">> WordPunctTokenizer : %s" % (time() - proctime,))
    proctime = time() 
        
        # Part-of-speech tag the word-tokenised essay.
    #text3 = pos_tag(text2)
    #_apiLogger.info(">> pos_tag : %s" % (time() - proctime,))
    #proctime = time() 

    _POS_TAGGER = 'taggers/maxent_treebank_pos_tagger/english.pickle'
    _eaTagger = load(_POS_TAGGER)
    text3 = _eaTagger.tag(text2)
    _apiLogger.info(">> _eaTagger.tag : %s" % (time() - proctime,))
    proctime = time() 

       
        # Remove tokens that are punctuation marks or series of punc marks.        
    text4 = [w for w in text3 if not keyword.re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', w[0])]
    _apiLogger.info(">> text4 : %s" % (time() - proctime,))
    proctime = time() 

        # Put essay into lower case.
    text5 = [(w[0].lower(),w[1]) for w in text4]
    _apiLogger.info(">> text5 : %s" % (time() - proctime,))
    proctime = time() 

        # Get the English stopwords from NLTK corpus.
    eng_stopwords = stopwords.words('english')
    _apiLogger.info(">> stopwords : %s" % (time() - proctime,))
    proctime = time() 

        # Remove the stopwords.
    text6 = [(w[0],w[1]) for w in text5 if w[0] not in eng_stopwords] 
    _apiLogger.info(">> text6 : %s" % (time() - proctime,))
    proctime = time() 

    # Grab only the tokens that you want.
    text = keyword.filter_unwanted_words(text6)
    _apiLogger.info(">> filter_unwanted_words : %s" % (time() - proctime,))
    proctime = time() 

        # Replace each word with its stem. Note: Whether and when to stem needs thought.
        #text = get_word_stems(text7)

    # Get the wordset for the essay.
    unique_word_set = keyword.unique_everseen([x[0] for x in text])
    _apiLogger.info(">> unique_everseen : %s" % (time() - proctime,))
    proctime = time() 

    # Initiate an empty directed graph 'gr' of 'digraph' class  
    # Digraphs are directed graphs built of nodes and directed edges.
    gr=nx.DiGraph() # Leave this in for the betweenness centrality version.
    _apiLogger.info(">> DiGraph : %s" % (time() - proctime,))
    proctime = time() 
       
    # Add nodes to the directed graph 'gr', one node for each unique word.
    # If you are filtering out certain parts of speech, you will add a node only for those remaining unique words.
    gr.add_nodes_from(list(unique_word_set)) # Leave this in for the betweenness centrality version.
    _apiLogger.info(">> add_nodes_from : %s" % (time() - proctime,))
    proctime = time() 
        
    # Add directed edges to the graph to which you have alreaded added nodes. 
    # A directed (and unweighted) edge is added from each node/word to the word/node that follows it in the prepared text.
    keyword.add_all_node_edges(gr, text)
    _apiLogger.info(">> add_all_node_edges : %s" % (time() - proctime,))
    proctime = time() 

        # Calculate the betweenness centrality score for each node in the graph.
    betweenness_scores = betweenness_centrality(gr)        
    _apiLogger.info(">> betweenness_centrality : %s" % (time() - proctime,))
    proctime = time() 
        
        # Sort the scores into order.
    di = keyword.sort_betweenness_scores(betweenness_scores) # Leave this in for the betweenness centrality version.
    _apiLogger.info(">> sort_betweenness_scores : %s" % (time() - proctime,))
    proctime = time() 

        # Get the ranked words but without the scores.    
    words = [item[1] for item in di]
    _apiLogger.info(">> words : %s" % (time() - proctime,))
    proctime = time() 

        # How many words are in the wordset? And then divide that by some integer. TextRank paper says a third of wordset are keywords.
    x = len(words)

        # Set var 'keywords' to the top x of the ranked words.
    keywords = words[:x]

        # Make key phrases by looking for series of key words in original text (that is, after word-tokenisation but before punc and stops are removed).
    trigram_keyphrases = keyword.keywords2trigrams(keywords,text2)
    bigram_keyphrases = keyword.keywords2bigrams(keywords,text2)
    _apiLogger.info(">> keywords2bigrams : %s" % (time() - proctime,))
    proctime = time() 

        # The next few lines are using the NLTK tools. This is done to make a comparisons.

        # Remove the POS tags from the fully processed text.
    t4 = [w[0] for w in text] # Remove the tags so that the collocation finder is working on plain tokenised text that has the same content as the keywords text.
    _apiLogger.info(">> t4 : %s" % (time() - proctime,))
    proctime = time() 

        # Run some NLTK analyses to compare with your results.
    bcf = BigramCollocationFinder.from_words(t4)
    bicolls = bcf.nbest(BigramAssocMeasures.likelihood_ratio, 200)
    _apiLogger.info(">> BigramCollocationFinder : %s" % (time() - proctime,))
    proctime = time() 

    tcf = TrigramCollocationFinder.from_words(t4)
    tricolls = tcf.nbest(TrigramAssocMeasures.likelihood_ratio, 200)
    _apiLogger.info(">> TrigramCollocationFinder : %s" % (time() - proctime,))
    proctime = time() 

    fdist = FreqDist(t4)    
    freqdist = fdist.keys()
    _apiLogger.info(">> freqdist : %s" % (time() - proctime,))
    proctime = time() 

    
    essay = {}

    essay['keywords'] = keywords[:25]
    essay['keywords_d'] = freqdist[:25]
    essay['bigram_keyphrases'] = bigram_keyphrases
    essay['trigram_keyphrases'] = trigram_keyphrases
    essay['tricolls'] = tricolls[:10]
    essay['di'] = di

    _apiLogger.info(">> essay : %s" % (time() - proctime,))
    proctime = time() 
    
    return jsonify(essay)

def process_essay_v2():
    text0 = request.form['text']        # NVL : the text of the essay is extracted from the FORM part of the REQUEST, as received by the API

    #nf = open("c:\windows\Temp\oeTemp\RECEIVE.txt", 'w')
    #print nf
    #sutf8 = text0.encode('UTF-8')
    #nf.write(sutf8)
    #nf.close()
    

    struc_feedback = {}
    text,parasenttok,number_of_words,section_names,section_labels = sentence2.pre_process_essay(text0,struc_feedback,None,None,'NVL')
    gr, myarray, ranked_global_weights, reorganised_array, graphtime = sentence2.process_essay(text, parasenttok, None,None,'NVL')
    essay, essay_id = sentence2.nicolas_results(gr,ranked_global_weights,parasenttok, number_of_words,struc_feedback)


    mylist3 = []
    for (a,b,c,d,e) in reorganised_array: # Get only the sentence key numbers from the sorted scores list...
        #mylist3.insert(b,c)
        mylist3.append((b,c))  
        
    mylist3.sort(key=itemgetter(0))      
    essay['struct'] = mylist3    

    
    return jsonify(essay)

def process_keyword_v2():
    text0 = request.form['text']        # NVL : the text of the essay is extracted from the FORM part of the REQUEST, as received by the API

    essay = keyword2.nicolas_results_ke(text0)
    return jsonify(essay)

'''

'''
def analyse_essay_v3(text0):   
    pass
