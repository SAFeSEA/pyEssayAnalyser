"""
This program uses graph-based methods to identify the key phrases in an essay. The program processes every file in its current working directory that ends in 'txt', and puts a results file for each file processed in a newly created temporary directory. The program also generates a single summary results file that contains results information on all the files that have been processed. First it does some pre-processing: latin9 tidy-up, word tokenisation, part-of-speech tagging, removal of punctuation, put into lower case, stop words removed. Then it builds a graph using words as nodes. In this program (unlike the sentence extraction program) the actual words are the nodes, there is no an array storing the sentences with a key. Directed edges are drawn between pairs of words/nodes (from earlier to later ones). Each pair of words/nodes is a bigram in the processed version of the text. Once the graph is built, an algorithm is applied to it to find the 'important' words. In this version, I use 'betweenness centrality'. In a different version I use PageRank. 'Important words' are those that are important with respect to the entire text. A word is important (is a key word) if it co-occurs with lots of words that co-occur with lots of words that co-occur... The scores algorithm attributes an 'importance' score to every word in the text. These are then sorted in order of descending score, and the top N words are considered to be the key words. An additional procedure takes the key words and looks for sequences of them in the original text, and these are considered to be key phrases. For the sake of comparison, the results files also include a straight frequency count and collocation measures using NLTK tools.

This program can be configured in a variety of ways. For example, this version is configured not to dismiss any parts of speech, but to use all of those that remain following removal of the stop words. Hence, for this version, it is not necessary to POS-tag the text. However, I am leaving the POS-tag procedure commented in. This version takes out all the stopwords and all the punctuation before the graph is built.
"""
import os # This is for file handling
import tempfile
import shutil
from operator import itemgetter
import networkx as nx

from nltk.tag import pos_tag
from nltk.tokenize import WordPunctTokenizer 
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import TrigramAssocMeasures
from nltk.probability import FreqDist

from keywords_functions_betweenness_v8 import *
from betweenness import *
from networkx.algorithms.centrality.betweenness import betweenness_centrality


# Begin by deleting the temporary directory and files you created last time you ran this program.
tempdir0 = tempfile.gettempdir() # This gets the path to the location of the temporary files and dirs.
tempfilelist = os.listdir(tempdir0) # This gets a list of the items stored in that location
for dirname in tempfilelist:
	fullpath = os.path.join(tempdir0, dirname) # Join the path name to the dir name so you can delete the directories
	if dirname.startswith('AAA_Key-Word-Phrase_Results_'): # Only delete the temp dirs that you have created in an earlier run of this program.
		shutil.rmtree(fullpath) # Do the deletion
tempdir1 = tempfile.mkdtemp(suffix='', prefix='AAA_Key-Word-Phrase_Results_', dir=None) # Create a new directory for the essay results files to go in. Make it a temporary directory. Temporary files are stored here: c:\\users\\debora\\appdata\\local\\temp		

cwdir = os.getcwd()  # Get current working directory
filelist = os.listdir(cwdir) # Set var 'filelist' to a list of files in cwdir. 'listdir' reads the dir you've given it, and returns a list of files.
newfilename2 = os.path.join(tempdir1, 'key-word-phrase_results_summary.txt') 
nf2 = open(newfilename2, 'w') # Open 'newfilename2' (for writing to) and set open file to var 'nf2'
nf2.write('\n\n*********************************************************\n\n')
for filename in filelist: # For each file in the current directory...    
    if filename[-3:] == 'txt': # If a file name ends in 'txt'...
        print '\n\n_____________________________________________'            
        print filename # Print to shell to monitor progress
        f = open(filename, 'r') # Open current essay file for reading
        text0 = f.read() # Read in the essay and set to var 'text0'
        f.close() # Close the essay file
        string = filename[:-4] + '_results' + '.txt'
        newfilename = os.path.join(tempdir1, string)                     
        nf = open(newfilename, 'w') # Open 'newfilename' (for writing to) and set open file to var 'nf'
        nf.write('\n\n') # Add blank lines to the essay results file            
        nf.write(str(filename)) # Write the new file name to the essay results file
        nf.write('\n\n') # Add blank lines to the essay results file
        nf2.write(str(filename)) # Write current essay file name to the summary results file
        nf2.write('\n') # Add a blank line to the summary results file
        
        # Get the body of the essay. 
        # Currently this is everything occurring before the references section but it needs improvement/refinment.
        text1 = get_essay_body(text0,nf)     

        # Split the essay body on whitespace so that you can correct some the encoding. Although this isn't needed for sentence splitting, it is needed for the correction of some characters. I have just copied the same function from the sentence splitting program.
        # Latin9 encoding puts questions marks everywhere, which confuses the sentence splitter. I reverse this split before sentence tokenisation. 
        text2 = re.split(r' ', text1)

        # Convert latin9-encoded text back into something very similar to the original text.		
        # Latin9 encoding substitutes a question mark for MS Word curly speech marks and curly apostrophes and en-dashes and em-dashes. Function 'tidy_up_latin9' replaces em- and en-dashes with hyphens and puts back apostrophes and speech marks.
        temp1 = tidy_up_text(text2)    

        # Following latin9 tidy-up, un-split the body of the essay ready for sentence splitting.
        temp2 = ' '.join(temp1) 

        # NVL : IMPORTANT ! 
        # NVL : NEED TO CONVERT TEXT TO STRING (UTF-8)
        # NVL : OTHERWISE YOU HAVE UNICODE TEXT (NOT SURE WHY YET) 
        temp3 = temp2.encode('utf8')        

        # Word-tokenise the body of the essay (splits off punctuation marks as well).
        text2 = WordPunctTokenizer().tokenize(temp3)
        
        # Part-of-speech tag the word-tokenised essay.
        text3 = pos_tag(text2)
        
        # Remove tokens that are punctuation marks or series of punc marks.        
        text4 = [w for w in text3 if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', w[0])]

        # Put essay into lower case.
        text5 = [(w[0].lower(),w[1]) for w in text4]

        # Get the English stopwords from NLTK corpus.
        eng_stopwords = stopwords.words('english')

        # Remove the stopwords.
        text6 = [(w[0],w[1]) for w in text5 if w[0] not in eng_stopwords] 

	# Grab only the tokens that you want.
        text = filter_unwanted_words(text6)

        # Replace each word with its stem. Note: Whether and when to stem needs thought.
        #text = get_word_stems(text7)

	# Get the wordset for the essay.
        unique_word_set = unique_everseen([x[0] for x in text])

	# Initiate an empty directed graph 'gr' of 'digraph' class  
	# Digraphs are directed graphs built of nodes and directed edges.
        gr=nx.DiGraph() # Leave this in for the betweenness centrality version.
        
	# Add nodes to the directed graph 'gr', one node for each unique word.
	# If you are filtering out certain parts of speech, you will add a node only for those remaining unique words.
        gr.add_nodes_from(list(unique_word_set)) # Leave this in for the betweenness centrality version.
        
	# Add directed edges to the graph to which you have alreaded added nodes. 
	# A directed (and unweighted) edge is added from each node/word to the word/node that follows it in the prepared text.
        add_all_node_edges(gr, text)

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
        trigram_keyphrases = keywords2trigrams(keywords,text2)
        bigram_keyphrases = keywords2bigrams(keywords,text2)

        # The next few lines are using the NLTK tools. This is done to make a comparisons.

        # Remove the POS tags from the fully processed text.
        t4 = [w[0] for w in text] # Remove the tags so that the collocation finder is working on plain tokenised text that has the same content as the keywords text.

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
        nf.close() # Close the essay file        

nf2.close()# Close the summary results file.


