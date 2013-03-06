import re # For regular expressions
from time import time # For calculating processing times
from uuid import uuid4
#from decimal import *
from EssayAnalyser.se_procedure_v3 import pre_process_text_se, pre_process_struc,\
    process_essay_se
from EssayAnalyser.ke_all_v3 import process_essay_ke
from decimal import getcontext, Decimal
from EssayAnalyser import _apiLogger
from collections import OrderedDict
from collections import Counter
import random

"""
This file contains the functions for writing desired sentence extraction results to file.
The functions for the key word/phrase results are in file ke_all.py.
The principal functions debora_results_se and nicolas_results_se are called in file se_main.py.
Function names:
# Function: write_to_details_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2):
# Function: write_to_summary_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2)    
# Function: print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2)
# Function: cf_keysents_sections(sorted_list)
# Function: debora_results_se(gr,text,ranked_global_weights,reorganised_array,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,filename,nf,nf2,dev)
# Function: nicolas_results_se(gr,text,ranked_global_weights,parasenttok, number_of_words, struc_feedback)
"""

# Function: write_to_details_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2):
# Called by debora_results_se in this file.
def write_to_details_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2):
    ########
    # WRITE SUMMARY INFO AT THE TOP
    ########    
    nf.write('\n') # Add blank lines to the essay results file            
    nf.write(str(filename)) # Write the new file name to the essay results file
    nf.write('\n') # Add blank lines to the essay results file
##    
##    nf.write('\nTotal number of paragraphs (includes everything that occurs before refs): ') #...and print the results to the summary results file.
##    nf.write(str(len(text)))
##
##    nf.write('\nTotal number of words (includes everything that occurs before refs): ') #...and print the results to the summary results file.
##    nf.write(str(number_of_words))
##
##    nf.write('\nTotal number of nodes') # The number of nodes is not equal to the number of true sentences. Some of the nodes that are added from myarray are not true sentences.
##    nf.write(str(len(gr.nodes())))
##    
##    number_of_edges = len(gr.edges()) # But edges are only added to link two true sentences that have a similarity score > 0.
##    nf.write('\nTotal number of edges in the graph: ')         
##    nf.write(str(number_of_edges))
##
##    nf.write('\nNumber of top 30 true sents in intro: ') 
##    nf.write(str(introcount)) # introcount is the number of top-ranking sentences that are in the introduction
##            
##    nf.write('\nNumber of top 30 true sents in concl: ') 
##    nf.write(str(conclcount)) # conclcount is the number of top-ranking sentences that are in the conclusion 

    mylist2 = []
    for item in ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        key = item[1]
        mylist2.append(key)
    nf.write('\nRanked importance ("key-ness") order of true sentences: \n') 
    nf.write(str(mylist2)) # ...and write them to the results file so you can see the order at a glance.
    nf.write('\n')
    
    ########
    # WRITE SECTION SENTENCES
    ########
    temp = zip(section_names, section_labels)
    for pair in temp: # For each member of the list of (section_name, section_label) pairs
        nf.write('\nSentences from section: ')
        nf.write(str(pair[0]))
        nf.write('\n')
        for item in reorganised_array: # For each member of the list/array (each sentence)
            if item[2] == pair[1]: # if the label of the sentence is the same as the label in the pair
                nf.write(str(item)) # and write it to file
                nf.write('\n')
    ########
    # WRITE DETAILED SCORES AND SENTS AT THE END
    ########    
    # Write detailed results to the essay results file.
    r = ranked_global_weights[:30]
    s = str(r)
#    s = str(ranked_global_weights) # Map the results into a string so you can write the string to the output file
    w = re.sub('\]\),', ']),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    y = re.sub('\"\),', '\'),\n', w) # Be careful, because Python sometimes uses double quotes instead of single ones          
    nf.write('\n\nTop 30 key sentences: \n')
    nf.write(y)
    nf.write('\n')

# Function: write_to_summary_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2)    
# Called by debora_results_se in this file.
def write_to_summary_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2):
    #nf2.write(str(filename)) # Write current essay file name to the summary results file
    #nf2.write('; ') # Add a blank line to the summary results file

    countTrueSent = 0
    countSentLen = 0
    for item in reorganised_array: # For each member of the list/array (each sentence)
        tidysent = item[4]
        countSentLen += len(tidysent)
        label = item[2]
        if label == '#+s#' or label == '#+s:i#' or label == '#+s:c#' or label == '#+s:s#' or label == '#+s:p#':
            countTrueSent += 1
        else:
            countTrueSent = countTrueSent

    countIntroSent = 0
    countConclSent = 0
    for item in reorganised_array:
        label = item[2]
        if label == '#+s:i#':
            countIntroSent += 1
        if label == '#+s:c#':
            countConclSent += 1
    countAvSentLen = float(countSentLen) / float(countTrueSent)
    countAvSentLen = round(countAvSentLen, 2)


    nf2.write('all words; ') 
    nf2.write(str(number_of_words))
    nf2.write('; ')
    nf2.write('tidy words; ') 
    nf2.write(str(countSentLen))
    nf2.write('; ')
    nf2.write('true sents; ')         
    nf2.write(str(countTrueSent))
    nf2.write('; ')
    nf2.write('avlen tidysent; ')
    nf2.write(str(countAvSentLen))
    nf2.write('; ')
    nf2.write('paras; ') # Total number of paragraphs
    nf2.write(str(len(text)))
    nf2.write('; ')
    nf2.write('heads; ')  # Total number of headings
    nf2.write(str(len(headings)))
    nf2.write('; ')
    nf2.write('non-heading paras; ')
    len_body = len(text) - len(headings)  
    nf2.write(str(len_body))
    nf2.write('; ')
    nf2.write('intro head; ')
    nf2.write(str(introheaded))
    nf2.write('; ')
    getcontext().prec = 3
    nf2.write('% body == i; ')
    if countIntroSent > 0: 
        y = 100 * Decimal(1.0/(countTrueSent / countIntroSent)) # y is the percentage of the essay body taken up by the introduction
    else: # xxxx This condition should not succeed for any essay, but some test files don't return a result for intro section, in which case countIntroSent == 0, which returns an error on the previous line. Needs a better fix. 
        y = []
    nf2.write(str(y))
    nf2.write('; ')
    nf2.write('i sents; ')
    nf2.write(str(countIntroSent))
    nf2.write('; ')
    nf2.write('concl head; ')
    nf2.write(str(conclheaded))
    nf2.write('; ')
    nf2.write('% body == c; ')
    if countConclSent > 0:
        y = 100 * Decimal(1.0/(countTrueSent / countConclSent)) # y is the percentage of the essay body taken up by the introduction
    else:
        y = []
    nf2.write(str(y))
    nf2.write('; ')    
    nf2.write('c sents; ')
    nf2.write(str(countConclSent))
    nf2.write('; ')            
    nf2.write('nodes; ')         
    nf2.write(str(len(gr.nodes())))
    nf2.write('; ')
    nf2.write('edges; ')
    number_of_edges = len(gr.edges())                          
    nf2.write(str(number_of_edges))
    nf2.write('; ')
    nf2.write('edges/sents; ')
    x = float(number_of_edges) / float(countTrueSent)
    ratio = round(x, 2)
    nf2.write(str(ratio))
    nf2.write('; ')              
    nf2.write('i & toprank; ') 
    nf2.write(str(introcount)) # introcount is the number of top-ranking sentences that are in the introduction
    nf2.write('; ') 
    nf2.write('c & toprank; ') 
    nf2.write(str(conclcount)) # introcount is the number of top-ranking sentences that are in the introduction
    nf2.write('; ')
    r = ranked_global_weights[0][0]
    nf2.write('se top centr score;')
    s = round(r,5)
    nf2.write(str(s))
    nf2.write('; ')
    

    mylist2 = []
    for item in ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        key = item[1]
        mylist2.append(key)
#    nf2.write('\n\nRanked importance ("key-ness") order of true sentences: \n') 
#    nf2.write(str(mylist2)) # ...and write them to the results file so you can see the order at a glance.
#    nf2.write('\n')
     
    ########
    # WRITE DETAILED SCORES AND SENTS AT THE END
    ########    
    # Write detailed results to the essay results file.
    q = countTrueSent / 4  # Writing only the top 25 % of key sentences to the file
    r = ranked_global_weights[:q]
    s = str(r)
#    s = str(ranked_global_weights) # Map the results into a string so you can write the string to the output file
    w = re.sub('\]\),', ']),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    y = re.sub('\"\),', '\'),\n', w) # Be careful, because Python sometimes uses double quotes instead of single ones          
#    nf2.write('\nTop ')
#    nf2.write(str(q))
#    nf2.write(' key sentences: \n')
#    nf2.write(y)
#    nf2.write('\n\n')
    
    
##    mylist2 = []
##    for item in ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
##        key = item[1]
##        mylist2.append(key)
##    nf2.write('\n\nRanked sentence order: (currently includes title (if the essay gives one) but not empty sentences (following processing) or headings, captions, ...)\n') 
##    nf2.write(str(mylist2)) # ...and write them to the results file so you can see the order at a glance.
                          


    

##    nf2.write('\n\nHighest-scoring sentence:')
##    nf2.write('\n')
##    nf2.write(str(ranked_global_weights[0]))
##    
##    nf2.write('\nOne of the lowest-scoring sentence (usually more than one):')
##    nf2.write('\n')
##    temp4 = len(ranked_global_weights)
##    temp5 = temp4-1
##    nf2.write(str(ranked_global_weights[temp5]))
##    nf2.write('\n')

# Function: print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2)
# Takes different recorded times, does some arithmetic, and prints/writes process times.
# For monitoring and improving program efficiency.
# Commented out at the moment because I don't want to focus on timings for now.
def print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2):
    textproctime = texttime - startfiletime # Work out how long different parts of the program took to run...
##    graphproctime = graphtime - texttime
##    scoresproctime = scorestime - graphtime
##    totalproctime = scorestime - startfiletime
##    importproctime = endimporttime - startprogtime # Get some more processing timings   
##    nf2.write('\nText processing time: ')
##    nf2.write(str(textproctime))
##    nf2.write('\nGraph processing time: ')
##    nf2.write(str(graphproctime))
##    nf2.write('\nScores processing time: ')
##    nf2.write(str(scoresproctime))
##    nf2.write('\nTotal essay processing time: ')
##    nf2.write(str(totalproctime))
##    nf2.write('\n\n*********************************************************\n\n')
##    #nf2.write('\n\n')
##    nf2.write('\nCompilation and import processing time: ')
##    nf2.write(str(importproctime))
##    stopprogtime = time()
##    nf2.write('\nProgram stopped running at: ')
##    nf2.write(str(stopprogtime))
##    totalprogtime = stopprogtime - startprogtime
##    nf2.write('\nTotal program processing time: ')
##    nf2.write(str(totalprogtime))

# Function: cf_keysents_sections(sorted_list)
# Makes some comparisons between the sentences that constitute the introduction, and the sentences sorted according to global weight.
# Does something similar for 'conclusion' sentences. 
# Returns the number of top-scoring sentences contained in 'this_section'.    
# Called by debora_results_se in this file.
def cf_keysents_sections(sorted_list):
    top_sents = sorted_list[0:30]
    intro = [item for item in sorted_list if item[2] == '#+s:i#']
    concl = [item for item in sorted_list if item[2] == '#+s:c#']
    # How many of the top 30 sentences are in the Introduction?
    # ditto Conclusion?
    counter1 = 0
    for item in top_sents:
        if item in intro:
            counter1 += 1
    counter2 = 0
    for item in top_sents:
        if item in concl:
            counter2 += 1
    return counter1, counter2

# Function: debora_results_se(gr,text,ranked_global_weights,reorganised_array,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,filename,nf,nf2,dev)
# Prints and writes to file various results I want to see.
# Called in se_main.py.
def debora_results_se(gr,text,ranked_global_weights,reorganised_array,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,filename,nf,nf2,dev):
    introcount,conclcount = cf_keysents_sections(ranked_global_weights)
    write_to_details_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2)
    write_to_summary_file(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2)

def write_to_summary_file_ALT(filename,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount,nf,nf2):
    """
    Write the sentence analytics into a file
    Replace DGF initial method (write_to_summary_file) by separating data processing and outputing
    TODO: check the format of the output
    """
    data = getAnalytics(text, number_of_words, section_names, section_labels, headings, conclheaded, c_first, c_last, introheaded, i_first, i_last, gr, ranked_global_weights, reorganised_array, introcount, conclcount)
    for key,attr in data.items():
        nf2.write(key + "; ") 
        nf2.write(str(attr))
        nf2.write('; ')
    pass

def getAnalytics(text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr,ranked_global_weights,reorganised_array,introcount,conclcount):
    """
    Get a summary of text & sentence analytics
    @return: A dictionary (ordrered) containing a set of metrics
    TODO: check the default values on some of the keys (intro head is [])
    """
    countTrueSent = 0
    countSentLen = 0
    for item in reorganised_array: # For each member of the list/array (each sentence)
        tidysent = item[4]
        countSentLen += len(tidysent)
        label = item[2]
        if label == '#+s#' or label == '#+s:i#' or label == '#+s:c#' or label == '#+s:s#' or label == '#+s:p#':
            countTrueSent += 1
        else:
            countTrueSent = countTrueSent

    countIntroSent = 0
    countConclSent = 0
    for item in reorganised_array:
        label = item[2]
        if label == '#+s:i#':
            countIntroSent += 1
        if label == '#+s:c#':
            countConclSent += 1
    countAvSentLen = float(countSentLen) / float(countTrueSent)
    countAvSentLen = round(countAvSentLen, 2)

    # Use an OrderedDict to maintain order of inserted item (better for checking)
    summary = OrderedDict()
    summary['all words'] = number_of_words
    summary['tidy words'] = countSentLen
    
    summary['true sents'] = countTrueSent
    summary['avlen tidysent'] = countAvSentLen
    summary['paras'] = len(text)
    summary['heads'] = len(headings)
    summary['non-heading paras'] = len(text) - len(headings)  
    summary['intro head'] = introheaded

    getcontext().prec = 3
    if countIntroSent > 0: 
        y = 100 * Decimal(1.0/(countTrueSent / countIntroSent)) # y is the percentage of the essay body taken up by the introduction
    else: # xxxx This condition should not succeed for any essay, but some test files don't return a result for intro section, in which case countIntroSent == 0, which returns an error on the previous line. Needs a better fix. 
        y = 0
    summary['% body == i'] = round(y,2)
    summary['i sents'] = countIntroSent
    summary['concl head'] = conclheaded

    if countConclSent > 0:
        y = 100 * Decimal(1.0/(countTrueSent / countConclSent)) # y is the percentage of the essay body taken up by the introduction
    else:
        y = 0
    summary['% body == c'] = round(y,2)
    summary['c sents'] = countConclSent
    summary['nodes'] = len(gr.nodes())
        
    number_of_edges = len(gr.edges())
    summary['edges'] = number_of_edges                        
    x = float(number_of_edges) / float(countTrueSent)
    ratio = round(x, 2)
    summary['edges/sents'] = ratio
    summary['i & toprank'] = (introcount) # introcount is the number of top-ranking sentences that are in the introduction
    summary['c & toprank'] = (conclcount) # introcount is the number of top-ranking sentences that are in the introduction

    r = ranked_global_weights[0][0]
    summary['se top centr score'] = round(r,5)
    
    return summary


def nicolas_results_se(gr,ranked_global_weights,parasenttok, number_of_words, struc_feedback):
    """
    Return the result of the text & sentence analytics
    @return: A dictionary containing various elements of the text analytics
    """
    
    essay = {}

    ### Add paragraph/sentence structure
    essay['parasenttok'] = parasenttok
    
    ### Add statistics on essay
    stats = {}
    stats['paragraphs'] = str(len(parasenttok))
    stats['sentences'] =  sum(w for w in [len(x) for x in parasenttok])       
    stats['words'] = number_of_words 
    stats['nodes'] = str(len(gr.nodes()))
    stats['edges'] = str(len(gr.edges()))

    essay['stats'] = stats

    ### Add section feedback
    struc_feedback['comment intro concl'] = cf_keysents_sections(ranked_global_weights)
    essay['struc_feedback'] = struc_feedback    
    

    ## Add ranked 
    mylist2 = []
    top_ranked_global_weights = ranked_global_weights[:15]    
    for (a,b,c,d,e) in top_ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        mylist2.append((a,b,c))        
    essay['ranked'] = mylist2
    
    return essay


def Flask_process_text(text0):
    processtime = time()
    _apiLogger.info(">> ##\t essay received : \t %s" % (time() - processtime))    

    
    ##############################
    ##############################
    ## 3. Do required NLP pre-processing on this essay
    ##############################
    ##############################
    text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,None,None,"NVL")
    # Next line is needed instead of above line if we are using sbd sentence splitter.
    #text,parasenttok,wordtok_text,number_of_words,struc_feedback = pre_process_text_se(text0,nf,nf2,model,dev)
    _apiLogger.info(">> ##\t pre_process_text_se : \t %s" % (time() - processtime))    
    ##############################
    ##############################
    ## 4. Do required essay structure pre-processing on this essay
    ##############################
    ##############################
    text_se,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last = pre_process_struc(text,None,None,"NVL")
    _apiLogger.info(">> ##\t pre_process_struc : \t %s" % (time() - processtime))    
    
    ##############################
    ##############################
    ## 5. Construct the key sentence graph and do the graph analyses
    ##############################
    ##############################      
    gr_se,myarray_se,ranked_global_weights,reorganised_array,graphtime=process_essay_se(text_se,parasenttok,None,None,"NVL")
    _apiLogger.info(">> ##\t process_essay_se : \t %s" % (time() - processtime))    
    
    '''###########################
    ##############################
    ## 6. Construct the key word graph and do the graph analyses
    ##############################
    ##############################      
    @param text_ke: ?????
    @param gr_ke: networkx graph for the keywords
    @param di: array of ["keyword", rank], sorted by rank
    @param myarray_ke: associative array "lemma" : [list of words]
    @param keylemmas: array of lemmas
    @param keywords: array of keywords
    @param bigram_keyphrases: array of [ [ "keyword", "keyword" ] , count ]
    @param trigram_keyphrases: array of [ [ "keyword", "keyword", "keyword" ] , count ]
    @param quadgram_keyphrases: array of [ [ "keyword", "keyword", "keyword", "keyword" ] , count ]
    '''
    text_ke,gr_ke,di,myarray_ke,keylemmas,keywords,bigram_keyphrases,trigram_keyphrases,quadgram_keyphrases=process_essay_ke(text_se,wordtok_text,None,None,"NVL")
    _apiLogger.info(">> ##\t process_essay_ke : \t %s" % (time() - processtime))    
    
    ##############################
    ##############################
    ## 7. Write to file whichever results you choose
    ##############################
    ##############################      
    essay = nicolas_results_se(gr_se,ranked_global_weights,parasenttok, number_of_words,struc_feedback)
    _apiLogger.info(">> ##\t nicolas_results_se : \t %s" % (time() - processtime))    
    
    ##############################
    ##############################
    ## 8. Get the text & sentence analytics
    ##############################
    ##############################      
    introcount,conclcount = cf_keysents_sections(ranked_global_weights)
    analytics = getAnalytics(text_se, number_of_words, section_names, section_labels, 
                                    headings, conclheaded, c_first, c_last, introheaded, 
                                    i_first, i_last, gr_se, ranked_global_weights, 
                                    reorganised_array, introcount, conclcount)
    _apiLogger.info(">> ##\t format getAnalytics : \t %s" % (time() - processtime))   
    #for key,attr in analytics.items():
    #    print "  " + key + " => " + str(attr)
    
    # Build an associative array out of the keywords list    
    mapkeyscore = {}
    for (word,score) in di:
        mapkeyscore[word] = score

    # Get the rank score of a keyword, 0 if not found
    def getScore(keyword):
        if keyword in mapkeyscore:
            return mapkeyscore[keyword]
        else:
            return 0
    
    # Get the lemma form of a keyword
    def getLemma(keyword):
        for (k,v) in myarray_ke.items():
            if keyword in v:
                return k
        return keyword + " ###"
    
    # Build A JSON object out of the Ngram(s), with their score(s), count and form(s) 
    def ngramToJSON(ngram_list):
        jsonNGram = []
        for [win_words,count] in ngram_list:
            ngram=[getLemma(w) for w in win_words]
            #key = ''.join(r1)
            score = [getScore(n) for n in ngram]
            jsonNGram.append({
                'ngram':ngram,
                'source':win_words,
                'count':count,
                'score':score})
        return jsonNGram
    
    # Build a hierarchical structure of keywpords 
    def keywordstoTree():
        treenode = []
        for kk in keylemmas:
            v = myarray_ke[kk]
            tally=Counter()
            for elem in v:
                tally[elem] += 1
            
            subtree = []    
            for (elem,count) in tally.items():
                keywords = [ {'name': w , 'mysize': getScore(w), 'mycount': 1, "colour":"#f9f0ab" } for w in v if w==elem ]
                subtree.append({ 'name' : elem, 'children' : keywords})
                #tt = [{ 'name' : elem, 'children' : keywords}]
                #keywords = [ {'name': w , 'size': getScore(w), "colour":"#f9f0ab" } for w in v ]
                ##treenode.append({ 'name' : k, 'size': 1, "colour":"#f9f0ab" })
            treenode.append({ 'name' : kk, 'children' : subtree})
        
        return treenode
    
    def ngramToTree(ngram_list):
        treenode = []
        for [win_words,count] in ngram_list:
            subtree = []
            for kk in win_words:
                keywords = [ {'name': kk , 'mysize': getScore(kk), 'mycount': count, "colour":"#f9f0ab" }]
                subtree.append({ 'name' : kk, 'children' : keywords})
                #gg = getLemma(kk)
                #v = myarray_ke[gg]
                #tally=Counter()
                #for elem in v:
                #    tally[elem] += 1
            
                    #subtree = []    
                #for (elem,count) in tally.items():
                #    keywords = [ {'name': w , 'mysize': getScore(w), 'mycount': 1, "colour":"#f9f0ab" } for w in v if w==elem ]
                #    subtree.append({ 'name' : elem, 'children' : keywords})
                    #tt = [{ 'name' : elem, 'children' : keywords}]
                    #keywords = [ {'name': w , 'size': getScore(w), "colour":"#f9f0ab" } for w in v ]
                    ##treenode.append({ 'name' : k, 'size': 1, "colour":"#f9f0ab" })
            treenode.append({ 'name' : ' '.join(win_words), 'children' : subtree})
       
        return treenode

    children = keywordstoTree()
    children1 = ngramToTree(bigram_keyphrases)
    ttttt = children + children1
    random.shuffle(ttttt)
    essay = OrderedDict()
    
    tt = [ttttt[i:i+6] for i in range(0, len(ttttt), 6)]
    
    gg = [{'name' : '##CAT_'+str(idx+1)+'##', 'children': elt} for idx,elt in enumerate(tt)]
    
    essay['stats'] = { 
            'n-keylemma' : len(keylemmas),
            'n-myarray_ke' : len(myarray_ke),
            'n-keywords' : len(keywords)
        }
    essay['tree'] = { 'name' : 'concept map', 'children' : gg}
    
    essay['keylemmas'] = keylemmas
    essay['keywords'] = keywords
    essay['bigram_keyphrases'] = ngramToJSON(bigram_keyphrases)
    essay['trigram_keyphrases'] = ngramToJSON(trigram_keyphrases)
    essay['quadgram_keyphrases'] = ngramToJSON(quadgram_keyphrases)
    #essay['myarray_ke'] = myarray_ke
    #essay['keylemmas'] = keylemmas
    essay['analytics'] = analytics
    
    
    
    _apiLogger.info(">> ##\t return processed JSON : \t %s" % (time() - processtime))    
    return  essay['tree']
    
    
    
        
# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>
