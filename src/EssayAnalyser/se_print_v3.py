import re # For regular expressions
from time import time # For calculating processing times
from uuid import uuid4
from decimal import *
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

# Function: nicolas_results_se(gr,ranked_global_weights,parasenttok, number_of_words, struc_feedback)
# Prints and writes to file various results Nicolas wants.    
# Called in se_main.py.
def nicolas_results_se(gr,ranked_global_weights,parasenttok, number_of_words, struc_feedback):
    # NVL : get the different pieces into the JSON data structure
    essay = {}
    essay['essayID'] = str(uuid4())     # NVL : generate a random UUID for the essay (converted to string)
    essay['parasenttok'] = parasenttok
    stats = {}
    stats['paragraphs'] = str(len(parasenttok))
    print 'stats["paragraphs"] = str(len(parasenttok))\n\n', len(parasenttok)

    stats['sentences'] =  sum(w for w in [len(x) for x in parasenttok])       
    print 'sum(w for w in [len(x) for x in parasenttok])\n\n', stats['sentences']               

    stats['words'] = number_of_words 
    print '\n\nTotal number of words: ', number_of_words

    stats['nodes'] = str(len(gr.nodes()))

    print '\n\nTotal number of edges in the graph: ',  len(gr.edges())        
    stats['edges'] = str(len(gr.edges()))

    essay['stats'] = stats

    struc_feedback['comment intro concl'] = cf_keysents_sections(ranked_global_weights)
    essay['struc_feedback'] = struc_feedback    
    

    mylist2 = []
    top_ranked_global_weights = ranked_global_weights[:10]    
    for (a,b,c,d,e) in top_ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        mylist2.append((a,b,c))        
    essay['ranked'] = mylist2

    print '\n\n', stats, '\n\n', struc_feedback, '\n\n', mylist2, '\n\n'
    
    return essay, essay['essayID']

    # NVL : return the JSON object
    #return render_template('essay.html', essay=essay)    
    







        
# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>
