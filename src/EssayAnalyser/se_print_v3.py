import re # For regular expressions
#import sys
from time import time # For calculating processing times
from decimal import getcontext, Decimal



"""
This file contains the functions for selecting data structures to be
passed to ea_results.py, and for writing desired sentence extraction
results to file. Similar functions for the key word/phrase results
are in file ke_all.py.
Function names:
def write_to_details_file(essay_fname,paras,rankorder,number_of_words,\
def write_to_summary_file(essay_fname,paras,number_of_words,\
def get_essay_stats_se(gr_se,text,headings,ranked_global_weights,reorganised_array):
def print_processing_times(getassdatatime,processasstexttime,processtbindextime,startassdatatime,startfiletime, texttime, structime, se_scorestime, ke_scorestime, nf2):
def cf_keysents_sections(sorted_list):
def debora_write_results_se(essay_fname,paras,rankorder,number_of_words,\
"""

# Function: write_to_details_file(essay_fname,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr_se,ranked_global_weights,reorganised_array,i_toprank,c_toprank,nf,nf2):
# Called by debora_results_se in this file.
#def write_to_details_file(essay_fname,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr_se,ranked_global_weights,reorganised_array,i_toprank,c_toprank,nf,nf2):
def write_to_details_file(essay_fname,paras,rankorder,number_of_words,\
    section_names,section_labels,headings,\
    conclheaded,c_first,c_last,introheaded,i_first,i_last,\
    ranked_global_weights,reorganised_array,i_toprank,c_toprank,\
    nf,nf2):

    ########
    # WRITE SUMMARY INFO AT THE TOP
    ########    
    nf.write('\n') # Add blank lines to the essay results file            
    nf.write(str(essay_fname)) # Write the new file name to the essay results file
    nf.write('\n') # Add blank lines to the essay results file

    #nf.write('\nKey sentences in descending rank order: \n')
    nf.write('\nSentences ranked in key-ness order (descending): \n')
    # xxxx Do you want all the sentences or do you want the top N?
    s = str(rankorder) # ...and write them to the results file so you can see the order at a glance.
    #s = str(rankorder[:25]) # ...and write them to the results file so you can see the order at a glance.
    w = re.sub('u\'', 'u\'\n\n', s) # Add a new line at the end of every result so that each result is written to a separate line

    c = w.decode('unicode-escape')
    nf.write(c)
    nf.write('\n')    

##    s = str(
##    c = s.decode('unicode-escape')
##    nf.write(c)
    
    ########
    # WRITE SECTION SENTENCES
    ########
    temp = zip(section_names, section_labels)
    for pair in temp: # For each member of the list of (section_name, section_label) pairs
        nf.write('\nSentences from section: ')
        s = str(pair[0])
        c = s.decode('unicode-escape')
        nf.write(c)
        nf.write('\n')
        for item in reorganised_array: # For each member of the list/array (each sentence)
            if item[2] == pair[1]: # if the label of the sentence is the same as the label in the pair               
                s = str(item)
                c = s.decode('unicode-escape')
                nf.write(c)# and write it to file
                nf.write('\n')
    ########
    # WRITE DETAILED SCORES AND SENTS AT THE END
    ########    
    # Write detailed results to the essay results file.
    r = ranked_global_weights # [:30] xxxx Do you want all the sentences ranked, or just the top N?
    s = str(r) # Map the results into a string so you can write the string to the output file
    w = re.sub('\]\),', ']),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    y = re.sub('\"\),', '\'),\n', w) # Be careful, because Python sometimes uses double quotes instead of single ones          
    #nf.write('\n\nTop 30 key sentences: \n')
    nf.write('\n\nAll sentences ranked in key-ness order (descending): \n')
    c = y.decode('unicode-escape')
    nf.write(c)                
    nf.write('\n')

# Function: write_to_summary_file(essay_fname,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr_se,ranked_global_weights,reorganised_array,i_toprank,c_toprank,nf,nf2)    
# Called by debora_results_se in this file.
def write_to_summary_file(essay_fname,paras,number_of_words,\
                          countTrueSent,countSentLen,countAvSentLen,\
                          countAssQSent,countTitleSent,
                          nodes,edges,edges_over_sents,\
                          len_headings,\
                          ranked_global_weights,\
                          b_last,len_body,len_refs,refsheaded,late_wc,appendixheaded,\
                          introheaded,i_first,i_last,i_toprank,countIntroSent,percent_body_i,\
                          conclheaded,c_first,c_last,c_toprank,countConclSent,percent_body_c,\
                          nf,nf2):

    
    #nf2.write(str(essay_fname)) # Write current essay file name to the summary results file
    #nf2.write('; ') # Add a blank line to the summary results file

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
    nf2.write(str(paras))
    nf2.write('; ')
    ################# begin new
    nf2.write('body last #; ')
    nf2.write(str(b_last))
    nf2.write('; ')
    nf2.write('refs head; ')
    nf2.write(str(refsheaded))
    nf2.write('; ')
    nf2.write('len refs; ')
    nf2.write(str(len_refs))
    nf2.write('; ')
    nf2.write('appndx head; ')
    nf2.write(str(appendixheaded))
    nf2.write('; ')
    nf2.write('late_wc; ')
    nf2.write(str(late_wc))
    nf2.write('; ')
    ######################## end new    
    nf2.write('heads; ')  # Total number of headings
    nf2.write(str(len_headings))
    nf2.write('; ')
    nf2.write('non-heading paras; ')
    nf2.write(str(len_body))
    nf2.write('; ')
    nf2.write('intro head; ')
    nf2.write(str(introheaded))
    nf2.write('; ')
    nf2.write('% body == i; ')
    nf2.write(str(percent_body_i))
    nf2.write('; ') 
    nf2.write('i sents; ')
    nf2.write(str(countIntroSent))
    nf2.write('; ')
    nf2.write('concl head; ')
    nf2.write(str(conclheaded))
    nf2.write('; ')
    nf2.write('% body == c; ')
    nf2.write(str(percent_body_c))
    nf2.write('; ')    
    nf2.write('c sents; ')
    nf2.write(str(countConclSent))
    nf2.write('; ')    
    ################### begin new
    nf2.write('t sents; ')         # How many sentences are labelled 'title'
    nf2.write(str(countTitleSent))
    nf2.write('; ')
    nf2.write('q sents; ')         # How many sentences are labelled 'assignment question'
    nf2.write(str(countAssQSent))
    nf2.write('; ')
    #################### end new
    nf2.write('nodes; ')         
    nf2.write(str(nodes))
    nf2.write('; ')
    nf2.write('edges; ')                       
    nf2.write(str(edges))
    nf2.write('; ')
    nf2.write('edges/sents; ')
    nf2.write(str(edges_over_sents))
    nf2.write('; ') 
    nf2.write('i & toprank; ') 
    nf2.write(str(i_toprank)) # i_toprank is the number of top-ranking sentences that are in the introduction
    nf2.write('; ') 
    nf2.write('c & toprank; ') 
    nf2.write(str(c_toprank)) # i_toprank is the number of top-ranking sentences that are in the introduction
    nf2.write('; ')
    r = ranked_global_weights[0][0]
    nf2.write('se top centr score; ')
    s = round(r,5)
    nf2.write(str(s))
    nf2.write('; ')
    

def get_essay_stats_se(gr_se,text,headings,ranked_global_weights,reorganised_array):
    rankorder = []
    for item in ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        key = item[1] # xxxx this line if you want a list of integers (ranked sentence numbers) with no other info
        #key = item[3] # xxxx this line is you want a list of sentences only (for producing clean results for testing purposes)
        rankorder.append(key)
        
    paras = len(text)   
    
    countTrueSent = 0
    countSentLen = 0
    truesents = []
    for item in reorganised_array: # For each member of the list/array (each sentence)
        tidysent = item[4]
        countSentLen += len(tidysent) # the sum of the lengths of all true tidysents
        label = item[2]
        if label == '#+s#' or label == '#+s:i#' or label == '#+s:c#' or label == '#+s:s#' or label == '#+s:p#':
            countTrueSent += 1
            truesents.append(item[1]) # Get a list of the node numbers for the true sentences to use later in making a sample graph
        else:
            countTrueSent = countTrueSent
    #print '\n\nTHIS IS REORGANISED ARRAY ITEM: ', item
    countIntroSent = 0
    countConclSent = 0
    countTitleSent = 0
    countAssQSent = 0
    for item in reorganised_array:
        label = item[2]
        if label == '#+s:i#':
            countIntroSent += 1  # Count the number of sentences in the introduction
        if label == '#+s:c#':
            countConclSent += 1  # Count the number of sentences in the conclusion
        if label == '#-s:t#':
            countTitleSent += 1  # Count the number of sentences in the title
        if label == '#-s:q#':
            countAssQSent += 1  # Count the number of sentences in the essay that are lifted from the assignment question
    if countTrueSent > 0:
        countAvSentLen = float(countSentLen) / float(countTrueSent)
        countAvSentLen = round(countAvSentLen, 2)
    else:
        countAvSentLen = []

    len_headings = len(headings)
    len_body = len(text) - len(headings)  

    getcontext().prec = 3
    if countIntroSent > 0: 
        ## @todo: added str() to ensure backward compatibility with Python 2.6
        percent_body_i = 100 * Decimal(str(1.0/(countTrueSent / countIntroSent))) # y is the percentage of the essay body taken up by the introduction
    else: # xxxx This condition should not succeed for any essay, but some test files don't return a result for intro section, in which case countIntroSent == 0, which returns an error on the previous line. Needs a better fix. 
        percent_body_i = 0
    percent_body_i = float(percent_body_i)

    if countConclSent > 0:
        ## @todo: added str() to ensure backward compatibility with Python 2.6
        percent_body_c = 100 * Decimal(str(1.0/(countTrueSent / countConclSent))) # y is the percentage of the essay body taken up by the introduction
    else:
        percent_body_c = 0
    percent_body_c = float(percent_body_c)

    edges = len(gr_se.edges())   
    nodes = len(gr_se.nodes())

    #print 'This is float(edges)', float(edges)
    #print 'This is float(countTrueSent)', float(countTrueSent)
    if countTrueSent > 0:
        x = float(edges) / float(countTrueSent)
    else:
        x = 0
    #print 'This is float(edges) / float(countTrueSent) ', x  
    edges_over_sents = round(x, 2)

    i_toprank,c_toprank = cf_keysents_sections(ranked_global_weights)

    return paras, rankorder,len_body,len_headings,countSentLen,truesents,countTrueSent,countAvSentLen,countIntroSent,countConclSent,countAssQSent,countTitleSent,percent_body_i,i_toprank,percent_body_c,c_toprank,nodes,edges,edges_over_sents


def print_processing_times(getassdatatime,processasstexttime,processtbindextime,startassdatatime,startfiletime, texttime, structime, se_scorestime, ke_scorestime, nf2):
    getassdataproctime  = getassdatatime - startassdatatime
    processasstextproctime = processasstexttime - getassdatatime 
    processtbindexproctime = processtbindextime - processasstexttime


    totalassdataproctime =  processtbindextime - startassdatatime
    textproctime = texttime - processtbindextime # Work out how long different parts of the program took to run...
    strucproctime = structime - texttime
    se_scoresproctime = se_scorestime - structime
    ke_scoresproctime = ke_scorestime - se_scorestime
    totalproctime = ke_scorestime - startassdatatime
    
##    graphproctime = graphtime - texttime
##    scoresproctime = scorestime - graphtime
##    totalproctime = scorestime - startfiletime
##    importproctime = endimporttime - startprogtime # Get some more processing timings   
    nf2.write('\ngetassdata processing time: ')
    nf2.write(str(getassdataproctime))
    nf2.write('\nprocessasstext processing time: ')
    nf2.write(str(processasstextproctime))
    nf2.write('\nprocesstbindex processing time: ')
    nf2.write(str(processtbindexproctime))
    nf2.write('\nTOTAL ASS DATA PROC TIME: ')
    nf2.write(str(totalassdataproctime))
    nf2.write('\nEssay pre-processing time: ')
    nf2.write(str(textproctime))
    nf2.write('\nStruc processing time: ')
    nf2.write(str(strucproctime))
    nf2.write('\nSE scores processing time: ')
    nf2.write(str(se_scoresproctime))
    nf2.write('\nKE scores processing time: ')
    nf2.write(str(ke_scoresproctime))
    nf2.write('\nTotal processing time: ')
    nf2.write(str(totalproctime))
    nf2.write('\n\n*********************************************************\n\n')
    #nf2.write('\n\n')



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



# Function: debora_write_results_se(essay_fname,paras,rankorder,number_of_words,...)
# Prints and writes to file various results I want to see.
# Called in se_main.py.
def debora_write_results_se(essay_fname,\
            paras,rankorder,number_of_words,\
            countTrueSent,countSentLen,countAvSentLen,\
            nodes,edges,edges_over_sents,\
            ranked_global_weights,reorganised_array,\
            section_names,section_labels,headings,len_headings,\
            countAssQSent,countTitleSent,
            b_last,len_body,len_refs,refsheaded,late_wc,appendixheaded,\
            introheaded,i_first,i_last,i_toprank,countIntroSent,percent_body_i,\
            conclheaded,c_first,c_last,c_toprank,countConclSent,percent_body_c,\
            nf,nf2):
    write_to_details_file(essay_fname,paras,rankorder,number_of_words,\
    section_names,section_labels,headings,\
    conclheaded,c_first,c_last,introheaded,i_first,i_last,\
    ranked_global_weights,reorganised_array,i_toprank,c_toprank,\
    nf,nf2)
    write_to_summary_file(essay_fname,paras,number_of_words,\
                          countTrueSent,countSentLen,countAvSentLen,\
                          countAssQSent,countTitleSent,
                          nodes,edges,edges_over_sents,\
                          len_headings,\
                          ranked_global_weights,\
                          b_last,len_body,len_refs,refsheaded,late_wc,appendixheaded,\
                          introheaded,i_first,i_last,i_toprank,countIntroSent,percent_body_i,\
                          conclheaded,c_first,c_last,c_toprank,countConclSent,percent_body_c,\
                          nf,nf2)



        
# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
