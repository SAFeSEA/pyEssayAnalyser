import re # For regular expressions
#import sys
#from time import time # For calculating processing times
#from decimal import getcontext, Decimal



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
def debora_write_results_se(essay_fname,\
"""

# Function: write_to_details_file(essay_fname,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr_se,ranked_global_weights,reorganised_array,i_toprank,c_toprank,nf,nf2):
# Called by debora_results_se in this file.
#def write_to_details_file(essay_fname,text,number_of_words,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last,gr_se,ranked_global_weights,reorganised_array,i_toprank,c_toprank,nf,nf2):
def write_to_details_file(essay_fname,\
    paras,rankorder,number_of_words,\
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

##    # xxxx do not delete. Do you want all the sentences or do you want the top N?
##    nf.write('\nSentences ranked in key-ness order (descending): \n')
##    s = str(rankorder) # ...and write them to the results file so you can see the order at a glance.
##    c = s.decode('unicode-escape')
##    nf.write(c)
##    nf.write('\n')    
    
    # xxxx Do you want all the sentences or do you want the top N ('threshold')?
    nf.write('\nTop ')
    threshold = 25
    nf.write(str(threshold))
    nf.write(' sentences ranked in key-ness order (descending): \n')    
    s = str(rankorder[:threshold]) # ...and write them to the results file so you can see the order at a glance.
    #w = re.sub('u\'', 'u\'\n\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    #w = re.sub('u\'', 'u\'\n\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    c = s.decode('unicode-escape')
    nf.write(c)
    nf.write('\n')    
    
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
                          countTrueSent,countTrueSentChars,\
                          countFalseSent,countSentLen,countAvSentLen,\
                          countAssQSent,countTitleSent,\
                          countTableEnt,countListItem,\
                          nodes,edges,edges_over_sents,\
                          len_headings,\
                          ranked_global_weights,\
                          b_last,countProseSents,countProseChars,len_refs,refsheaded,late_wc,\
                          appendixheaded,\
                          introheaded,i_first,i_last,i_toprank,\
                          countIntroSent,countIntroChars,percent_body_i,\
                          conclheaded,c_first,c_last,c_toprank,
                          countConclSent,countConclChars,percent_body_c,\
                          nf,nf2):    
    print ' '
    #nf2.write('\n')
    
    #nf2.write(str(essay_fname)) # Write current essay file name to the summary results file
    #nf2.write('; ') # Add a blank line to the summary results file


    #####################
    #####################
    ## FULL SET
    #####################
    #####################
    nf2.write('all words; ') 
    nf2.write(str(number_of_words))
    nf2.write('; ')
    nf2.write('tidy words; ') 
    nf2.write(str(countSentLen))
    nf2.write('; ')
    nf2.write('avlen tidysent; ')
    nf2.write(str(countAvSentLen))
    nf2.write('; ')
    nf2.write('paras; ') # Total number of paragraphs
    nf2.write(str(paras))
    nf2.write('; ')
    nf2.write('body last #; ')
    nf2.write(str(b_last))
    nf2.write('; ')
    nf2.write('refs head; ')
    nf2.write(str(refsheaded))
    nf2.write('; ')
    nf2.write('refs; ')
    nf2.write(str(len_refs))
    nf2.write('; ')
    nf2.write('appndx head; ')
    nf2.write(str(appendixheaded))
    nf2.write('; ')
    nf2.write('late_wc; ')
    nf2.write(str(late_wc))
    nf2.write('; ')  
    nf2.write('heads; ')  # Total number of true headings. Currently '#-s:h#', '#-s:H#','#-s:t#','#-s:s#','#-s:d#','#-s:l#'
    nf2.write(str(len_headings))
    nf2.write('; ')
    nf2.write('table ents; ')
    nf2.write(str(countTableEnt))
    nf2.write('; ')
    nf2.write('list items; ')
    nf2.write(str(countListItem))
    nf2.write('; ')                              
    nf2.write('prose sents; ')
    nf2.write(str(countProseSents))
    nf2.write('; ')
    nf2.write('prose chars; ')
    nf2.write(str(countProseChars))
    nf2.write('; ')
    nf2.write('nodes; ')         
    nf2.write(str(nodes))
    nf2.write('; ')
    nf2.write('edges; ')                       
    nf2.write(str(edges))
    nf2.write('; ')
##    nf2.write('false sents; ')   # Note, This is meaningless at the moment, but I'm leaving it in case I want to do something similar.      
##    nf2.write(str(countFalseSent))
##    nf2.write('; ')    
    nf2.write('true sents; ')         
    nf2.write(str(countTrueSent))
    nf2.write('; ')    
    nf2.write('true sent chars; ')         
    nf2.write(str(countTrueSentChars))
    nf2.write('; ')    
    nf2.write('edges/sents; ')
    nf2.write(str(edges_over_sents))
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
    nf2.write('i chars; ')
    nf2.write(str(countIntroChars))
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
    nf2.write('c chars; ')
    nf2.write(str(countConclChars))
    nf2.write('; ')        
    nf2.write('t sents; ')         # How many sentences are labelled 'title'
    nf2.write(str(countTitleSent))
    nf2.write('; ')
    nf2.write('q sents; ')         # How many sentences are labelled 'assignment question'
    nf2.write(str(countAssQSent))
    nf2.write('; ')
    nf2.write('i & toprank; ') 
    nf2.write(str(i_toprank)) # i_toprank is the number of top-ranking sentences that are in the introduction
    nf2.write('; ') 
    nf2.write('c & toprank; ') 
    nf2.write(str(c_toprank)) # i_toprank is the number of top-ranking sentences that are in the introduction
    nf2.write('; ')
    if len(ranked_global_weights)>0: # edge case condition
        r = ranked_global_weights[0][0]
    else:
        r = 'nil'
    nf2.write('se top centr score; ')
    #s = round(r,5)
    nf2.write(str(r))
    nf2.write('; ')


##    ###################
##    ###################
##    ## PARTIAL SET
##    ###################
##    ###################
##    nf2.write('all words; ') 
##    nf2.write(str(number_of_words))
##    nf2.write('; ')
##    nf2.write('tidy words; ') 
##    nf2.write(str(countSentLen))
##    nf2.write('; ')
##    nf2.write('true sents; ')         
##    nf2.write(str(countTrueSent))
##    nf2.write('; ')
##    nf2.write('avlen tidysent; ')
##    nf2.write(str(countAvSentLen))
##    nf2.write('; ')
##    nf2.write('paras; ') # Total number of paragraphs
##    nf2.write(str(paras))
##    nf2.write('; ')
##    ################# begin new
####    nf2.write('body last #; ')
####    nf2.write(str(b_last))
####    nf2.write('; ')
####    nf2.write('refs head; ')
####    nf2.write(str(refsheaded))
####    nf2.write('; ')
##    nf2.write('len refs; ')
##    nf2.write(str(len_refs))
##    nf2.write('; ')
####    nf2.write('appndx head; ')
####    nf2.write(str(appendixheaded))
####    nf2.write('; ')
####    nf2.write('late_wc; ')
####    nf2.write(str(late_wc))
####    nf2.write('; ')
##    ######################## end new    
##    nf2.write('heads; ')  # Total number of headings
##    nf2.write(str(len_headings))
##    nf2.write('; ')
####    nf2.write('non-heading paras; ')
####    nf2.write(str(countProseSents))
####    nf2.write('; ')
####    nf2.write('intro head; ')
####    nf2.write(str(introheaded))
####    nf2.write('; ')
####    nf2.write('% body == i; ')
####    nf2.write(str(percent_body_i))
####    nf2.write('; ') 
####    nf2.write('i sents; ')
####    nf2.write(str(countIntroChars))
####    nf2.write('; ')
####    nf2.write('concl head; ')
####    nf2.write(str(conclheaded))
####    nf2.write('; ')
####    nf2.write('% body == c; ')
####    nf2.write(str(percent_body_c))
####    nf2.write('; ')    
####    nf2.write('c sents; ')
####    nf2.write(str(countConclChars))
####    nf2.write('; ')    
##    ################### begin new
####    nf2.write('t sents; ')         # How many sentences are labelled 'title'
####    nf2.write(str(countTitleSent))
####    nf2.write('; ')
####    nf2.write('q sents; ')         # How many sentences are labelled 'assignment question'
####    nf2.write(str(countAssQSent))
####    nf2.write('; ')
##    #################### end new
####    nf2.write('nodes; ')         
####    nf2.write(str(nodes))
####    nf2.write('; ')
##    nf2.write('edges; ')                       
##    nf2.write(str(edges))
##    nf2.write('; ')
##    nf2.write('edges/sents; ')
##    nf2.write(str(edges_over_sents))
##    nf2.write('; ') 
####    nf2.write('i & toprank; ') 
####    nf2.write(str(i_toprank)) # i_toprank is the number of top-ranking sentences that are in the introduction
####    nf2.write('; ') 
####    nf2.write('c & toprank; ') 
####    nf2.write(str(c_toprank)) # i_toprank is the number of top-ranking sentences that are in the introduction
####    nf2.write('; ')
##    if len(ranked_global_weights)>0: # edge case condition
##        r = ranked_global_weights[0][0]
##    else:
##        r = 'nil'
##    nf2.write('se top centr score; ')
##    #s = round(r,5)
##    nf2.write(str(r))
##    nf2.write('; ')    
    

def get_essay_stats_se(gr_se,text,headings,ranked_global_weights,reorganised_array):
    rankorder = []
    for item in ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        key = item[1] # xxxx this line if you want a list of integers (ranked sentence numbers) with no other info
        #key = item[3] # xxxx this line if you want a list of sentences only (for producing clean results for testing purposes)
        rankorder.append(key)
        
    paras = len(text)   
    
    countTrueSent = 0
    countTrueSentChars = 0
    countFalseSent = 0
    countSentLen = 0
    truesents = []
    for item in reorganised_array: # For each member of the list/array (each sentence)
        tidysent = item[4]
        countSentLen += len(tidysent) # the sum of the lengths of all true tidysents
        label = item[2]
        if label == '#+s#' or label == '#+s:i#' or label == '#+s:c#' or label == '#+s:s#' or label == '#+s:p#':
            countTrueSent += 1
            countTrueSentChars += len(item[3]) #1  # Count the number of characters in a true sentence 
            truesents.append(item[1]) # Get a list of the node numbers for the true sentences to use later in making a sample graph
        else:
            #countTrueSent = countTrueSent
            countFalseSent +=1
    #print '\n\nTHIS IS REORGANISED ARRAY ITEM: ', item
    #section_names =  ['AssQ',  'Title', 'SectionHeadings', 'SpecialHeadings', 'GeneralHeadings','ItemisedShort', 'TableEntries', 'Captions', 'DigitalHeadings', 'LetterHeadings', 'Introduction', 'Conclusion', 'Summary', 'Preface', 'Numerics', 'Punctuation']
    #section_labels = ['#-s:q#','#-s:t#','#-s:s#',          '#-s:h#',          '#-s:H#',         '#-s:b#',        '#-s:e#',       '#-s:c#',   '#-s:d#',          '#-s:l#',         '#+s:i#',       '#+s:c#',     '#+s:s#',  '#+s:p#',  '#-s:n#',   '#-s:p#']
             
    countIntroChars = 0
    countConclChars = 0
    countDiscChars = 0
    countIntroSent = 0
    countConclSent = 0
    countDiscSent = 0
    
    countTitleSent = 0
    countAssQSent = 0
    countSpecHead = 0
    countGenHead = 0
    countTableEnt = 0
    countListItem = 0
    countSectHead = 0
    countCaption = 0
    countDigitalHead = 0
    countLetterHead = 0
    for item in reorganised_array: # (0.0008982035928143714, 165, '#-s:H#', u'Acknowledgments', [(u'acknowledgments', u'acknowledgment')])
        label = item[2]
        if label == '#-s:q#':
            countAssQSent += 1  # Count the number of sentences in the essay that are lifted from the assignment question
        if label == '#-s:t#':
            countTitleSent += 1  # Count the number of sentences in the title
        if label == '#-s:s#':
            countSectHead += 1  # Count the number of section headings
        if label == '#-s:h#':
            countSpecHead += 1  # Count the number of special headings
        if label == '#-s:H#':
            countGenHead += 1  # Count the number of general headings
        if label == '#-s:d#':
            countDigitalHead += 1  # Count the number of headings beginning with a digit
        if label == '#-s:l#':
            countLetterHead += 1  # Count the number of headings beginning with a letter
            
        if label == '#-s:b#':
            countListItem += 1  # Count the number of paras that are short bullet points and list items
        if label == '#-s:e#':
            countTableEnt += 1  # Count the number of paras that are table entries
        if label == '#-s:c#':
            countCaption += 1  # Count the number of captions
   
        if label == '#+s:i#':
            countIntroChars += len(item[3]) #1  # Count the number of characters in a sentence in the introduction
        if label == '#+s:c#':
            countConclChars += len(item[3]) #1  # Count the number of characters in a sentence in the conclusion
        if label == '#+s#':
            countDiscChars += len(item[3]) #1  # Count the number of characters in a sentence in the discussion
        if label == '#+s:i#':
            countIntroSent += 1  # Count the number of sentences in the introduction
        if label == '#+s:c#':
            countConclSent += 1  # Count the number of sentences in the conclusion
        if label == '#+s#':
            countDiscSent += 1  # Count the number of sentences in the discussion

    if countTrueSent > 0:
        countAvSentLen = float(countSentLen) / float(countTrueSent)
        countAvSentLen = round(countAvSentLen, 2)
    else:
        countAvSentLen = []

    len_headings = len(headings)

    countProseSents = countIntroSent + countConclSent + countDiscSent

    countProseChars = countIntroChars + countConclChars + countDiscChars

    #getcontext().prec = 3
    if countIntroChars > 0: 
        ## @todo: added str() to ensure backward compatibility with Python 2.6
        #print countTrueSent
        #print countIntroChars
        x = 1.0/(float(countTrueSentChars)/float(countIntroChars))
        #print x
        #percent_body_i = 100 * Decimal(str(1.0/(countTrueSent / countIntroChars))) # y is the percentage of the essay body taken up by the introduction
        percent_body_i = 100 * x
        #print percent_body_i
    else: # xxxx This condition should not succeed for any essay, but some test files don't return a result for intro section, in which case countIntroChars == 0, which returns an error on the previous line. Needs a better fix. 
        percent_body_i = 0
    #percent_body_i = float(percent_body_i)
    percent_body_i = round(percent_body_i,2)
    print 'Per cent body i:', percent_body_i
    

    if countConclChars > 0:
        ## @todo: added str() to ensure backward compatibility with Python 2.6
        x = 1.0/(float(countTrueSentChars)/float(countConclChars))
        percent_body_c = 100 * x
    else:
        percent_body_c = 0
    percent_body_c = round(percent_body_c,2)
    print 'Per cent body c:', percent_body_c
    

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

    return paras, rankorder,countProseSents,countProseChars,len_headings,\
           countSentLen,truesents,countTrueSent,countTrueSentChars, countFalseSent,\
           countAvSentLen,countIntroSent,countIntroChars,countConclSent,\
           countConclChars,countAssQSent,\
           countTableEnt,countListItem,\
           countTitleSent,percent_body_i,i_toprank,percent_body_c,\
           c_toprank,nodes,edges,edges_over_sents


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
##    nf2.write('\ngetassdata processing time: ')
##    nf2.write(str(getassdataproctime))
##    nf2.write('\nprocessasstext processing time: ')
##    nf2.write(str(processasstextproctime))
##    nf2.write('\nprocesstbindex processing time: ')
##    nf2.write(str(processtbindexproctime))
##    nf2.write('\nTOTAL ASS DATA PROC TIME: ')
##    nf2.write(str(totalassdataproctime))
##    nf2.write('\nEssay pre-processing time: ')
##    nf2.write(str(textproctime))
##    nf2.write('\nStruc processing time: ')
##    nf2.write(str(strucproctime))
##    nf2.write('\nSE scores processing time: ')
##    nf2.write(str(se_scoresproctime))
##    nf2.write('\nKE scores processing time: ')
##    nf2.write(str(ke_scoresproctime))
##    nf2.write('\nTotal processing time: ')
##    nf2.write(str(totalproctime))
##    nf2.write('\n\n*********************************************************\n\n')
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
            countTrueSent,countTrueSentChars,\
            countFalseSent,countSentLen,countAvSentLen,\
            nodes,edges,edges_over_sents,\
            ranked_global_weights,reorganised_array,\
            section_names,section_labels,headings,len_headings,\
            countAssQSent,countTitleSent,
            countTableEnt,countListItem,\
            b_last,countProseSents,countProseChars,len_refs,refsheaded,late_wc,appendixheaded,\
            introheaded,i_first,i_last,i_toprank,countIntroSent,countIntroChars,percent_body_i,\
            conclheaded,c_first,c_last,c_toprank,
            countConclSent,countConclChars,percent_body_c,\
            nf,nf2):
    write_to_details_file(essay_fname,paras,rankorder,number_of_words,\
    section_names,section_labels,headings,\
    conclheaded,c_first,c_last,introheaded,i_first,i_last,\
    ranked_global_weights,reorganised_array,i_toprank,c_toprank,\
    nf,nf2)
    write_to_summary_file(essay_fname,paras,number_of_words,\
                          countTrueSent,countTrueSentChars,\
                          countFalseSent,countSentLen,countAvSentLen,\
                          countAssQSent,countTitleSent,\
                          countTableEnt,countListItem,\
                          nodes,edges,edges_over_sents,\
                          len_headings,\
                          ranked_global_weights,\
                          b_last,countProseSents,countProseChars,len_refs,refsheaded,late_wc,\
                          appendixheaded,\
                          introheaded,i_first,i_last,i_toprank,\
                          countIntroSent,countIntroChars,percent_body_i,\
                          conclheaded,c_first,c_last,c_toprank,\
                          countConclSent,countConclChars,percent_body_c,\
                          nf,nf2)




        
# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
