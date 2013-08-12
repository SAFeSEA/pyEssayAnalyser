import re # For regular expressions
#from nltk.corpus import stopwords # For removing uninteresting words from the text
from se_stops import essay_stop_words
""""
This file contains all the functions concerning analysing the
structure of the essay. The functions are mostly called by the
function pre_process_struc in file se_procedure.py.
Functions names:
def label_section_sents(text, section_name, section_names, section_labels, section_index_first, section_index_last):
def count_this_heading(section_name, headings, text):
def find_last_section_para_index(section_name, heading_index_first, text):
def find_first_section_para_index(section_name, first_heading, text):
def find_first_intro_para_index(section_name, first_heading, text, headings):
def find_no_intro_heading_indices(text, headings):
def find_first_concl_para_index(text,result_last,headings,nf,nf2,dev):
def find_no_concl_heading_indices(section_name, headings, text,nf,nf2, dev):
def find_title_indices(index, text): # 'index' is the first paragraph of the introduction
def find_section_paras(text, section_name, headings, nf,nf2,dev):
def pre_process_sent(sent):
def get_headings(text)
def match_sentence_2_heading(sent, headings)
def get_more_headings_using_contents(text, headings)
def table_entries_recheck1(text)
def table_entries_recheck2(text)
def find_and_label_headings(text,ass_q_long_words):
def find_and_label_heading(text,sent, proc_sent, sent1, counter_s, para, para2, previouspara, nextpara, ass_q_long_words):
"""


# Function: label_section_sents(text, section_name, section_names, section_labels, section_index_first, section_index_last)
# Called by find_and_label_section_sents in this file after the indices for the section being called have been calculated by find_section_paras
# Returns the full essay text having labelled each introduction (summary, conclusion...) sentence with its structural ID
# Does this by labelling every paragraph between and including the first section_name para and the last section_name para
# as already found.
def label_section_sents(text, section_name, section_names, section_labels, section_index_first, section_index_last):
    x = section_names.index(section_name) # Get the position of this section name in the section_names list
    label = section_labels[x] # so you can find its label in the section_labels list
    if section_name == 'Summary' and section_index_first == [] and section_index_last == []:
        result = text # If there is no 'Summary' heading, assume there is no summary       
    else:
        mylist2 = []
        counter = 0
        while 1:
            if counter <= len(text)-1:
                mylist1 = []
                for sent in text[counter]: # For cases where no heading has been found, both indices are the same, a single paragraph to be labelled
                    if sent[0] == '#dummy#' and section_index_first == section_index_last and counter == section_index_last: 
                        temp = [label] + sent[1:]
                        mylist1.append(temp)
                    elif sent[0] == '#dummy#' and section_index_last != [] and counter >= section_index_first and counter <= section_index_last and len(sent) > 1:                    
                        temp = [label] + sent[1:]
                        mylist1.append(temp)
                    elif section_name == 'Title' and section_index_first == section_index_last and counter == section_index_last: # added for Seale 2006 textbook, also see addition to find_title_indices
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

# Function: count_this_heading(section_name, headings, text)
# Go through every heading and see if contains the case-insensitive version of section_name.
# Return a list containing the found headings and their indices.
# Called by find_no_concl_heading_indices and other functions in this file.
def count_this_heading(section_name, headings, text):
    mylist = []
    p = re.compile(section_name, re.IGNORECASE)
    for item in headings:
        heading2 = item[0] #  (['#-s:h#', u'Seale', u'Chapter', u'1'], 0)
        temp = ' '.join(heading2)
        if (re.search(p, temp)
            and item[0][0] == '#-s:s#'): # New condition because I only want section  headings to qualify here because section headings have extra constraints on them compared to general headings labelled as '#-s:H#'
            mylist.append(item)
#    else:
#        mylist = mylist
    return mylist

# Function: find_last_section_para_index(section_name, heading_index_first, text)
# Called by several functions in this file.
# Returns the position of the last section_name paragraph in the essay.
# Does this by finding the heading that follows the heading 'section_name' (already found).
# The para that precedes that next heading is assumed to be the last para of the section.
# Assumes that the sections (Intro, Concl, Summary, Preface) don't have headings inside them, which is not true in every case.
# Function: find_last_section_para_index(section_name, heading_index_first, text)
# Called by several functions in this file.
# Returns the position of the last section_name paragraph in the essay.
# Does this by finding the heading that follows the heading 'section_name' (already found).
# The para that precedes that next heading is assumed to be the last para of the section.
# Assumes that the sections (Intro, Concl, Summary, Preface) don't have headings inside them, which is not true in every case.
def find_last_section_para_index(section_name, heading_index_first, text):
    counter_p = heading_index_first + 1 # Get the paragraph following the para that is the heading
    position1 = heading_index_first + 1 # position1 is used to ensure we only get the first eligible paragraph returned as the result.
    section_index_last = []
    while 1:         
        if counter_p <= len(text)-1:
            counter_s = 0
            while 2:
                if counter_s <= len(text[counter_p]) - 1:
                    if ((text[counter_p][counter_s][0] == '#-s:h#'
                        or text[counter_p][counter_s][0] == '#-s:H#'
                        or text[counter_p][counter_s][0] == '#-s:l#' # a letter heading
                        or text[counter_p][counter_s][0] == '#-s:d#' # a digital heading
                        or text[counter_p][counter_s][0] == '#-s:s#') # a section heading
                        and counter_p == position1): # See if this paragraph is a heading
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
        result = heading_index_first
    return result


# Function: find_first_section_para_index(section_name, first_heading, text)
# Called by find_section_paras when a section_name heading has been found.
# Returns the position of the first and last paras of section_name 
def find_first_section_para_index(section_name, first_heading, text):
    first = []
    last = []
    counter1 = first_heading
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            # See if this paragraph has label 'dummy'
            if text[counter1][0][0] == '#-s:n#' and len(text[counter1]) > 1: # If the first sentence of the paragraph is a numeric sentence, skip to the second sentence of the paragraph. B5927135-H810-11I_02-1-U.
                sent = text[counter1][1] 
            else: # otherwise stick with this paragraph.
                sent = text[counter1][0]                        
            if (sent[0] == '#dummy#'):
                    first = counter1
                    last = find_last_section_para_index(section_name, first, text)
                    break                                       
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1                                           
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)

# Function: find_first_intro_para_index(section_name, first_heading, text, headings)
# Called by find_section_paras when an Introduction heading has been found.
# Returns the position of the first and last paras of the introduction.    
def find_first_intro_para_index(section_name, first_heading, text, headings):
    all_heading_indices = [item[1] for item in headings]
    counter1 = first_heading
    first = [] # edge case condition
    last = [] # edge case condition
    countTextChars = 0
    for para in text:
        for sent in para:
            temp = ' '.join(sent[1:])
            countTextChars += len(temp)                            
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            if text[counter1][0][0] == '#-s:n#' and len(text[counter1]) > 1: # If the first sentence of the paragraph is a numeric sentence, skip to the second sentence of the paragraph. B5927135-H810-11I_02-1-U.
                sent = text[counter1][1] 
            else: # otherwise stick with this paragraph.
                sent = text[counter1][0]            
            if (sent[0] == '#dummy#'): # See if this paragraph has label 'dummy'
                    first = counter1
                    last = find_last_section_para_index(section_name, first, text) # then look for a heading to mark the end of the intro                    
                    y = last+1
                    countPassageChars = 0
                    for para in text[first:y]: # Find the char length of the introduction section as you have identified it
                        for sent in para:
                            temp = ' '.join(sent[1:])
                            countPassageChars += len(temp)
                    if countPassageChars > countTextChars/3: # If the introduction you have identified is bigger than a third of the whole text, you've probably got the last paragraph index wrong, so revert to making the intro a single paragraph long.
                        last = first # #This stops whole essays being marked up as introduction then conclusion in essays that don't have headings.
                    else: 
                        last = last                         
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1                                     
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)
    
# Function: find_no_intro_heading_indices(text, headings)
# Called by find_section_paras when no Introduction heading has been found.
# Returns the indices of the first and last paragraphs of the Introduction section.
# Assumes that the intro is the first para that has not been labelled a heading
# and that is either a multi-sentence para, or has a single long sentence in it.
# Calls find_last_section_para_index under certain conditions.
def find_no_intro_heading_indices(text, headings):
    counter1 = 0
    first = []
    last = []
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            countPassageChars = 0
            for sent in text[counter1]:
                temp = ' '.join(sent[1:])
                countPassageChars += len(temp)            
            if text[counter1][0][0] == '#-s:n#' and len(text[counter1]) > 1: # If the first sentence of the paragraph is a numeric sentence, skip to the second sentence of the paragraph. B5927135-H810-11I_02-1-U.
                sent = text[counter1][1] 
            else: # otherwise stick with this paragraph.
                sent = text[counter1][0]
            if (sent[0] == '#dummy#'  # See if this sentence has label 'dummy'
                and countPassageChars > 100): # and the paragraph contains more than 100 characters
                    first = counter1 # Set this paragraph as the first paragraph of the introduction
                    last = find_last_section_para_index('Introduction', first, text) # Look for a heading to mark the # end of the Introduction.
                    countTextChars = 0
                    countIntroChars = 0
                    y = last+1
                    for para in text:
                        for sent in para:
                            temp = ' '.join(sent[1:])
                            countTextChars += len(temp)                        
                    for para in text[first:y]:
                        for sent in para:
                            temp = ' '.join(sent[1:])
                            countIntroChars += len(temp)
                    #print '\n#### find_no_intro_heading_indices countTextChars', countTextChars
                    #print '\n#### find_no_intro_heading_indices countIntroChars', countIntroChars
                    if countIntroChars > countTextChars/3:
                        last = first                    
                        print '###### INTRO SET TO A SINGLE PARA#####'
                        #print '\n\n\nfirst, last', first, last, text[first]
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1
        else:
            break # Stop looping when you've dealt with the last paragraph. 
    return (first,last)

# Function: find_first_concl_para_index(text,result_last,headings,nf,nf2,dev)
# Called with arguments 'text' and the last paragraph of the essay that is not a heading ('result_last').
# Returns the index of the first paragraph of the conclusion.
# xxxx Note that to find the conclusion in some cases, you need to find the introduction.
# This means that in these cases, the introduction is found twice, because the intro arguments are not carried forwards.
# This is bad programming and needs fixing. Note that it is only in some cases that the introduction is actually used.
# Called by find_no_concl_heading_indices.
def find_first_concl_para_index(text,result_last,headings,nf,nf2,dev):
    ((intro_first, intro_last), title_indices, headingQ) = find_section_paras(text, 'Introduction', headings, nf,nf2,dev)
    all_heading_indices = [item[1] for item in headings]
    temp2 = [item for item in all_heading_indices if item < result_last and item > intro_last] # Get all the heading indices that are earlier than the last concl paragraph and later than the last intro paragraph.
    counter1 = result_last
    first_concl_para_index = []
    p = re.compile('this report', re.IGNORECASE)
    q = re.compile('conclusion', re.IGNORECASE)
    r = re.compile('conclud', re.IGNORECASE)
    while 1:
        if counter1 >= 0:
            temp = ' '.join(text[counter1][0])
            if re.search(p, temp): # If the first sentence of this paragraph contains the phrase 'this report', it's prob the first para of the conclusion. Put in for 2012 C1264876 H810 TMA01
                first_concl_para_index = counter1
                break
            elif re.search(q, temp): # If the first sentence of this paragraph contains the phrase 'conclusion', it's prob the first para of the conclusion. Put in for 2012 C1264876 H810 TMA01
                first_concl_para_index = counter1
                break
            elif re.search(r, temp): # If the first sentence of this paragraph contains the phrase 'conclud', it's prob the first para of the conclusion. Put in for 2012 C1264876 H810 TMA01
                first_concl_para_index = counter1
                break            
            elif temp2 == []: # If there are no headings between intro and concl, assume no headings in essay, and set concl to one paragraph.
                first_concl_para_index = counter1                
                break
            # Otherwise find the heading that precedes 'result_last', increment counter1 by 1, and return value.                            
            elif (text[counter1][0][0] == '#-s:h#' # special
                  or text[counter1][0][0] == '#-s:H#' # general
                  or text[counter1][0][0] == '#-s:s#' # section
                  or text[counter1][0][0] == '#-s:d#' # digital
                  or text[counter1][0][0] == '#-s:l#' # letter
                  or text[counter1][0][0] == '#-s:q#'): # Note that some essays use the assignment question sentences as headings, so this needs accounting for here with the '#-s:q#' 
                first_concl_para_index = counter1 + 1  # But note that some essays use the assignment question sentences as headings, so this needs accounting for here with the '#-s:q#'
                break
            else:
                counter1 -= 1
        else:
            break
    return first_concl_para_index

# Function: find_no_concl_heading_indices(section_name, headings, text,nf,nf2, dev)
# Returns the indices of the first and last paragraph of the conclusion.
# Works out which is the last paragraph, then uses that to find the first.
# Calls find_first_concl_para_index.
# Is called by find_section_paras only if no 'Conclusion' heading has been found.
def find_no_concl_heading_indices(section_name, headings, text,nf,nf2, dev):
    list_this_heading = count_this_heading('word count', headings, text)
    list_this_heading.reverse() # Reverse the order of headings with word count in them in case there is more than one, because you want the one at the end of the essay.
    heading_count = len(list_this_heading)
    word_count_index = len(text)
    # Set word_count_index to the index of the last para. If there is no heading for word count in the essay, this will ensure that the main clause doesn't fail.
    if heading_count > 0 and list_this_heading[0][1] > (len(text)/2): # If there is a word count heading, and it occurs in the second half of the essay, then re-set word count heading to the new value
        word_count_index = list_this_heading[0][1]
    counter1 = len(text) - 1
    first = []
    last = []
    while 1: # Cycle through every sentence of the text backwards from the end 
        if counter1 >= 0:
            if text[counter1][0][0] == '#-s:n#' and len(text[counter1]) > 1: # If the first sentence of the paragraph is a numeric sentence, skip to the second sentence of the paragraph. B4423906-H810-10I_02-1-U.txt
                sent = text[counter1][1] 
            else: # otherwise stick with this paragraph.
                sent = text[counter1][0]
            if (sent[0] == '#dummy#'  # See if this sentence has label 'dummy'            
                and (len(text[counter1]) > 1 or len(sent) > 14) # ...and the paragraph contains more than one sentence, or it's a long sentence
                and (counter1 < word_count_index)):  
                    last = counter1 # then set this paragraph to the last para of the concl
                    print '\n\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^THIS IS LAST PARA OF CONCL: ', last, text[last]
                    first = find_first_concl_para_index(text,last,headings,nf,nf2,dev) # and find the first para
                    print '\n\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^THIS IS FIRST PARA OF CONCL: ', first,text[first]
                    print '\n\n\n'

                    countTextChars = 0
                    countConclChars = 0
                    y = last+1
                    for para in text:
                        for sent in para:
                            temp = ' '.join(sent[1:])
                            countTextChars += len(temp)                        
                    for para in text[first:y]:
                        for sent in para:
                            temp = ' '.join(sent[1:])
                            countConclChars += len(temp)
                    if countConclChars > countTextChars/3: # If the concl you have found is longer than a third of the body of the essay
                        first = last                    
                        print '###### CONCL SET TO A SINGLE PARA#####'
                        print '\n\n\nfirst, last', first, last, text[first]                    
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 -= 1
        else:
            break # Stop looping when you've dealt with the first paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)        

# Function: find_title_indices(index, text)
# Returns the index of the title.
# Called by find_section_paras.
# Currently configured to allow only one paragraph to be returned (first title para and last title para are the same).
# xxxx @improve this to exclude the module title, e.g., 'H810 Accessible online learning: supporting disabled students'
# Requires pickling of title, loading at the beginning, etc.
def find_title_indices(index, text): # 'index' is the first paragraph of the introduction
    counter1 = 0
    first = []
    p = re.compile('title', re.IGNORECASE)
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            previousparaindex = counter1-1
            temp = ' '.join(text[counter1][0])
            if previousparaindex <= len(text)-1:
                #print '\n\n\nThis find_title_indices 1 with text[previousparaindex]:', text[previousparaindex], previousparaindex
                temp2 = ' '.join(text[previousparaindex][0])
            if (previousparaindex <= len(text)-1 # This clause added for Seale textbook, see also addition to label_section_sents
                and counter1 < index # If this paragraph is earlier than the introduction
                and re.search(p, temp2)): # and the first sentence of the previous para contains 'title'
                    first = counter1 # then this para is the title
                    #print '\n\n\nThis find_title_indices 1 with title:', text[counter1]
                    break                
            #if (text[counter1][0][0] == '#dummy#' # If this hasn't been spotted as a heading
            if (counter1 < index # and this para is earlier than the intro
                and re.search(p, temp)): # and this para contains 'title'
                    #print '\n\n\nThis find_title_indices 2 with title:', text[counter1]
                    first = counter1 # then this para is the title
                    break
            #elif (text[counter1][0][0] == '#dummy#' # If this para hasn't been spotted as a heading
            elif (len(text[counter1][0][0]) > 5 # and the length of this sentence is between 5 and 28
                and len(text[counter1][0][0]) < 28 # and this para is earlier than the intro
                and counter1 < index):# and position3 == counter1):
                    #print '\n\n\nThis find_title_indices 3 with title:', text[counter1]
                    first = counter1 # then this para is the title
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,first)

# Function: find_section_paras(text, section_name, headings, nf,nf2,dev)
# Called by find_and_label_section_sents in this file.
# First counts the number of headings for that section type, then uses the result to decide how to determine which are the section paragraphs.
# Calls different functions depending on section name and number of headings found.
# Uses information found about certain sections to find the index of the title.
def find_section_paras(text, section_name, headings, nf,nf2,dev):
    #print '\n\n\Looking for heading for section_name:', section_name
    #print 'headings:', headings    
    list_this_heading = count_this_heading(section_name, headings, text)
    if list_this_heading != [] and dev == 'DGF':
        print 'All headings like this:', list_this_heading
    if section_name == 'Preface': # Once you have counted the heading occurrences, treat prefaces exactly the same as summaries
        section_name = 'Summary'
    heading_count = len(list_this_heading) # heading_count is the number of 'section_name' headings found. Typically 2, 1, or 0. If 2, the first is probably in a contents section.
    first = []
    last = []
    title_indices = ([],[])
    headingQ = []
    if heading_count == 0 and section_name == 'Summary':
        if dev == 'DGF':
            print 'No "Summary" heading has been found'
        headingQ = False
        True # Don't do anything, para indices remain empty. Not assuming that there is unlabelled Summary section, as we do with Introduction and Conclusion.        
    elif heading_count == 0 and section_name == 'Introduction': # If no 'Introduction' section heading has been found
        (first,last) = find_no_intro_heading_indices(text, headings)
        title_indices = find_title_indices(first, text)
        if dev == 'DGF':
            print 'No "Introduction" heading has been found'
        headingQ = False
    elif heading_count == 0 and section_name == 'Conclusion': # If no 'Conclusion' section heading has been found
        (first,last) = find_no_concl_heading_indices(section_name, headings, text,nf,nf2,dev)
        if dev == 'DGF':
            print 'No "Conclusion" heading has been found'
        headingQ = False
    elif heading_count >= 2 and section_name == 'Introduction': # If there are at least two occurrences of 'Introduction' heading, first is prob contents page, and second prob body section
        first_heading = list_this_heading[1][1] # So take second occurrence as heading of body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        contents_heading_index = list_this_heading[0][1]
        title_indices = find_title_indices(contents_heading_index, text)
        if dev == 'DGF':
            print '1 An "Introduction" heading has been found (1)', list_this_heading[1][0]
        headingQ = True
    elif heading_count >= 2 and section_name == 'Conclusion': # If there are at least two occurrences of 'Conclusion' heading, first is prob contents page, and second prob body section
        first_heading = list_this_heading[1][1] # So take second occurrence as heading of body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            print '2 A "Conclusion" heading has been found', first, last, list_this_heading[1][0]
        headingQ = True
    elif section_name == 'Introduction': # In all other Introduction cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_intro_para_index(section_name, first_heading, text, headings)
        title_indices = find_title_indices(first, text)
        if dev == 'DGF':
            headingQ = True
        print '3 A heading has been found for section name:', section_name, first, last, list_this_heading[0][0]             
    elif section_name == 'Conclusion': # In all other 'conclusion' cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            print '4 A heading has been found for section name:', section_name, first, last, list_this_heading[0][0]    
        headingQ = True
    else: # In all other cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            print '5 A heading has been found for section name:', section_name, first, last, list_this_heading[0][0]
        headingQ = True
    para_indices = (first, last)
    return (para_indices, title_indices, headingQ)


### Function: pre_process_sent(sent)
### Called by find_and_label_headings in this file.
### Processes one sentence partially (no POS, no lemm'ng) so that it can be
### directly compared with the assignment question long version.
def pre_process_sent(sent):
    sent = [w.lower() for w in sent]
    sent = [w for w in sent if w not in essay_stop_words]
    # These lines are necessary to make sent processing exactly match ass q processing.
    sent = [w for w in sent if not re.match(r'[o0-9]+$',w)] # Gets rid of single letter 'o' (used as a bullet point) and integers.
    sent = [w for w in sent if not re.match(u'\u2022',w)] # Gets rid of bullet points.
    sent = [w for w in sent if not re.match(u'\xb7',w)] # Gets rid of middle dots.
    sent = [w for w in sent if not re.match(u'-',w)] # Gets rid of a token that is a hyphen (not hyphens in the middle of hyphenated words). These often used like bullet points. Should not interfere with hyphenated words.
    return sent

# Function: get_headings(text)
# Called by find_and_label_headings in this file.
# Returns a list of all the sentences so far marked as headings.
# Each heading is accompanied by its index.
# The headings and their indices are used in different ways to find section indices.
'''
Currently sentences in the essay that are _not_ included in the key sentence graph are:
- things that are actually headings: '#-s:h#','#-s:H#', '#-s:s#', '#-s:d#', '#-s:l#'
- things that are short itemised points: '#-s:b#'
Note that long itemised points are labelled as true sentences '#+s#'.
- things that are entries in a table: '#-s:e#'
- things that are quoted from the assignment question: '#-s:q#'
- things that are captions: '#-s:c#'
- things that are in the title: '#-s:t#'
- things that are in the preface (if there is one): '#+s:p#'
- things that are in the summary (if there is one): '#+s:s#'
- things that only have numbers in them: '#-s:n#'
- things that only have punctuation in them: '#-s:p#'

For the statistical analyses I really want to know how many real headings there are
but here I need a list that will be used to locate the beginning and end of the introduction and conclusion.
'''
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
                    if (sent[0] == '#-s:h#' # special heading
                        or sent[0] == '#-s:H#' # short itemised heading
                        or sent[0] == '#-s:s#' # section heading
                        or sent[0] == '#-s:d#' # digital heading
                        or sent[0] == '#-s:l#' # letter heading
                        #or sent[0] == '#-s:b#' # xxxx note this is not an actual heading. Added for testing. At least one essay uses letters as headings so I am trying this A5059833-H810-11I_02.txt
                        #or sent[0] == '#-s:e#' # xxxx note this is not an actual heading. Added for testing.
                        #or sent[0] == '#-s:q#' # xxxx note this is not an actual heading. Added for testing.
                        or sent[0] == '#-s:t#'): # title
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

# Function: match_sentence_2_heading(sent, headings)
# Called by get_more_headings_using_contents in this file.
# Tests whether a sentence matches any of the headings. 
# Uses regular expression 'search' rather than 'match' in case of page numbers being present in heading.
def match_sentence_2_heading(sent, headings):
    #while 1:
    result = False
    for item in headings:
        if re.search(sent, item):
            result = True
    return result

                
# Function: get_more_headings_using_contents(text, headings)
# Called by find_and_label_headings in this file.
# Returns the essay with further headings marked as headings.
# This takes the list of headings found so far and goes through the essay
# to see if any sentences not marked as headings match any of the headings.
# This is done because entries in the contents page are typically picked
# up as headings because they end in a number (the page number), but the twin
# entry in the essay body may be missed if it is particularly long, as it doesn't
# end in a number. 
def get_more_headings_using_contents(text, headings):
    section_name = "Introduction"
    mylist1 = headings
    temp = count_this_heading(section_name, headings, text)
    heading_count = len(temp)
    if heading_count == 0 or heading_count == 1:
        return headings
    else: # Note that some kinds of publication, e.g., the Seale text book, have more than three 'introduction' headings.
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
                                temp = ['#-s:s#'] + sent1 # Put a 'section heading' label at the beginning (instead of 'dummy')
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
    
def table_entries_recheck1(text):
    mylist3 = []
    counter_p = 0
    while 2:
        if counter_p <= len(text)-1:
            para = text[counter_p]
            paraindex = text.index(para)
            nextpara = paraindex+1
            nextnextpara = paraindex+2
            prevpara = paraindex-1
            prevprevpara = paraindex-2
            sent = para[0]
            #print '\n\n'
            #print sent[0]
            #print nextpara
            #print nextnextpara
            #print '######################\n', para
            #####################
            # LOOK BACK ONE PARAGRAPH, IF BOTH SHORT HEADINGS, THIS IS TABLE CONTENTS
            #####################
            if (len(para) == 1 # If this para has one sentence only
                  and sent[0] == '#-s:H#' # and if this para is a short heading without a number leading or an enumerator
                  and len(sent) <= 9 # and the single sentence is shortish
                  and prevpara > 0 # This clause is needed to stop prog looking for a prev para that doesn't exist, otherwise it fails      
                  and text[prevpara][0][0] == '#-s:e#'): # and the previous para is table entries
                temp = ['#-s:e#'] + sent[1:] # label the sentence 'table entries': '#-s:e#'
                para2 = [temp] # Make the sentence into a single-sentence paragraph
                print '\n34.', para2
                mylist3.append(para2)
                counter_p += 1
            #####################
            # LOOK BACK ONE PARAGRAPH, IF BOTH DIGITAL HEADINGS, THIS IS LIST ITEM
            #####################                            
            elif (sent[0] == '#-s:d#' # and if this para starts with a digit label
                  and prevpara > 0 # This clause is needed to stop prog looking for a prev para that doesn't exist, otherwise it fails      
                  and text[prevpara][0][0] == '#-s:d#'): # and the previous para starts with a digit label
                sentlist = []
                counter_s = 0
                while 1: # Note that there may be more than one sentence in this para (owing to sentence splitter making single digits sentences) so need to label every sentence.
                    if counter_s <= len(para)-1: # # label all the sentences in this para as list items
                        s = para[counter_s]
                        temp = ['#-s:b#'] + s[1:] 
                        sentlist.append(temp)                        
                        counter_s += 1
                    else:
                        break
                para2 = sentlist                
                print '\n35.', para2                
                mylist3.append(para2)
                counter_p += 1
            #####################
            # LOOK BACK ONE PARAGRAPH, IF BOTH LETTER HEADINGS, THIS IS LIST ITEM
            #####################                
            elif (sent[0] == '#-s:l#' # and if this para is a letter heading 
                  #and len(sent) <= 9 # and the single sentence is shortish
                  and prevpara > 0 # This clause is needed to stop prog looking for a prev para that doesn't exist, otherwise it fails      
                  and text[prevpara][0][0] == '#-s:l#'): # and the previous para is letter heading
                sentlist = []
                counter_s = 0
                while 1: # label all the sentences in this para as list items
                    if counter_s <= len(para)-1:
                        s = para[counter_s]
                        temp = ['#-s:b#'] + s[1:] 
                        sentlist.append(temp)                        
                        counter_s += 1
                    else:
                        break
                para2 = sentlist
                print '\n36.', para2
                mylist3.append(para2)
                counter_p += 1
            else:
                mylist3.append(para)
                counter_p += 1
        else:
            break
    text = mylist3
    return text


def table_entries_recheck2(text):
    mylist3 = []
    counter_p = 0
    while 2:
        if counter_p <= len(text)-1:
            para = text[counter_p]
            paraindex = text.index(para)
            nextpara = paraindex+1
            prevpara = paraindex-1
            sent = para[0]
            countPassageChars = 0
            for sent in para:
                temp = ' '.join(sent[1:])
                countPassageChars += len(temp)            
            #print '\n\n'
            #print sent[0]
            #print nextpara
            #print nextnextpara
            #print '######################\n', para
            #####################
            # LOOK BACK ONE PARAGRAPH, AND FORWARD ONE PARAGRAPH. IF BOTH ARE TABLE ENTRIES, THIS IS PROBABLY ALSO TABLE ENTRY REGARDLESS OF LENGTH OR LABEL.
            #####################
            if (len(para) == 1 # If this para has one sentence only
                  #and sent[0] == '#-s:H#' # and if this para HAS ANY LABEL
                  #and len(sent) <= 9 # and the single sentence CAN BE OF ANY LENGTH
                  and prevpara > 0 # This clause is needed to stop prog looking for a prev para that doesn't exist, otherwise it fails
                  and nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                  and text[nextpara][0][0] == '#-s:e#' # and the next para is a table entry
                  and text[prevpara][0][0] == '#-s:e#'): # and the previous para is a table entry
                temp = ['#-s:e#'] + sent[1:] # label the sentence 'table entries': '#-s:e#'
                para2 = [temp] # Make the sentence into a single-sentence paragraph
                print '\n37.', para2
                #print para2
                mylist3.append(para2)
                counter_p += 1
            #####################
            # LOOK BACK ONE PARAGRAPH, AND FORWARD ONE PARAGRAPH. IF BOTH ARE LIST ITEMS, THIS IS PROBABLY ALSO A LIST ITEM REGARDLESS OF LENGTH OR LABEL.
            #####################
            elif (countPassageChars < 150 # If this para has fewer than 15 chars xxxx watch this
                  #and sent[0] == '#-s:H#' # and if this para HAS ANY LABEL
                  #and len(sent) <= 9 # and the single sentence CAN BE OF ANY LENGTH
                  and prevpara > 0 # This clause is needed to stop prog looking for a prev para that doesn't exist, otherwise it fails
                  and nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                  and text[nextpara][0][0] == '#-s:b#' # and the next para is a LIST ITEM
                  and text[prevpara][0][0] == '#-s:b#'): # and the previous para is A LIST ITEM
                sentlist = []
                counter_s = 0
                while 1: # label all the sentences in this para as list items
                    if counter_s <= len(para)-1:
                        s = para[counter_s]
                        temp = ['#-s:b#'] + s[1:] 
                        sentlist.append(temp)                        
                        counter_s += 1
                    else:
                        break
                para2 = sentlist
                print '\n38.', para2
                #print para2
                mylist3.append(para2)
                counter_p += 1
            else:
                para2 = para
                #mylist = mylist.append(para2)
                #print '\n30.', para2
                #print mylist3
                mylist3.append(para2)
                counter_p += 1
        else:
            break
    text = mylist3
    return text   


def find_and_label_headings(text,ass_q_long_words,nf2,dev):
    ass_q_long_words = [x for y in ass_q_long_words for x in y] # Unnest paragraph level of nesting in ass_q
    #######################
    # FIRST DEAL WITH ENUMERATORS THAT CONSTITUE ENTIRE 'SENTENCES' AND THE SENTENCE THAT IMMEDIATELY FOLLOWS IT.
    # (I.E., THERE'S NOTHING IN THE SENT EXCEPT THE ENUMERATOR, WHICH IS CAUSED BY THE SENTENCE SPLITTER SPLITTING ON PERIODS.)
    # THIS NEEDS DOING PARAGRAPH BY PARAGRAPH. THE WHOLE 2-SENTENCE PARAGRAPH IS LABELLED AS A HEADING.
    #######################
    paralist = []
    counter_p = 0
    while 2:
        if counter_p <= len(text)-1:
            para = text[counter_p]
            mylist2 = []
            for sent in para:
                untokend = ' '.join(sent)
                sentlen = len(untokend)
                mylist2.append(sentlen)
            paralen = sum(mylist2)
            if (para[0][0] == '#-s:n#' # if the first token of the first sentence of the para is a numeric label                                                   
                  and len(para) > 1 # and the para has more than one sentence
                  and paralen < 120): # Watch this. 
                sentlist = []
                counter_s = 0
                while 1:
                    if counter_s <= len(para)-1:
                        sent = para[counter_s]
                        temp = ['#-s:d#'] + sent[1:] # label this sentence as a digital heading
                        sentlist.append(temp)                        
                        counter_s += 1
                    else:
                        break
                paralist.append(sentlist)                        
                counter_p += 1
            else:                
                paralist.append(para)
                counter_p += 1
        else:
            break
    text = paralist
    ###############################
    # NOW TAKE EACH SENTENCE OF THE WHOLE TEXT AND EXAMINE IT AND LABEL IT
    ###############################
    mylist2 = []
    counter_p = 0
    while 2:
        if counter_p <= len(text)-1:
            para = text[counter_p]
            #para2 = [s for s in para if s[0] == '#dummy#'] # Delete from the para those sentences that are numerics and puncs leaving only those with label 'dummy'
            mylist1 = []
            counter_s = 0
            paraindex = text.index(para)
            nextpara = paraindex+1
            previouspara = paraindex-1
            while 1:
                if counter_s <= len(para)-1:
                    sent = para[counter_s]
                    sent1 = [item for item in sent if not re.search('[0-9]+',item)] # Get every item in the sent that doesn't contain numbers
                    proc_sent = pre_process_sent(sent)
                    temp = find_and_label_heading(text,sent, proc_sent, sent1, counter_s, counter_p, para, previouspara, nextpara, ass_q_long_words)
                    mylist1.append(temp)
                    counter_s += 1                        
                else:
                    break
            mylist2.append(mylist1)
            counter_p += 1
        else:
            break
    text = mylist2        
    #############################
    # NOW LOOK FOR TABLE ENTRIES AND OTHER SIMILAR
    #############################
    mylist3 = []
    counter_p = 0
    while 2:
        if counter_p <= len(text)-1:
            para = text[counter_p]
            paraindex = text.index(para)
            nextpara = paraindex+1
            nextnextpara = paraindex+2
            prevpara = paraindex-1
            prevprevpara = paraindex-2
            sent = para[0]
            #print '\n\n'
            #print sent[0]
            #print nextpara
            #print nextnextpara
            #print '######################\n', para
            #####################
            # LOOK AHEAD TWO PARAGRAPHS, IF ALL THREE SHORT HEADINGS, THIS IS TABLE CONTENTS. 
            #####################
            if (len(para) == 1 # If this para has one sentence only
                  and sent[0] == '#-s:H#' # and if this para is a short heading without a number leading or an enumerator
                  and len(sent) <= 9 # and the single sentence is shortish
                  and nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                  and nextnextpara <= len(text)-1 # Likewise          
                  and len(text[nextpara]) == 1 # and the next paragraph has one sentence
                  and text[nextpara][0][0] == '#-s:H#' # and the next para is a short heading without a number leading or an enumerator
                  and len(text[nextpara][0]) <=9 # and the length of that sentence is short
                  and len(text[nextnextpara]) == 1 # and the paragraph following the next para has one sentence
                  and text[nextnextpara][0][0] == '#-s:H#' # and the para after the next para is a short heading without a number leading or an enumerator
                  and len(text[nextnextpara][0]) <=9): # and the length of that sentence is short
                temp = ['#-s:e#'] + sent[1:] # label the sentence 'table entry': '#-s:e#'
                para2 = [temp] # Make the sentence into a single-sentence paragraph
                print '\n31.', para2
                mylist3.append(para2)
                counter_p += 1
            #####################
            # LOOK AHEAD TWO PARAGRAPHS. IF ALL THREE ARE DIGITAL HEADINGS, THIS IS A LIST OF ITEMS.
            #####################                
            #elif (len(para) == 1 # If this para has one sentence only
            elif (sent[0] == '#-s:d#' # and if this para is a heading starting with a digit
                  and nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                  and nextnextpara <= len(text)-1 # Likewise          
                  and text[nextpara][0][0] == '#-s:d#' # and the next para is a digital heading
                  and text[nextnextpara][0][0] == '#-s:d#'): # and the para after the next para is a digital heading 
                sentlist = []
                counter_s = 0
                while 1: # Note that there may be more than one sentence in this para (owing to sentence splitter making single digits sentences) so need to label every sentence.
                    if counter_s <= len(para)-1:
                        s = para[counter_s]
                        temp = ['#-s:b#'] + s[1:] # label this sentence as a list item
                        sentlist.append(temp)                        
                        counter_s += 1
                    else:
                        break
                para2 = sentlist                
                print '\n32.', para2
                mylist3.append(para2)
                counter_p += 1                            
            #####################
            # LOOK AHEAD TWO PARAGRAPHS. IF ALL THREE ARE LETTER HEADINGS, THIS IS A LIST OF ITEMS.
            #####################                
            #elif (len(para) == 1 # If this para has one sentence only
            elif (sent[0] == '#-s:l#' # and if this para is a heading starting with a letter
                  and nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                  and nextnextpara <= len(text)-1 # Likewise          
                  and text[nextpara][0][0] == '#-s:l#' # and the next para is a letter heading
                  and text[nextnextpara][0][0] == '#-s:l#'): # and the para after the next para is a letter heading 
                sentlist = []
                counter_s = 0
                while 1: # Note that there may be more than one sentence in this para (owing to sentence splitter making single digits sentences) so need to label every sentence.
                    if counter_s <= len(para)-1:
                        s = para[counter_s]
                        temp = ['#-s:b#'] + s[1:] # label this sentence as a list item
                        sentlist.append(temp)                        
                        counter_s += 1
                    else:
                        break
                para2 = sentlist                
                print '\n33.', para2
                mylist3.append(para2)
                counter_p += 1
            else:
                para2 = para
                mylist3.append(para2)
                counter_p += 1
        else:
            break
    text = mylist3
    text = table_entries_recheck1(text) # Look back two paragraphs.
    text = table_entries_recheck1(text)
    text = table_entries_recheck2(text) # If the previous and the following paras are table entries, then this is probably a table entry regardless of how long it is.
    someheadings = get_headings(text)     # Get a list of all the headings you have found, each with its index.
    allheadings = get_more_headings_using_contents(text, someheadings)  # Use the headings you have found so far to see if there are any headings you have missed. This tends to only derive additional headings if there is a 'table of contents' page.
    return text, allheadings   


    

# xxxx Note that when you write nested 'if' clauses, you must provide 'else' cases for all cases where previous 'if's succeed.                    
def find_and_label_heading(text,sent, proc_sent, sent1, counter_s, counter_p, para, previouspara, nextpara, ass_q_long_words):
    countTextChars = 0 # Count the number of characters in the whole text
    for para3 in text:
        for sent3 in para3:
            temp = ' '.join(sent3[1:])
            countTextChars += len(temp)
    countPassageChars = 0 # Count the number of characters in the text up to this paragraph
    w = counter_p + 1
    for para3 in text[:w]:
        for sent3 in para3:
            temp = ' '.join(sent3[1:])
            countPassageChars += len(temp)
    if len(sent)>1: # Sents that were pure punctuation only contain a label. Don't look in those for any words.
        firstword = sent[1] # 'firstword' is first actual word following the label
    if len(sent)>2: # Sents that were pure punctuation only contain a label. Don't look in those for any words.
        secondword = sent[2] # 'firstword' is first actual word following the label
    else:
        firstword = 'nil'
    x = len(sent) - 1 # Get the last word in the sentence
    lastword = sent[x]
    y = x-1
    penultimateword = sent[y]
    untokend = ' '.join(sent)
    toc = re.compile('contents', re.IGNORECASE) # Find out if there is a Table of Contents (for later)
    wordcount = re.compile('word count', re.IGNORECASE)
    words = re.compile('words', re.IGNORECASE)    
    introduction = re.compile('introduction', re.IGNORECASE) # make sure these are not labelled as short headings otherwise they may become table entries
    conclusion = re.compile('conclusion', re.IGNORECASE)
    summary = re.compile('summary', re.IGNORECASE)
    abstract = re.compile('abstract', re.IGNORECASE)
    preface = re.compile('preface', re.IGNORECASE)
    part = re.compile('part', re.IGNORECASE)
    letters = ['a','b','c','d','e','f','g','h','o','B','C','D','E','F','G','H'] # Note that 'o' is often used like a bullet point. I have deliberately left out 'A' for now. This needs improving.
    enums = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','One','Two','Three','Four','Five','Six','Seven','Eight'] # xxxx testing this. It might create odd results.    #t = re.compile(untokend, re.IGNORECASE)
    #######################
    # JUST PASS ON SENTS THAT HAVE ALREADY BEEN LABELLED
    #######################
    if sent[0] == '#-s:p#': # If the sentence contains only stray punctuation marks 
        temp = sent # just pass it on unchanged.
        #print '###################', temp
        print '\n1.', temp
        return temp           
    elif sent[0] == '#-s:n#': # If the sentence has already been labelled a numeric
        temp = sent # just pass it on unchanged.
        #print '###################', temp
        print '\n2.', temp
        return temp        
    elif sent[0] == '#-s:d#': # If the sentence has already been labelled a digital heading
        temp = sent # just pass it on unchanged.
        #print '###################', temp
        print '\n3.', temp
        return temp        
    #############################
    # WORD COUNT (MAY BE MULTI-SENTENCE PARA OR NOT)
    #############################
    # Note this does not need to be the first sentence, it can be any
    elif (re.match(words, lastword)
          and re.match('[0-9][0-9][0-9][0-9]',penultimateword)): #2012 TMA01_H810_ Y7508648, U2303246-H810-11I_02-1-U
        temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
        print '\n4.', temp
        return temp                            
    ########################
    # SENTENCES THAT ARE COPIED FROM THE ASSIGNMENT QUESTION (MAY BE MULTI-SENTENCE PARA OR NOT)
    ########################
    # Note this does not need to be the first sentence, it can be any
    elif proc_sent in ass_q_long_words and len(proc_sent)>1: # len condition: Y7508648-H810-12I_02-1-M        
        temp = ['#-s:q#'] + sent[1:]
        print '\n5.', temp
        return temp        
    ########################
    # SPECIAL HEADINGS: PARAGRAPH-INITIAL SENTENCES WITH SPECIAL WORDS IN THEM (MAY BE MULTI-SENTENCE PARA)
    ########################
    # Note that I cannot nest everything in this block inside the 'counter_s == 0' condition, because the condition is not exclusive.
    # I am trying to avoid repeating code by covering one-sentence paras with this multi-sentence paras code.
    elif firstword.startswith('Appendix') and counter_s == 0:
        temp = ['#-s:h#'] + sent[1:]
        print '\n6.', temp
        return temp        
    elif (firstword.startswith('Figure') or re.match(r'Fig',firstword)) and counter_s == 0: # Figure captions are not headings and they never mark the beginnings of sections.
        temp = ['#-s:c#'] + sent[1:] # xxxx introducing a new label 'caption' here.
        print '\n7.', temp
        return temp        
    elif firstword.startswith('Table') and counter_s == 0: # Table captions are not headings and they never mark the beginnings of sections.
        temp = ['#-s:c#'] + sent[1:] # xxxx introducing a new label 'caption' here.
        print '\n8.', temp
        return temp        
    elif firstword.startswith('AFTERWORD') and counter_s == 0:
        temp = ['#-s:h#'] + sent[1:]
        print '\n9.', temp
        return temp        
    elif re.search(toc, untokend) and counter_s == 0 and len(sent) < 5:
        temp = ['#-s:h#'] + sent[1:]
        print '\n10.', temp, sent
        return temp        
    elif re.search(wordcount, untokend) and counter_s == 0:
        temp = ['#-s:h#'] + sent[1:] 
        print '\n11.', temp
        return temp
    # xxxx Now that I've added the new category 'short heading', I don't want introduction and conclusion headings to be counted
    # in that category (because short headings can become table entries), so I need to find them here first.
    elif (re.search(introduction, untokend)
          and counter_s == 0
          and len(sent1) < 7
          and countPassageChars < countTextChars/3):  # The introduction heading (either real heading or table of contents heading) must be in the first quarter of the text
        temp = ['#-s:s#'] + sent[1:]
        print '\n12.', temp
        return temp
    elif (re.search(conclusion, untokend)
          and counter_s == 0
          and len(sent1) < 7
          and countPassageChars > (countTextChars/2)): # The conclusion heading (either real heading or table of contents heading) must be in the last half of the text
        temp = ['#-s:s#'] + sent[1:] 
        print '\n12.', temp
        return temp            
    elif (re.search(summary, untokend)
          and counter_s == 0
          and len(sent1) < 7): 
        temp = ['#-s:s#'] + sent[1:] 
        print '\n13.', temp
        return temp            
    elif (re.search(abstract, untokend)
          and counter_s == 0
          and len(sent1) < 7): 
        temp = ['#-s:s#'] + sent[1:] 
        print '\n14.', temp
        return temp
    elif (re.search(preface, untokend)
          and counter_s == 0
          and len(sent1) < 7): 
        temp = ['#-s:s#'] + sent[1:] 
        print '\n15.', temp        
        return temp    
    elif ((re.match(r'Part', firstword) or re.match(r'PART', firstword))
          and (re.match(r'\d+', secondword) or secondword in enums)
          and counter_s == 0
          and len(sent1) < 15): 
        temp = ['#-s:s#'] + sent[1:] 
        print '\n16.', temp        
        return temp
    elif ((re.match(r'Section', firstword) or re.match(r'SECTION', firstword))
          and (re.match(r'\d+', secondword) or secondword in enums)
          and counter_s == 0
          and len(sent1) < 15): 
        temp = ['#-s:s#'] + sent[1:] 
        print '\n17.', temp        
        return temp       
    ########################
    # SHORT PARAGRAPH-INITIAL SENTENCES STARTING A MULTI-SENTENCE PARAGRAPH
    ########################            
    elif ((counter_s == 0) # If it's the first sentence of the paragraph
          and len(para) > 1 # and the para has more than one sentence
          and len(sent1) > 1): # it does have at least one lexical word in addition to the label
        if ((firstword == u'\u2022' # if the first token is also a bullet point
              or firstword == u'\xb7' # or a middle dot
              or firstword in letters) # or another kind of list itemiser
              and len(sent1) <= 9): # and it's a shortish sentence
            temp = ['#-s:b#'] + sent[1:] # it's probably a short bullet point, even if it's not the whole paragraph. M3806725-H810-11I_02-1-U
            print '\n18.', temp
            return temp
        elif (len(sent1) <= 4 # if this sent is also very short (three or fewer words)
              and firstword not in letters
              and firstword not in enums): # and the first word is not an itemiser or an enumerator
            temp = ['#-s:h#'] + sent[1:] # it's probably a heading, even if it's not a whole paragraph. B5888256 2012 H810 TMA01.
            print '\n19.', temp
            return temp
        else:
            temp = ['#dummy#'] + sent[1:]
            print '\n20.', temp
            return temp                
            
##                        elif len(para2)==1 and len(sent)<=7 and re.search(evaluat,untokend): # xxxx these four paras just for printing out headings for H810 TMA02, not necessary otherwise
##                            print '\nEvaluation: ', sent, counter_p
##                            temp = ['#-s:h#'] + sent[1:]
##                            mylist1.append(temp)
##                        elif len(para2)==1 and len(sent)<=7 and re.search(reflect,untokend):
##                            print '\nReflection: ', sent, counter_p, 
##                            temp = ['#-s:h#'] + sent[1:]
##                            mylist1.append(temp)
##                        elif len(para2)==1 and len(sent)<=7 and re.search(compar,untokend):
##                            print '\nComparison: ', sent, counter_p
##                            temp = ['#-s:h#'] + sent[1:]
##                            mylist1.append(temp)
##                        elif len(para2)==1 and len(sent)<=7 and re.search(resource,untokend):
##                            print '\nResource: ', sent, counter_p,  
##                            temp = ['#-s:h#'] + sent[1:]
##                            mylist1.append(temp)       
    #######################
    # ONE-SENTENCE PARAGRAPHS
    #######################
    elif len(para) == 1: # If the paragraph contains only one sentence
        ###################
        # FIRST TOKEN OF THIS PARA IS A BULLET POINT OR SIMILAR
        ###################
        # Some bullet points are sentences and some are not sentences.
        # We need to distinguish between the two. The sentences will be included in the sentence graph calculations.
        # The bullet-pointed non-sentences will be included in the key word graph, but not the sentence graph.
        # Here the label is '#-s:b#'. Bullet points that are not short will not succeed here, and will be labelled as sentences.
        if ((firstword == u'\u2022' # if the first token is a bullet point 
              or firstword == u'\xb7' # or a middle dot
              or firstword == '-') # or a hyphen
              and len(sent) > 2): # If the sentence has more than two tokens in it and (more than just the label and the bullet/enumerator)           
            if (re.match('\d+$',lastword) # if the last token is a number and
                  and re.match('\d+$',sent[2])):  # if the third token is a number  # xxxx This added for Seale textbook                    
                temp = ['#-s:b#'] + sent[1:] # label the sentence 'bullet point'
                print '\n21.', temp                
                return temp
            elif len(sent) <= 9: # if this sent is also short, it's probably a bullet point 
                temp = ['#-s:b#'] + sent[1:]
                print '\n22.', temp
                return temp
            else:
                temp = ['#dummy#'] + sent[1:]
                print '\n23.', temp
                return temp
        ###################
        # FIRST TOKEN OF THIS PARA IS A LETTER
        ###################
        # Some lines beginning with a single letter token are sentences and some are not sentences.
        # We need to distinguish between the two. The sentences will be included in the sentence graph calculations.
        # The non-sentences will be included in the key word graph, but not the sentence graph.
        # Here the label is '#-s:l#'. Lines that are not short will not succeed here, and will be labelled as sentences.
        if ((firstword in letters) # If the first token is a letter. Could replace this with regex but waiting for now.
              and len(sent) > 2): # If the sentence has more than two tokens in it and (more than just the label and the letter)           
            if len(sent) <= 9: # if this sent is also short, it's probably a heading 
                temp = ['#-s:l#'] + sent[1:]
                print '\n24.', temp
                return temp
            else:
                temp = ['#dummy#'] + sent[1:]
                print '\n25.', temp
                return temp
        #######################
        # FIRST TOKEN OF THIS PARA STARTS WITH A NUMBER
        #######################
        # Lines that start with numbers need dealing with separately. Lines that start with numbers are often headings
        # even if they are quite long. But they can also be listed prose points
        elif re.search('^[0-9]+',firstword) or firstword in enums: # If first token of sentence starts with a number (arabic or roman)
            if (re.match('\d+$',lastword) # Last token is also a number
                  and not re.match('\d\d\d\d',lastword)): # UNDER 1000 (to stop year dates succeeding, no essay will have 1000 pages). R909989X-H810-10I_01-1-U_utf8.txt section 3.2 should fail here.                
                temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                print '\n26.', temp
                return temp
            elif (len(sent1) <= 16 # and it contains fewer than n lexical words
                  and len(sent1) > 0): # and there is more than 0 lexical word
                temp = ['#-s:d#'] + sent[1:] # label the sentence as 'digital heading' 
                print '\n27.', temp
                return temp                            
            else:  # If it doesn't match the above clauses but does start with a number, it's not a heading
                temp = ['#dummy#'] + sent[1:]
                print '\n28.', temp
                return temp
        #############################
        # LAST TOKEN IS A NUMBER, AND SHORTISH, PROBABLY CONTENTS PAGE ENTRY
        #############################
        elif re.match('\d+$',lastword) and not re.match('\d\d\d\d',lastword) and len(sent) < 17: # If last word IS a number, and the sentence is shortish, it's probably in the contents page 
            temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
            print '\n29.', temp
            return temp                            
        #############################
        # REMAINING SHORTISH SINGLE-SENTENCE PARAS    
        #############################
        # The reason for putting this last and not first is because I want to label some bullet points as bullet points and not as headings.
        # Many bullet points would match this rule and be labelled as headings if it was put first.
        # I also am considering labelling table of contents items. 
        # Note that this essay needs the number to be 8 or many headings are missed: B5843667_TMA01_H810_2012. Also H810_TMA01_9Oct12_B379967X needs 8.
        elif len(sent) <= 12: # If the sentence has fewer than 8 words in it. Note that this essay needs the number to be 8 or many headings are missed: B5843667_TMA01_H810_2012_latin9.txt. Also H810_TMA01_9Oct12_B379967X needs 8.
            temp = ['#-s:H#'] + sent[1:] # label it as 'not a sentence' (replace dummy label) currently meaning probably a heading
            print '\n30.', temp
            return temp                            
        else: # If the para contains only one sentence and doesn't match any of the above rules, it's not a heading
            temp = sent
            print '\n40.', temp            
            return temp                            
    else:
        temp = sent
        print '\n41.', temp        
        return temp                        
    #print sent
    #print temp, '\n'
    #print '#######################'
    #print '#######################'
    #print '#######################'    
    #return temp    

# Called by pre_process_struc in se_procedure.py
def find_and_label_section_sents(text50,headings,nf,nf2,dev):

    # Set variables 'section_names' and 'section_labels'.
    # Orders must match.
    section_names =  ['AssQ',  'Title', 'SectionHeadings', 'SpecialHeadings', 'GeneralHeadings','ItemisedShort', 'TableEntries', 'Captions', 'DigitalHeadings', 'LetterHeadings', 'Introduction', 'Conclusion', 'Summary', 'Preface', 'Numerics', 'Punctuation']
    section_labels = ['#-s:q#','#-s:t#','#-s:s#',          '#-s:h#',          '#-s:H#',         '#-s:b#',        '#-s:e#',       '#-s:c#',   '#-s:d#',          '#-s:l#',         '#+s:i#',       '#+s:c#',     '#+s:s#',  '#+s:p#',  '#-s:n#',   '#-s:p#']
    # Find the indices of the first and last paragraphs of the
    # conclusion section.
    ((c_first, c_last),title_indices,conclheaded) = find_section_paras(text50, 'Conclusion', headings, nf, nf2, dev)

    # Label the conclusion sentences using the indices you have just found.
    text50a = label_section_sents(text50, 'Conclusion', section_names, section_labels, c_first, c_last)

    # Find the indices of the first and last paragraphs of the summary section (if there is one).
    ((first, last),(title_first1,title_last1),headingQ) = find_section_paras(text50, 'Summary', headings, nf, nf2, dev)
    # Label the summary sentences using the indices you have just found.    
    text51 = label_section_sents(text50a, 'Summary', section_names, section_labels, first, last)

    # Find the indices of the first and last paragraphs of the preface section (if there is one).    
    ((first, last),(title_first2,title_last2),headingQ) = find_section_paras(text50, 'Preface', headings, nf, nf2, dev)
    # Label the preface sentences using the indices you have just found.
    text52 = label_section_sents(text51, 'Preface', section_names, section_labels, first, last)
       
    # Find the indices of the first and last paragraphs of the introduction section.
    ((i_first, i_last),(title_first3,title_last3),introheaded) = find_section_paras(text50,'Introduction', headings, nf, nf2, dev)        
    # Label the introduction sentences using the indices you have just found.
    text53 = label_section_sents(text52, 'Introduction', section_names, section_labels, i_first, i_last)
    
    # The title will typically appear before the summary if there is
    # one, and before the preface if there is one. But introductions
    # typically follow summaries and prefaces. So we need to look for
    # a title in each case and choose the first one that succeeds.
    if title_first1 != []:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first1, title_last1)
    elif title_first2 != []:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first2, title_last2)
    else:
        text77 = label_section_sents(text53, 'Title', section_names, section_labels, title_first3, title_last3)
    # Function 'count_words' counts the words in the body text only,
    # not the headings, captions, not the title.

    return text77,section_names,section_labels,headings,conclheaded,c_first,c_last,introheaded,i_first,i_last

# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>



