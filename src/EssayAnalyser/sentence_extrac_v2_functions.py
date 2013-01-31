import re # For regular expressions
#import sbd # For alternative sentence splitter
import networkx as nx # This is for implementing networks/graphs
#import math 
#import random # Needed if I seed scores_array with random numbers instead of the same number
from time import time # For calculating processing times
from nltk.corpus import stopwords # For removing uninteresting words from the text
#from nltk import PunktSentenceTokenizer 
from nltk.tokenize import WordPunctTokenizer # Word tokeniser that separates punctuation marks from words
from nltk.tokenize import LineTokenizer # "tokenizer that divides a string into substrings by treating any single newline character as a separator."
from nltk import PunktSentenceTokenizer # The standard sentence tokeniser used by NLTK
from uuid import uuid4 # For generation of unique identifier
from operator import itemgetter

""""
Functions names:
# Function: get_essay_body
# Function: update_text
# Function: restore_quote
# Function: tidy_up_latin9
# Function: sentence_tokenize
# Function: word_tokenize
# Function: remove_punc_fm_sents
# Function: count_words
# Function: lowercase_sents
# Function: process_sents
# Function: remove_stops_fm_sents
# Function: find_and_label_numeric_sents
# Function: label_section_sents
# Function: count_this_heading
# Function: find_last_section_para_index
# Function: find_first_section_para_index
# Function: find_first_intro_para_index
# Function: find_no_intro_heading_indices
# Function: find_first_concl_para_index
# Function: find_no_concl_heading_indices
# Function: find_title_indices
# Function: find_section_paras
# Function: find_and_label_headings
# Function: get_headings
# Function: match_sentence_2_heading
# Function: get_more_headings_using_contents
# Function: add_item_to_array
# Function: add_to_sentence_array
# Function: fill_sentence_array
# Function: make_scores_array
# Function: make_graph_building_arrays
# Function: find_cosine_similarity
# Function: add_one_nodes_edges
# Function: add_all_node_edges
# Function: find_global_weight_score
# Function: find_all_gw_scores
# Function: update_array
# Function: reorganise_array
# Function: sort_ranked_sentences
# Function: analyse_intro_concl
# Function: print_structure_feedback                
# Function: print_scores_info         
# Function: print_section_sents
# Function: print_processing_times
# Function: pre_process_essay
# Function: process_essay
# Function: debora_results
# Function: nicolas_results
"""

# Function: get_essay_body
# Currently this gets all that occurs before the bibliography
#(actually before the last occurrence of the term 'references' (or ...)). 
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
# I have tried various ways of using a disjunction for this, but have not yet succeeded.
def get_essay_body(text,nf,dev):
    if 'References' in text:
        a = text.rfind('References') # Find the LAST occurrence of 'References', not the first, in case there is a contents page or other xref.        
        b = text[:a] # Get all the text of the essay occurring before the bibliography (the body).
        return b, 'yes'    
    elif 'REFERENCES' in text:
        a = text.rfind("REFERENCES") 
        b = text[:a] 
        return b, 'yes'
    elif 'Reference' in text: # One essay I looked at had the bibliography section title: 'Reference list'.
        a = text.rfind("Reference") 
        b = text[:a] 
        return b, 'yes'
    elif 'REFERENCE' in text: # One essay I looked at had: 'REFERENCE'.
        a = text.rfind("REFERENCE") 
        b = text[:a] 
        return b, 'yes'         
    elif 'Bibliography' in text:
        a = text.rfind("Bibliography") 
        b = text[:a] 
        return b, 'yes'
    else:
        if dev == 'DGF':
            print '\n********* Cannot find a references section. *********\n'
            nf.write('\n********* Cannot find a references section. *********\n')
        return text, 'no' # If none of those terms are in text, just return text.

# Function: update_text
# A basic substitution operation that carries out character substitution in a text (a list of words).
# Called by restore_quote.
# Returns updated text.
def update_text(text, x, y, counter):
    list.remove(text, x) # Substitute the new string you have made for the old string.
    list.insert(text, counter, y) # (There must be a better way of doing this.)
    return text             

# Function: restore_quote
# Reinstate the SECOND of a pair of quotation marks.
# Note: Be careful to skip over word-initial question marks,
# which are the beginning of embedded quotations.
# Called by 'tidy_up_latin9'.
# Returns updated text.
def restore_quote(text, counter):
    while 1:
        if counter <= len(text)-1:        
            x = text[counter]
            if not x.startswith('?'): # We need the 'not x.startswith...' because there may be an embedded quotation and we are looking for the closing speech/question mark of a pair.
                if x.endswith('?.'): # For 'dizzy?.' cases
                    #y = x.replace('\?.', "'.")
                    y = re.sub('\?.', "'.", x)
                    result = update_text(text, x, y, counter)
                    return result             
                elif x.endswith('?,'): # "dizzy?," becomes "dizzy',"
                    y = re.sub('\?,', "',", x)
                    result = update_text(text, x, y, counter)
                    return result             
                elif x.endswith('?;'): # "dizzy?;" becomes "dizzy';" 
                    y = re.sub('\?;', "';", x)
                    result = update_text(text, x, y, counter)
                    return result             
                elif x.endswith('?:'): # "dizzy?:" becomes "dizzy':"
                    y = re.sub('\?:', "':", x)
                    result = update_text(text, x, y, counter)
                    return result             
                elif x.endswith('.?'): # "dizzy.?" becomes "dizzy.'"
                    y = re.sub('\.\?', ".'", x)
                    result = update_text(text, x, y, counter)
                    return result             
                elif x.endswith('.?\n'): # "dizzy.?\n" becomes "dizzy.'\n"
                    y = re.sub('\.\?\n', ".'\n", x)
                    result = update_text(text, x, y, counter)
                    return result             
                elif x.endswith('?'):  # "dizzy?" becomes "dizzy'" and "that??" becomes "that?'".      
                    y = re.sub('\?$', "'", x)
                    result = update_text(text, x, y, counter)
                    return result             
                else: # If x doesn't start with '?' but doesn't have any of these endings, try the next word
                    counter += 1
            else: # If x does start with '?', try the next word
                counter += 1
        else:
            break # Stop when you get to the end of the text.                    
    
# Function: tidy_up_latin9
# Text saved in encoding Latin9 substitutes a question mark for
# curly speech marks and curly apostrophes and en-dashes and em-dashes.
# This function replaces dashes with hyphens and puts back apostrophes and speech marks.
# It does not cover every case, but it does a reasonable job.
# Returns updated text.
def tidy_up_latin9(text):
    counter = 0
    text = [re.sub('\n\?$', "\n* ", w) for w in text] # paragraph-initial question mark followed by whitespace replaced with paragraph marker then a star then a space
    text = [re.sub('\\xfc', "o", w) for w in text] # 'u umlaut' 
    text = [re.sub('\\xf6', "o", w) for w in text] # 'o umlaut' 
    text = [re.sub('\\xb9', "", w) for w in text] # footnote marker     
    text = [re.sub('\\xe9', "e", w) for w in text] # 'e accute' 
    text = [re.sub('\\xa3', "GBP ", w) for w in text] # British pound sign
    text = [re.sub('\\xa0', " ", w) for w in text] 
    text = [re.sub('\t', " ", w) for w in text] # Just getting rid of tab characters that are attached to words
    text = [re.sub('\?t$', "'t", w) for w in text] # Apostrophe: "don?t" becomes "don't"
    text = [re.sub('^\?$', "--", w) for w in text]   # Em-dashes and en-dashes: 'access ? enrolment' becomes 'access -- enrolment'
    text = [re.sub('\?s$', "'s", w) for w in text]   # Apostrophe: "Frankenstein?s" becomes "Frankenstein's"
    text = [re.sub('^p\.$', "p", w) for w in text]   # change 'p.' to 'p'
    while 1: # Now deal with quotation marks (that come in pairs), starting with the first of the pair here.
        if counter <= len(text): # Note that you cannot now just replace every question mark with a quotation mark, because some questions marks really are questions marks.
            for x in text:
                if x.startswith('?'):
                    place = text.index(x) # Find the position of x in the text
                    y = re.sub('^\?', "'", x) # Deal with the word-initial question mark. "?lost?", and, "?dizzy?." become "'lost?", 'and', "'dizzy?."
                    list.remove(text, x) # Substitute the new string you have made for the old string
                    list.insert(text, place, y)
                    restore_quote(text, place) # Find where the closing quote (qmark) of the pair should be and put quote mark back 
                    counter += 1 
                elif '\n?' in x:                   
                    place = text.index(x) # Find the position of x in the text
                    y = re.sub('\n\?', "\n'", x) # Deal with the new line followed by question mark. "states:\n?Accessibility", becomes "states:\n'Accessibility"
                    list.remove(text, x) # Substitute the new string you have made for the old string
                    list.insert(text, place, y)                    
                    restore_quote(text, place) # Find where the closing quote (qmark) of the pair should be and put quote mark back                     
                    counter += 1
                else:
                    counter += 1
        else:
            break
    return text

# Function: sentence_tokenize
# An alternative sentence tokenizer that does a better job with abbreviations,
# but it takes several seconds to load the model.
# Returns tokenised text.
##def sentence_tokenize(model,text):
##    mylist1 = []
##    for para in text:
##        temp = sbd.sbd_text(model, para)
##        mylist1.append(temp)
##    return mylist1

# Function: word_tokenize
# Word-tokenise a paragraph-sentence-tokenised text.
# There are different word tokenisers available in NLTK. This one
# "divides a text into sequences of alphabetic and non-alphabetic characters".
# This means that punctuation marks are represented as separate tokens from
# the words they adjoin.
# This tokeniser uses quotation marks as word delimiters.
# In the output square brackets are now used to delimit paragraphs AND sentences.
# Returns tokenised text.
def word_tokenize(text):
    mylist = []
    for para in text:
         temp = [WordPunctTokenizer().tokenize(t) for t in para]
         mylist.append(temp)
    return mylist
 
# Function: remove_punc_fm_sents
# Remove from a word-tok sentence all word-tokens that contain
# punctuation marks or series of punctuation marks. 
# Don't remove double hyphens or stars, which can be used as list markers.
# Returns updated sentence.
# Called by process_sents.
def remove_punc_fm_sents(sent):
    temp1 = [re.sub('--', "*", w) for w in sent] # Change double hyphens to stars, and then don't delete stars. Used as list markers. Useful for recognising non-headings.            
    temp = [w for w in temp1 if not re.search('[\.\|\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', w)]
    if temp == []: # If removing all the punc marks leaves an empty sentence
        result = ['#-s:p#']  # label this sentence as punctuation                
    else:
        result = ['#dummy#'] + temp # Otherwise put a 'dummy' label in as a place-holder for proper labels to be added later.
    return result

# Function: count_words
# Count the words in a para-sent-word-tok text.
# Returns number of words. Done after punctuation tokens removed.
def count_words(text):
    mylist = []
    for para in text:
        for sent in para:
            # first element is structure label
            x = sum(1 for w in sent[1:])
            mylist.append(x)
            y = sum(mylist)
    return y

# Function: lowercase_sents
# Given a word-tok sentence, put all word tokens into lower case.
def lowercase_sents(sent):    
    return [w.lower() for w in sent]

# Function: process_sents
# A basic list processor that works through a para-sent-tok text and calls the function 'do_this' with each sentence.
# Is called by 'main'.
def process_sents(do_this, text):
    mylist2 = []
    for para in text:
        mylist1 = []
        for sent in para:
            temp = do_this(sent)
            mylist1.append(temp)
        mylist2.append(mylist1)
    return mylist2

# Function: remove_stops_fm_sents
# Given a sentence, remove all word tokens that are stopwords
# (uninteresting and usually very frequent words).
def remove_stops_fm_sents(sent):
    eng_stopwords=stopwords.words('english')
    return [w for w in sent if w not in eng_stopwords]

# Function: find_and_label_numeric_sents
# If this sentence contains only tokens that contain numbers, label it as a numeric sentence: '#-s:n#'
def find_and_label_numeric_sents(sent):
    temp0 = [item for item in sent if not re.search('[0-9]+',item)] # Get every item in the sent that doesn't contain numbers
    temp2 = [item for item in temp0 if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', item)] # Get every item in the sent that doesn't contain punc
    if sent[0] == '#-s:p#': # Just pass on sents that have already been labelled as punc
        result = sent
    elif temp2 == ['#dummy#']: # If the sentence is empty (apart from a 'dummy' label) after all tokens that contain numbers and punc have been removed 
        temp = ['#-s:n#'] + sent[1:] # Label it as a numeric sentence (replace 'dummy' label with new label)
        result = temp
    else:
        result = sent               
    return result

# Function: label_section_sents
# Called by find_section_paras
# Returns the full essay text having labelled each introduction (summary, conclusion...) sentence with its structural function.
# Does this by labelling every paragraph between and including the first section_name para and the last section_name para
# as already found.
def label_section_sents(text, section_name, section_names, section_labels, section_index_first, section_index_last):
    x = section_names.index(section_name)
    label = section_labels[x]
    if section_name == 'Summary' and section_index_first == [] and section_index_last == []:
        result = text # If there is no 'Summary' heading, assume there is no summary       
    else:
        mylist2 = []
        counter = 0
        while 1:
            if counter <= len(text)-1:
                mylist1 = []
                for sent in text[counter]:
                    if sent[0] == '#dummy#' and section_index_first == section_index_last and counter == section_index_last: # For cases where no heading has been found, both indices are the same, a single paragraph to be labelled
                        temp = [label] + sent[1:]
                        mylist1.append(temp)
                    elif sent[0] == '#dummy#' and section_index_last != [] and counter >= section_index_first and counter <= section_index_last and len(sent) > 1:                    
                        temp = [label] + sent[1:]
                        mylist1.append(temp)
                    else:
                        mylist1.append(sent)
                mylist2.append(mylist1)
                counter += 1
            else:
                break
        result = mylist2
    return result

# Function: count_this_heading
# Go through every heading and see if contains the case-insensitive version of section_name.
# Return a list containing the found headings and their indices.
def count_this_heading(section_name, headings, text):
    mylist = []
    p = re.compile(section_name, re.IGNORECASE)
    for item in headings:
        heading2 = item[0]
        temp = u' '.join(heading2)
        if re.search(p, temp):
            mylist.append(item)
    return mylist

# Function: find_last_section_para_index
# Called by find_section_indices, find_first_section_para_index, find_first_intro_para_index, find_no_intro_heading_indices
# Returns the position of the last section_name paragraph in the essay.
# Does this by finding the heading that follows the heading 'section_name' (already found).
# The para that precedes that next heading is assumed to be the last para of the section.
# Note: assumes that the sections (Intro, Concl, Summary, Preface) don't have headings inside them, which is not true in every case.
def find_last_section_para_index(section_name, heading_index_first, text):
    counter_p = heading_index_first + 1 # Get the paragraph following the para that is the heading
    #counter_p = counter1 + 1     
    position1 = heading_index_first + 1 # position1 is used to ensure we only get the first eligible paragraph returned as the result.
    section_index_last = []
    while 1:         
        if counter_p <= len(text)-1:
            counter_s = 0
            while 2:                
                if counter_s <= len(text[counter_p]) - 1:
                    if text[counter_p][counter_s][0] == '#-s:h#' and counter_p == position1: # See if this paragraph is a section heading
                        section_index_last = counter_p - 1
                        position1 += counter_p
                        counter_s += 1
                        break
                    else:                        
                        counter_s += 1                        
                else:
                    break
            counter_p += 1
            position1 += 1
        else:
            break
    if section_index_last != []: # If you have found a heading following 'heading_index_first'
        result = section_index_last
    elif section_name == 'Conclusion': # If you can't find any headings following 'Conclusion', assume the end of the concl is the last paragraph of the body of the essay.
        temp = len(text)-1
        result = temp
    else:
        result = []
    return result

# Function: find_first_section_para_index
# Called by find_section_paras when a section_name heading has been found.
# Returns the position of the first and last paras of section_name 
def find_first_section_para_index(section_name, first_heading, text):
    counter1 = first_heading
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            # See if this paragraph has label 'dummy'
            if (text[counter1][0][0] == '#dummy#'): 
                    first = counter1
                    last = find_last_section_para_index(section_name, first, text)
                    break                                       
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1                                           
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)

# Function: find_first_intro_para_index
# Called by find_section_paras when an Introduction heading has been found.
# Returns the position of the first and last paras of the introduction.    
def find_first_intro_para_index(section_name, first_heading, text, headings):
    all_heading_indices = [item[1] for item in headings]
    counter1 = first_heading
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:            
            if (text[counter1][0][0] == '#dummy#'): # See if this paragraph has label 'dummy'
                    first = counter1
                    temp = [item for item in all_heading_indices if item > first]
                    if len(temp) > 5: # If there are more than X headings like this... 
                        last = find_last_section_para_index(section_name, first, text) # then look for a heading to mark the end of the intro
                    else: # otherwise if there are only a few headings, assume a one-para intro.
                        last = first # Note: This is quite rough. The idea is that if there are not many headings later than the introduction, there probably aren't any section headings at all. This stops whole essays being marked up as introduction then conclusion.                   
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1                                     
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)
    
# Function: find_no_intro_heading_indices
# Called by find_section_paras when no Introduction heading has been found.
# Returns the indices of the first and last paragraphs of the Introduction section.
# Assumes that the intro is the first para that has not been labelled a heading
# and that is either a multi-sentence para, or has a single long sentence in it.
# Calls find_last_section_para_index under certain conditions.
def find_no_intro_heading_indices(text, headings):
    all_heading_indices = [item[1] for item in headings]
    counter1 = 0
    first = []
    last = []
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            if (text[counter1][0][0] == '#dummy#'  # See if this paragraph has label 'dummy'
                and (len(text[counter1]) > 1 or len(text[counter1][0]) > 14)):  # ...and the paragraph contains more than one sentence, or it's a long sentence
                # Some intro paragraphs may have only one sentence, e.g., Evaldas_Bielskis_B2041593_H810_TMA01_latin9                
                    first = counter1 # Set this paragraph as the first paragraph of the introduction
                    temp = [item for item in all_heading_indices if item > first] # Get all the heading indices that are greater/later than the first intro paragraph 
                    if len(temp) > 3: # If there are more than three headings like this... 
                        last = find_last_section_para_index('Introduction', first, text) # Look for a heading to mark the end of the Introduction.
                        break
                    else: # If there are fewer than three headings like this, set intro to a single paragraph. # Note: This is quite rough. The idea is that if there are not many headings later than the introduction, there probably aren't any section headings at all. This stops whole essays being marked up as introduction then conclusion.                   
                        last = first
                        break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1
        else:
            break # Stop looping when you've dealt with the last paragraph. 
    return (first,last)

# Function: find_first_concl_para_index(text,result_last)
# Called with arguments 'text' and the last paragraph of the essay that is not a heading ('result_last').
# Returns the index of the first paragraph of the conclusion.
# Called by find_no_concl_heading_indices.
def find_first_concl_para_index(text,result_last,headings,nf,dev):
    ((intro_first, intro_last), title_indices) = find_section_paras(text, 'Introduction', headings, nf,dev)
    all_heading_indices = [item[1] for item in headings]
    temp2 = [item for item in all_heading_indices if item < result_last and item > intro_last] # Get all the heading indices that are earlier than the last concl paragraph and later than the last conclusion paragraph.
    counter1 = result_last
    first_concl_para_index = []
    p = re.compile('this report', re.IGNORECASE)
    while 1:
        if counter1 >= 0:
            temp = ' '.join(text[counter1][0])
            if re.search(p, temp): # If the first sentence of this paragraph contains the phrase 'this report', it's prob the first para of the conclusion. Put in for H810_Guy_Cowley_C1264876_TMA01_latin9
                first_concl_para_index = counter1
                break
            elif temp2 == []: # If there are no headings between intro and concl, assume no headings in essay, and set concl to one paragraph.
                first_concl_para_index = counter1                
                break            
            elif text[counter1][0][0] == '#-s:h#': # Otherwise find the heading that precedes 'result_last', increment counter1 by 1, and return value.                            
                first_concl_para_index = counter1 + 1
                break
            else:
                counter1 -= 1
        else:
            break
    return first_concl_para_index

# Function: find_no_concl_heading_indices
# Returns the indices of the first and last paragraph of the conclusion.
# Works out which is the last paragraph, then uses that to find the first.
# Calls find_first_concl_para_index.
# Is called by find_section_paras only if no 'Conclusion' heading has been found.
def find_no_concl_heading_indices(section_name, headings, text,nf, dev):
    list_this_heading = count_this_heading('word count', headings, text)
    heading_count = len(list_this_heading)
    word_count_index = len(text) # Set word_count_index to the index of the last para. If there is no heading for word count in the essay, this will ensure that the main clause doesn't fail.
    if heading_count > 0: # If there is a word count heading, then re-set word count heading to the new value
        word_count_index = list_this_heading[0][1]
    counter1 = len(text) - 1
    first = []
    last = []
    while 1: # Cycle through every sentence of the text backwards from the end 
        if counter1 >= 0:            
            if (text[counter1][0][0] == '#dummy#' # See if this paragraph has label 'dummy'           
                and (len(text[counter1]) > 1 or len(text[counter1][0]) > 14) # ...and the paragraph contains more than one sentence, or it's a long sentence
                and (counter1 < word_count_index)):  
                    last = counter1 # then set this paragraph to the last para of the concl
                    first = find_first_concl_para_index(text,last,headings,nf,dev) # and find the first para
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 -= 1
        else:
            break # Stop looping when you've dealt with the first paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)        

# Function: find_title_indices
# Returns the index of the title.
# Called by find_section_paras.
# Currently configured to allow only on paragraph to be returned (first title para and last title para are the same).
def find_title_indices(index, text):
    counter1 = 0
    first = []
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            if (text[counter1][0][0] == '#dummy#' # See if this paragraph-initial sentence has label 'dummy'
                and len(text[counter1][0][0]) > 5
                and len(text[counter1][0][0]) < 28
                and counter1 < index):# and position3 == counter1):                    
                    first = counter1
                    #last = find_last_section_para_index(section_name, first, text)                    
                    counter1 +=1                                            
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,first)

# Function: find_section_paras
# Is called by 'main' with each section type.
# First counts the number of headings for that section type, then uses the result to decide how to determine which are the section paragraphs.
# Calls different functions depending on section name and number of headings found.
# Uses information found about certain sections to find the index of the title.
def find_section_paras(text, section_name, headings, nf,dev):
    list_this_heading = count_this_heading(section_name, headings, text)
    if section_name == 'Preface': # Once you have counted the heading occurrences, treat prefaces exactly the same as summaries
        section_name = 'Summary'
    heading_count = len(list_this_heading) # heading_count is the number of 'section_name' headings found. Typically 2, 1, or 0. If 2, the first is probably in a contents section.
    first = []
    last = []
    title_indices = ([],[])
    if heading_count == 0 and section_name == 'Summary':
        if dev == 'DGF':
            nf.write('\nNo Summary/Preface heading has been found\n')
            print '\nNo Summary/Preface heading has been found\n'
        True # Don't do anything, para indices remain empty. Not assuming that there is unlabelled Summary section, as we do with Introduction and Conclusion.        
    elif heading_count == 0 and section_name == 'Introduction': # If no 'Introduction' section heading has been found
        (first,last) = find_no_intro_heading_indices(text, headings)
        title_indices = find_title_indices(first, text)
        if dev == 'DGF':
            print '\nNo "Introduction" heading has been found\n'
            nf.write('\nNo "Introduction" heading has been found\n')
    elif heading_count == 0 and section_name == 'Conclusion': # If no 'Conclusion' section heading has been found
        (first,last) = find_no_concl_heading_indices(section_name, headings, text,nf,dev)
        if dev == 'DGF':
            print '\nNo "Conclusion" heading has been found\n'
            nf.write('\nNo "Conclusion" heading has been found\n')
    elif heading_count == 2 and section_name == 'Introduction': # If there are two occurrences of 'Introduction' heading, first is prob contents page, and second prob body section
        first_heading = list_this_heading[1][1] # So take second occurrence as heading of body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        contents_heading_index = list_this_heading[0][1]
        title_indices = find_title_indices(contents_heading_index, text)
        if dev == 'DGF':
            nf.write('\nAn "Introduction" heading has been found \n')
            print '\nAn "Introduction" heading has been found (1) \n'
    elif heading_count == 2 and section_name == 'Conclusion': # If there are two occurrences of 'Conclusion' heading, first is prob contents page, and second prob body section
        first_heading = list_this_heading[1][1] # So take second occurrence as heading of body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            nf.write('\nA "Conclusion" heading has been found\n')
            print '\nA "Conclusion" heading has been found\n'
    elif section_name == 'Introduction': # In all other Introduction cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_intro_para_index(section_name, first_heading, text, headings)
        title_indices = find_title_indices(first, text)
        if dev == 'DGF':
            nf.write('\nA heading has been found for section name:')
            nf.write(str(section_name))
            print '\nA heading has been found for section name:', section_name             
    else: # In all other cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            nf.write('\nA heading has been found for section name:')
            nf.write(str(section_name))
            print '\nA heading has been found for section name:', section_name     
    para_indices = (first, last)
    return (para_indices, title_indices)

# Function: find_and_label_headings
# Label things that are probably headings as headings.
# so that later on you can exclude them from the results that are
# returned to the user, but don't exclude them from the ranking calculations.
def find_and_label_headings(text):
    mylist2 = []
    for para0 in text:
        para2 = [s for s in para0 if s[0] == '#dummy#'] # Delete from the para those sentences that are numerics and puncs leaving only those with label 'dummy'
        mylist1 = []
        counter_s = 0
        paraindex = text.index(para0)
        nextpara = paraindex+1
        while 1:
            if counter_s <= len(para0)-1:
                sent = para0[counter_s]
                sent0 = [item for item in sent if not re.search('[0-9]+',item)] # Get every item in the sent that doesn't contain numbers
                sent1 = [item for item in sent0 if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', item)] # Get every item in the sent that doesn't contain punc                                        
                if sent == ['#-s:p#']: # If the sentence is empty (because it was a stray punctuation mark that has now been removed...)
                    mylist1.append(sent) # just pass it on unchanged.
                else: # First deal with paragraphs of any length that begin with particular types of item                                    
                    firstword = sent[1] # 'firstword' is first actual word following the label
                    x = len(sent) - 1 # Get the last word in the sentence
                    lastword = sent[x]
                    untokend = ' '.join(sent)
                    p = re.compile('table of contents', re.IGNORECASE) # Find out if there is a Table of Contents (for later)
                    if (firstword.startswith('Appendix') # If first word of sentence is 'Appendix'
                        and counter_s == 0): # and this is the first sentence of the paragrah (note that some discussion sentences can start with 'Appendix', 'Figure'...)
                            temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                            mylist1.append(temp)
                    elif firstword.startswith('Figure') and counter_s == 0:  # If first word of sentence is 'Figure' and this is the first sentence of the paragraph
                        temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                        mylist1.append(temp)
                    elif re.search(p, untokend): # This concerns 'table of contents' headings. Added for one essay TMA01_H810_CG4535_Griffiths_latin9 whose last sentence is not part of the conclusion, but it was not being picked up as a heading
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif firstword == '*' and counter_s == 0: # if this sent starts with a bullet point, it's probably not a heading
                        temp = ['#dummy#'] + sent[1:]
                        mylist1.append(temp)
                    elif len(sent0) <= 3 and counter_s == 0: # If this sent is very short (two or fewer words), it's probably a heading, even if it's not a whole paragraph. TMA0001_Torrance_latin9.txt
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif (nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                          and text[nextpara][0][1] == '*' # if the next paragraph starts with a bullet point
                          and len(sent) <= 4
                          and counter_s == 0): # and this is a very short sentence, it is probably a heading. For H810_TMA01_Jelfs_final.
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif nextpara <= len(text)-1 and text[nextpara][0][1] == '*' and counter_s == 0:  # if the next paragraph starts with a bullet point, this is probably not a heading
                        temp = ['#dummy#'] + sent[1:]
                        mylist1.append(temp)
                    elif (re.search('^[0-9]+',firstword)
                          and len(sent0) <= 7
                          and counter_s == 0):  # If first word of sentence starts with a number and it contains less than n words
                        temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                        mylist1.append(temp)                        
                    elif (re.search('^[0-9]+',firstword) # First word starts with one or more numbers
                          and re.match('[0-9]$',lastword) # Last word IS a single digit (Note: shaky as essay may have more than 9 pages)
                          and counter_s == 0):  # 
                        temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                        mylist1.append(temp)
                    elif (re.search('^[0-9]+',firstword) # First word starts with one or more numbers
                          and len(sent) < 17 # Length of sentence is smaller than 16
                          and counter_s == 0):  # 
                        temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                        mylist1.append(temp)
                    elif re.search('^[0-9]+$',firstword) and len(sent) >= 17 and counter_s == 0: # If first word of sentence is numbers and sentence contains more than n words
                        secondword = sent[2]
                        if re.search('^[0-9]+$',secondword): # and if second word of sentence is also numbers [note: this should be done recursively to get all the numbers]                                                               
                            temp = ['#dummy#'] + sent[1:] # but don't change the label of the sentence from 'dummy', because this is probably not a heading
                            mylist1.append(temp)  
                        else:                                                        
                            temp = ['#dummy#'] + sent[1:] # but don't change the label of the sentence from 'dummy', because this is probably not a heading
                            mylist1.append(temp)  # This and the last elif were were necessary for one particular essay Report_-_assignment_1_T1282256_latin9. This author puts numbers at the beginning of most paragraphs.                    
                    # Next deal with all those so-far unmatched paragraphs that contain only one sentence 
                    elif len(para2) == 1: # If the paragraph contains only one sentence
                        temp2 = [item for item in sent if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', item)] # Get every item in the sent that doesn't contain punc marks
                        if re.match('[0-9]$',lastword) and len(sent) < 17: # If last word IS a single digit, and the sentence is shortish, it's probably in the contents page (Note: shaky as essay may have more than 9 pages, plus some short true sents end in a digit)
                            temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                            mylist1.append(temp)
                        elif len(temp2) <= 7 and sent[0] != '#-s:n#': #and sent[0] != '#-s:p#' # If the sentence has less than 7 words in it and is not a numeric sent. Note that this essay needs the number to be 7 or many headings are missed: Fleckhammer_B5843667_TMA01_H810_2012_latin9.txt
                            temp = ['#-s:h#'] + sent[1:] # label it as 'not a sentence' (replace dummy label) currently meaning probably a heading
                            mylist1.append(temp) 
                        else: # Otherwise pass the sentence on unchanged
                            mylist1.append(sent)
                    else:
                        mylist1.append(sent) # Otherwise pass the sentence on unchanged
                counter_s += 1                        
            else:
                break
        mylist2.append(mylist1)
    return mylist2

# Function: get_headings(text)
# Returns a list of all the sentences so far marked as headings.
# Each heading is accompanied by its index.
# Is called by main. The headings and their indices are used in different ways to find section indices.
def get_headings(text):
    counter_p = 0
    mylist2 = []
    while 1:
        if counter_p <= len(text)-1:
            mylist1 = []
            counter_s = 0
            while 2:
                if counter_s <= len(text[counter_p])-1:
                    sent = text[counter_p][counter_s]
                    x = len(sent) - 1 # ... get the length of the sentence
                    lastword = sent[x] # ... get the last word of the sentence                            
                    if sent[0] == '#-s:h#':
                        mylist1.append((sent, counter_p))
                        counter_s += 1
                    else:
                        counter_s += 1
                else:
                    break
            mylist2 = mylist2 + mylist1
            counter_p += 1
        else:
            break    
    result = [para for para in mylist2 if para != []]
    return result

# Function: match_sentence_2_heading
# Called by get_more_headings_using_contents
# Tests whether a sentence matches any of the headings. 
# Uses regular expression 'search' rather than 'match' in case of page numbers being present in heading.
def match_sentence_2_heading(sent, headings):
    #while 1:
    result = False
    for item in headings:
        if re.search(sent, item):
            result = True
    return result

                    
# Function: get_more_headings_using_contents
# Returns the essay with further headings marked as headings.
# This takes the list of headings found so far and goes through the essay
# to see if any sentences not marked as headings match any of the headings.
# This is done because entries in the contents page are typically picked
# up as headings because they end in a number (the page number), but the twin
# entry in the essay body may be missed if it is particularly long, as it doesn't
# end in a number. Note: It does not seem an obvious move to use the contents page
# earlier on in the process to get headings from the essay body, because so few
# essays contain a contents page. 
def get_more_headings_using_contents(text, headings):    
    section_name = "Introduction"
    mylist1 = headings
    temp = count_this_heading(section_name, headings, text)
    heading_count = len(temp)
    if heading_count == 0:
        return headings
    elif heading_count == 1:
        return headings
    elif heading_count == 2:
        x = temp[1][1] # So take second heading as heading for body intro section                                  
        y = find_last_section_para_index(section_name, x, text)    
        counter_p = 0
        while 2:            
            if counter_p <= len(text) - 1:
                counter_s = 0
                while 3:
                    if counter_s <= len(text[counter_p]) - 1:                    
                        sent = text[counter_p][counter_s]
                        if text[counter_p][counter_s][0] == '#dummy#':                    
                            sent1 = sent[1:] # Get everything in the sentence except the label                                    
                            headings2 = [item[0] for item in headings]
                            headings3 = [item[1:] for item in headings2]
                            headings4 = [' '.join(item) for item in headings3]
                            tempsent0 = ' '.join(sent1)
                            tempsent = re.sub('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', "", tempsent0) # Remove any punctuation otherwise the reg expr that you make will break
                            result = match_sentence_2_heading(tempsent, headings4)
                            if counter_p > x and result == True:
                                temp = ['#-s:h#'] + sent1 # Put a 'heading' label at the beginning (instead of 'dummy')
                                mylist1.append(temp)
                                counter_s += 1
                            else:
                                counter_s += 1
                        else:
                            counter_s += 1
                    else:
                        counter_p += 1                        
                        break
            else:
                break                 
        return mylist1
                

# Function: add_item_to_array
# Add single item 'item' as a new item in 'myarray',
# or as a detail of an existing item. Called by 'fill_sentence_array'.
# Called by 'fill_sentence_array' and 'make_graph_building_arrays' and 'update_array'.
def add_item_to_array(myarray, num, item):
    if myarray.has_key(num): # If num is one of the keys already in the array...
        myarray[num].append(item) # append 'item' (add 'item' as a detail to an already existing entry).
    else:
        myarray[num] = [item] # Otherwise add this item as new entry in the array.

# Function: add_to_sentence_array
# Add each original sentence as a detail to an entry in the 'myarray'
# initialised and filled earlier. This is done so that we can return the original
# sentence to the user in the results.
def add_to_sentence_array(myarray, text):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            add_item_to_array(myarray, counter, sent)  # Add the counter'th sentence to the array with counter as its key
            counter += 1        


# Function: fill_sentence_array
# Add each word-tokenised sentence as an entry in the empty 'myarray'
# initialised earlier. This is done partly so that each sentence has an index/key
# pointing to it, so that we can build a graph using numbers as nodes instead of
# actual sentences as nodes. The structure label of each sentence is also added
# to the array entry of that sentence.
def fill_sentence_array(myarray, text, struc_labels):
    counter = 0 # Sentence counter to add as key in array
    for para in text:
        for sent in para:
            if sent != [] and sent[0] != '#dummy#':
                place = struc_labels.index(sent[0]) # Get the label of the sentence
                label = struc_labels[place]
                temp = sent[1:] # Get everything in the sent after the label                                
                add_item_to_array(myarray, counter, temp) # Add the sent to the array
                add_item_to_array(myarray, counter, label) # add the label to the array at the same key
            elif sent != [] and sent[0] == '#dummy#': # I am keeping 'dummy' for the time being but may get rid of it. Everything is labelled 'dummy' in the first instance, but I could label everything '#+s#'.
                temp = sent[1:]                
                add_item_to_array(myarray, counter, temp)
                add_item_to_array(myarray, counter, '#+s#')                  
            counter += 1
                

# Function: make_graph_building_arrays
# Fill the empty array 'myWarray' with the unique words for each sentence
# and fill the other empty array 'myCarray' with their numbers of occurrences.
# There is one entry in 'myWarray' for each sentence. Each entry contains every
# unique word in that sentence. Similarly there is one entry in 'myCarray' for
# each sentence. Each entry is the number of occurrences of the word that occurs
# in that same position in 'myWarray'.
def make_graph_building_arrays(myarray, myWarray, myCarray):
    sentencecounter = 0
    while 1:
        if sentencecounter <= len(myarray)-1:
            tidysent = myarray[sentencecounter][0]
            if tidysent == []:
                add_item_to_array(myWarray, sentencecounter, '$$$$EMPTY_SENT_TOKEN$$$$')
                add_item_to_array(myCarray, sentencecounter, 0)
            else:
                wordcounter = 0
                monitorlist = []
                for w in tidysent:
                    if w not in monitorlist:
                        c = sum(1 for w in tidysent if w == tidysent[wordcounter])
                        add_item_to_array(myWarray, sentencecounter, w)
                        add_item_to_array(myCarray, sentencecounter, c)
                        monitorlist.append(w)
                        wordcounter += 1
                    else:
                        wordcounter += 1
            sentencecounter += 1
        elif sentencecounter > len(myarray)-1:
            break   
    
# Function: find_cosine_similarity
# Calculate the similarity of a pair of sentences using cosine similarity
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


# Function: add_one_nodes_edges
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
            elif weight == 0: # Count the number of zero-weight edges you are making (for monitoring)
                counterA += 1
            counter1 += 1
        elif counter1 == counter0: # If the 'from' and 'to' nodes are the same node, increment the 'from' node and carry on (don't join a node to itself).
            counter1 += 1
        else:
            return counterA # For this node (counter0), return the number of edges added with weight == 0. For monitoring.

# Function: add_all_node_edges
# Add all the weighted and directed edges to a graph that you have already initiated,
# and to which you have already added the appropriate nodes.
# Note that this involves finding which nodes should be joined by an edge, which in turn
# requires every pair of nodes/sentences in the graph to be compared in order to derive
# a similarity score. That part is carried by 'add_one_nodes_edges'.
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
    #if dev == 'DGF':
        #print '\nNumber of sentence pair comparisons with edge weight 0 (sentence pairs with no similarity): ',
        #print sumzeroweights
        #nf2.write(str(sumzeroweights))
        #nf2.write(': Number of sentence pair comparisons with edge weight 0 (sentence pairs with no similarity)\n')
    
# Function: find_global_weight_score
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

# Function: find_all_gw_scores
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
                #nf2.write('\nFinal iteration number:')                      
                #nf2.write(str(i+1))
                #nf2.write('\n')                    
            break # ... stop
    return scores_array

# Function: update_array
# Add the WSVi scores to the array created right at the beginning
# that contains the processed and the original sentences. For printing the results out.
def update_array(myarray,scores_array):
    temp = list(myarray)
    for Vi in temp:         
        WSVi = scores_array[Vi] # Get the score for Vi from the scores array
        add_item_to_array(myarray,Vi,WSVi) # And add it to 'myarray'  
            
# Function: reorganise_array
# Make a structure containing the results presented with the WSVi score
# first, then the array key, then the original sentence.
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

# Function: sort_ranked_sentences
# The array has now been turned into a list for results purposes.
# This function now removes from the list all items labelled as 'not a sentence': '#-s...#'
# Then sorts the remaining sentences into descending WSVi rank order. 
# Returns the list of true sentences in descending rank order.
def sort_ranked_sentences(mylist):
    temp = [item for item in mylist if item[2] == '#-s:p#' or item[2] == '#-s:n#' or item[2] == '#-s:h#' or item[2] == '#-s:t#']
    sorted_list = [item for item in mylist if item not in temp]
    sorted_list.sort() # ... and sort the structure according to its first argument (WSVi score)
    list.reverse(sorted_list)
    return sorted_list

# Function: analyse_intro_concl
# Makes some comparisons between the sentences that constitute the introduction, and the sentences sorted according to global weight.
# Does something similar for 'conclusion' sentences. 
# Returns the number of top-scoring sentences contained in 'this_section'.    
def analyse_intro_concl(sorted_list):
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
    #return (('intro',counter1),('concl',counter2))
    return {'intro':counter1,'concl':counter2}      #NVL: change structure


# Function: print_structure_feedback                
# Prints information concerning essay structure to two files.
def print_structure_feedback(text, structure_feedback, number_of_words, gr, nf, nf2):
    nf.write('\nTotal number of paragraphs (includes headings, tables,... but not refs): ') #...and print the results to the summary results file.
    nf.write(str(len(text)))

    nf.write('\nTotal number of sentences (includes headings, tables,... but not refs): ')         
    nf.write(str(len(gr.nodes())))            

    nf.write('\nTotal number of words (includes headings, tables,... but not refs): ') #...and print the results to the summary results file.
    nf.write(str(number_of_words))

    number_of_edges = len(gr.edges())
    nf.write('\nTotal number of edges in the graph: ')         
    nf.write(str(number_of_edges))

    nf2.write('\nNumber of INTRO and CONCL sentences which are in 30 most important sentences:\n')
    nf2.write(str(structure_feedback))
    nf2.write('\n\n')


# Function: print_scores_info         
# Writes global weight results to two files.
def print_scores_info(ranked_global_weights, nf, nf2):
    mylist2 = []
    for item in ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        key = item[1]
        mylist2.append(key)
    nf.write('\n\nRanked sentence order: (currently includes title (if the essay gives one) but not empty sentences (following processing) or headings, captions, ...)\n') 
    nf.write(str(mylist2)) # ...and write them to the results file so you can see the order at a glance.

    # Write detailed results to the essay results file.		
    s = str(ranked_global_weights) # Map the results into a string so you can write the string to the output file
    w = re.sub('\]\),', ']),\n', s) # Add a new line at the end of every result so that each result is written to a separate line
    y = re.sub('\"\),', '\'),\n', w) # Be careful, because Python sometimes uses double quotes instead of single ones          
    nf.write('\n\nDetailed sentence ranking results : \n')
    nf.write(y)
    ########
    # WRITE SELECTED INFO TO SUMMARY FILE NF2
    ########
##    nf2.write('\n\nRanked sentence order:\n') 
##    nf2.write(str(mylist2)) # ...and write them to the summary file as well.
##    
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
            

# Function: print_section_sents
# Prints the sentences of each section, grouped by section.
def print_section_sents(mylist, section_names, section_labels, nf):
    temp = zip(section_names, section_labels)
    for pair in temp: # For each member of the list of (section_name, section_label) pairs
        print '\n\nSentences from section: ', pair[0]
        nf.write('\n\nSentences from section: ')
        nf.write(str(pair[0]))
        nf.write('\n')
        for item in mylist: # For each member of the list/array (each sentence)
            if item[2] == pair[1]: # if the label of the sentence is the same as the label in the pair
                print item # print it
                nf.write(str(item)) # and write it to file
                nf.write('\n')

# Function: print_processing_times
# Takes different recorded times, does some arithmetic, and prints/writes process times.
# For monitoring and improving program efficiency.
# Commented out at the moment because I don't want to focus on timings for now.
def print_processing_times(startprogtime, endimporttime, startfiletime, texttime, graphtime, scorestime, nf2):
    textproctime = texttime - startfiletime # Work out how long different parts of the program took to run...
    graphproctime = graphtime - texttime
    scoresproctime = scorestime - graphtime
    totalproctime = scorestime - startfiletime
    importproctime = endimporttime - startprogtime # Get some more processing timings   
    nf2.write('\nText processing time: ')
    nf2.write(str(textproctime))
    nf2.write('\nGraph processing time: ')
    nf2.write(str(graphproctime))
    nf2.write('\nScores processing time: ')
    nf2.write(str(scoresproctime))
    nf2.write('\nTotal essay processing time: ')
    nf2.write(str(totalproctime))
    nf2.write('\n\n*********************************************************\n\n')
    #nf2.write('\n\n')
    nf2.write('\nCompilation and import processing time: ')
    nf2.write(str(importproctime))
    stopprogtime = time()
    nf2.write('\nProgram stopped running at: ')
    nf2.write(str(stopprogtime))
    totalprogtime = stopprogtime - startprogtime
    nf2.write('\nTotal program processing time: ')
    nf2.write(str(totalprogtime))

# Function: pre_process_essay
# Carries out all text processing that is necessary before the graph can be constructed from the essay's sentences.
# Also labels each sentence with its structural function.
# Returns: text (fully processed text), parasenttok (text before word tokenisation, for Nicolas), number_of_words (calculated before stop words removed), section_names, section_labels.
def pre_process_essay(text0,struc_feedback,nf,nf2,dev):
#def pre_process_essay(text0,struc_feedback,nf,nf2,dev,model):    
    # Get the body of the essay. 
    # Currently this is everything occurring before the references section but it needs improvement/refinment.
    text1, refs_present = get_essay_body(text0,nf,dev)     

    # Put refs comment into Nicolas' essay results
    struc_feedback['comment refs present'] = refs_present

    # Split the essay body on whitespace so that you can correct the latin9 encoding before sentence splitting. 
    # Latin9 encoding puts questions marks everywhere, which confuses the sentence splitter. I reverse this split before sentence tokenisation. 
    text2 = re.split(r' ', text1)

    # Convert latin9-encoded text back into something very similar to the original text.		
    # Latin9 encoding substitutes a question mark for MS Word curly speech marks and curly apostrophes and en-dashes and em-dashes. Function 'tidy_up_latin9' replaces em- and en-dashes with hyphens and puts back apostrophes and speech marks.
    temp1 = tidy_up_latin9(text2)    

    # Following latin9 tidy-up, un-split the body of the essay ready for sentence splitting.
    temp2 = ' '.join(temp1) 

    # Paragraph-tokenise the result.
    # This results in having quotation marks as paragraph delimiters.
    paratok = LineTokenizer().tokenize(temp2)
    len_paratok = len(paratok)
    
    # Sentence-tokenise the result.
    # This results in having quotation marks as sentence delimiters, and preserves the paragraph delimiters by using square brackets.
    parasenttok = [PunktSentenceTokenizer().tokenize(item) for item in paratok]        

    #parasenttok = sentence_tokenize(model,paratok) # This calls a sentence splitter that uses a model. The model takes a few seconds to load.
    
    # Word-tokenise the result.           
    text3 = word_tokenize(parasenttok)

    # Remove all word-tokens that contain punctuation marks or series of punctuation marks. 
    # This is done because we are not interested in the frequency or usage of punctuation apart from to divide text up into sentences, which has been done by now. 
    text4 = process_sents(remove_punc_fm_sents, text3)

    # Words are counted before stop words removed.    
    number_of_words = count_words(text4)
       
    # For each sentence that contains only words which contain numbers, label the sentence as a numeric sentence.
    # Numeric sentences can be module names, entries in tables, list enumerators, etc.
    # Numeric sentences are not returned to the user as important sentences, but they are included in the derivation of the scores.
    # I do not remove them at the beginning, because I do not yet know how interesting/significant numeric sentences are.
    text5 = process_sents(find_and_label_numeric_sents, text4)

    # Find and label as 'heading' all the paragraphs that are probably headings.
    # Currently the sentence scores are worked out with the headings included in the sums, but the headings are not included in the final ranked list returned to the user. 
    # This is because the content of the headings is important, but the headings themselves cannot be key sentences.
    # Happens before lowercasing in case we use letter case as a clue.
    # Happens before removing stop words because some sentences become very short if you remove all the stop words from them, and so can get mistaken for headings.
    text50 = find_and_label_headings(text5)

    # Derive from the text all the headings you have found, each with its index.
    someheadings = get_headings(text50)

    # Use the headings you have found so far to see if there are any headings you have missed. This tends to only derive additional headings if there is a 'contents' page.
    headings = get_more_headings_using_contents(text50, someheadings)

    # Set variables 'section_names' and 'section_labels'. Orders match.
    section_names = ['Headings', 'Numerics', 'Punctuation',  'Title', 'Summary', 'Preface', 'Introduction',  'Conclusion']
    section_labels = ['#-s:h#', '#-s:n#', '#-s:p#', '#-s:t#', '#+s:s#', '#+s:p#', '#+s:i#', '#+s:c#']
    
    # Find the indices of the first and last paragraphs of the conclusion section.
    ((first, last),title_indices) = find_section_paras(text50, 'Conclusion', headings, nf, dev)
    # Label the conclusion sentences using the indices you have just found.
    text50a = label_section_sents(text50, 'Conclusion', section_names, section_labels, first, last)        

    # Find the indices of the first and last paragraphs of the summary section (if there is one).
    ((first, last),(title_first1,title_last1)) = find_section_paras(text50, 'Summary', headings, nf, dev)
    # Label the summary sentences using the indices you have just found.    
    text51 = label_section_sents(text50a, 'Summary', section_names, section_labels, first, last)

    # Find the indices of the first and last paragraphs of the preface section (if there is one).    
    ((first, last),(title_first2,title_last2)) = find_section_paras(text50, 'Preface', headings, nf, dev)
    # Label the preface sentences using the indices you have just found.
    text52 = label_section_sents(text51, 'Preface', section_names, section_labels, first, last)
       
    # Find the indices of the first and last paragraphs of the introduction section.
    ((first, last),(title_first3,title_last3)) = find_section_paras(text50,'Introduction', headings, nf, dev)
    # Label the introduction sentences using the indices you have just found.
    text53 = label_section_sents(text52, 'Introduction', section_names, section_labels, first, last)
    
    # The title will typically appear before the summary if there is one, and before the preface if there is one.
    # But introductions typically follow summaries and prefaces. So we need to look for a title in each case
    # and choose the first one that succeeds.
    if title_first1 != []:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first1, title_last1)
    elif title_first2 != []:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first2, title_last2)
    else:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first3, title_last3)

    # Put all word-tokens into lower case. 
    # This is done so that the same word token represented in different cases will be counted as the same word. Note that this is done after sentence splitting in case capitalisation of sentence-initial words is used by sentence splitter.
    text7 = process_sents(lowercase_sents, text77)

    # Remove all word-tokens that are stop words. 
    # This is done because we are not interested in the frequency or usage of stop words, and because stop words are typically the most frequent words in prose. E.g., we don't want sentence N being returned as the most representative sentence in the text based on how the word 'the' is used.        
    text = process_sents(remove_stops_fm_sents, text7)
    
    return text,parasenttok,number_of_words,section_names,section_labels

# Function: process_essay
# Carries out all procedures relating to drawing of graph and analysing edges and weights and calculating global weight scores of nodes.
def process_essay(text, parasenttok, nf, nf2, dev):
    # Initialise an empty associative array (Python dict) that will hold the sentence- and word- tokenised sentences, each associated with an index key. 
    # This is done partly so that we can build a graph using numbers as nodes instead of actual sentences as nodes.
    myarray = {}  

    # Initialise structure labels
    struc_labels = ['#-s:h#', '#-s:n#', '#-s:p#', '#-s:t#', '#+s:i#', '#+s:c#', '#+s:s#', '#+s:p#']        

    # Fill array 'myarray' with the fully processed version of the text, one sentence per entry in the array.
    # Each sentence is thus associated with an array key number which represents its position in the text.
    fill_sentence_array(myarray, text, struc_labels)

    # Add each original unprocessed sentence to 'myarray' at the appropriate key point, so they can be returned in the user feedback later.
    # 'Unprocessed' means following latin9 cleanup, after sentence tokenisation, but before word tokenisation and all the other pre-processing
    add_to_sentence_array(myarray, parasenttok) 
    
    # Now we start to build the graph in which the index key to each sentence (from 'myarray') is a node representing that sentence. 
    # We build a graph so that we can work out how strongly connected each sentence is to every other sentence in the graph/text on the basis of similarity of pairs of sentences.

    # Initiate an empty directed graph 'gr'.
    # A graph of class 'directed graph' meaning edges are directed, i.e., an edge points like an arrow from one node to another node. This class and 'nx' are from the package 'networkx' which needs to be imported at the start.
    # We use a directed graph encoded in a backwards direction (a node can only point to an earlier node) following some discussion on the penultimate page of (Mihalcea and Tarau, 2005). 
    gr=nx.DiGraph() 

    # Add the appropriate nodes to the empty graph.	
    # 'list(myarray)' lists only the keys from 'myarray', so this adds the keys from 'myarray' as nodes to the graph 'gr' that we have already defined and filled with the essay's sentences, one per key/node.
    gr.add_nodes_from(list(myarray)) 
                
    # Initialise some empty arrays.
    myWarray = {} 
    myCarray = {}

    # Fill one array with the unique words in each sentence (i.e., remove repetitions) and fill the other array with their numbers of occurrences. There is one entry in each array for each sentence.            
    # This is done to speed up the graph-building process. In an essay with 280 sentences, every sentence is compared to every sentence that precedes it, that's about 39,200 comparisons. The arrays are used as look-up tables by the cosine similarity function that measures the similarity of a pair of sentences.
    make_graph_building_arrays(myarray, myWarray, myCarray)
    # Add all the appropriate weighted and directed edges to the graph that you have already initiated, and to which you have added the appropriate nodes. This requires comparison of pairs of sentences/nodes in order to calculate the weight of the edge that joins them.
    add_all_node_edges(gr,myWarray,myCarray,nf2,dev)
    
    possible_number_of_edges = ((len(myarray))**2)/2
    graphtime = time() # Set current time to a variable for later calculations

    # Initialise an array with WSVi score set to 1/graph_size (no. nodes) for all nodes.
    # The decision to use this number to seed scores_array is copied directly from pagerank.py. Beware the problem of massive numbers coming up in WSVi scores if initial scores are too high.
    scores_array = dict.fromkeys(gr.nodes(),1.0/len(gr.nodes()))
    
    # And finally we get to calculate the WSVi global weight score for each node in the graph using parameters set above.
    # This function relies on all the processing done so far (the building of a directed graph with weighted edges using an essay as input).    
    find_all_gw_scores(gr, scores_array, nf2, dev)        
    # Add the WSVi scores to the array created earlier that contains the original text before word-tokenisation. For printing the results out.       
    update_array(myarray,scores_array)
    #print '\nThis is myarray after updating with scores: ', myarray

    reorganised_array = reorganise_array(myarray)
    
    # Make a structure containing the results, putting the WSVi rank first, 
    ranked_global_weights = sort_ranked_sentences(reorganised_array)

    return gr, myarray, ranked_global_weights, reorganised_array, graphtime                      

# Function: debora_results
# Prints and writes to file various results I want to see.
def debora_results(gr,text,ranked_global_weights,reorganised_array,number_of_words,section_names,section_labels,nf,nf2):
    structure_feedback = analyse_intro_concl(ranked_global_weights)
    print_structure_feedback(text, structure_feedback,number_of_words,gr, nf, nf2)
    print_section_sents(reorganised_array, section_names, section_labels, nf)
    print_scores_info(ranked_global_weights, nf, nf2)

# Function: nicolas_results
# Prints and writes to file various results Nicolas wants.    
def nicolas_results(gr,ranked_global_weights,parasenttok, number_of_words, struc_feedback):
    # NVL : get the different pieces into the JSON data structure
    essay = {}
    essay['essayID'] = str(uuid4())     # NVL : generate a random UUID for the essay (converted to string)
    essay['parasenttok'] = parasenttok

    stats = {}
    stats['paragraphs'] = len(parasenttok)
    #stats['words'] = str(count_words(text))
    stats['words'] = number_of_words # DGF: The words have to be counted before the stop words are removed.

    stats['sentences'] =  sum(w for w in [len(x) for x in parasenttok])
    stats['nodes'] = len(gr.nodes())

    stats['edges'] = len(gr.edges())
    essay['stats'] = stats
    
    struc_feedback['comment intro concl'] = analyse_intro_concl(ranked_global_weights)
    essay['struc_feedback'] = struc_feedback    
    #essay['gr'] = gr
    #hh = 1/0    
    mylist2 = []
    top_ranked_global_weights = ranked_global_weights[:15]    
    for (a,b,c,d,e) in top_ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
        mylist2.append((a,b,c))        
    essay['ranked'] = mylist2    
    #nx.write_weighted_edgelist(gr,'fdfdfd.txt');
    

    #mylist3 = []
    #top_ranked_global_weights = ranked_global_weights   
    #for (a,b,c,d,e) in top_ranked_global_weights: # Get only the sentence key numbers from the sorted scores list...
    #    mylist3.append((b,c))  
    #mylist3.sort(key=itemgetter(0))      
    #essay['struct'] = mylist3    
    
    return essay, essay['essayID']
    # NVL : return the JSON object
    #return render_template('essay.html', essay=essay)    
    

        
# Copyright (c) 2012 Debora Georgia Field <deboraf7@aol.com>
