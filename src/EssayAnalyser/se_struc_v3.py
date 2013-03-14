import re # For regular expressions
""""
This file contains all the functions concerning analysing the internal structure of the essay.
The functions are mostly called by the function pre_process_struc in file se_procedure.py.
Functions names:
# Function: label_section_sents(text, section_name, section_names, section_labels, section_index_first, section_index_last)
# Function: count_this_heading(section_name, headings, text)
# Function: find_last_section_para_index(section_name, heading_index_first, text)
# Function: find_first_section_para_index(section_name, first_heading, text)
# Function: find_first_intro_para_index(section_name, first_heading, text, headings)
# Function: find_no_intro_heading_indices(text, headings)
# Function: find_first_concl_para_index(text,result_last,headings,nf,nf2,dev)
# Function: find_no_concl_heading_indices(section_name, headings, text,nf,nf2, dev)
# Function: find_title_indices(index, text)
# Function: find_section_paras(text, section_name, headings, nf,nf2,dev)
# Function: find_and_label_headings(text)
# Function: get_headings(text)
# Function: match_sentence_2_heading(sent, headings)
# Function: get_more_headings_using_contents(text, headings)
"""


# Function: label_section_sents(text, section_name, section_names, section_labels, section_index_first, section_index_last)
# Returns the full essay text having labelled each introduction (summary, conclusion...) sentence with its structural ID
# Does this by labelling every paragraph between and including the first section_name para and the last section_name para
# as already found.
# Called by pre_process_struc in se_procedure.py.
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

# Function: count_this_heading(section_name, headings, text)
# Go through every heading and see if contains the case-insensitive version of section_name.
# Return a list containing the found headings and their indices.
# Called by find_no_concl_heading_indices and other functions in this file.
def count_this_heading(section_name, headings, text):
    mylist = []
    p = re.compile(section_name, re.IGNORECASE)
    for item in headings:
        heading2 = item[0]
        temp = ' '.join(heading2)
        if re.search(p, temp):
            mylist.append(item)
    return mylist

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

# Function: find_first_section_para_index(section_name, first_heading, text)
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

# Function: find_first_intro_para_index(section_name, first_heading, text, headings)
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
    
# Function: find_no_intro_heading_indices(text, headings)
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
                    if len(temp) > 4: # If there are more than three headings like this... xxxx shaky
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

# Function: find_first_concl_para_index(text,result_last,headings,nf,nf2,dev)
# Called with arguments 'text' and the last paragraph of the essay that is not a heading ('result_last').
# Returns the index of the first paragraph of the conclusion.
# Called by find_no_concl_heading_indices.
def find_first_concl_para_index(text,result_last,headings,nf,nf2,dev):
    ((intro_first, intro_last), title_indices, headingQ) = find_section_paras(text, 'Introduction', headings, nf,nf2,dev)
    all_heading_indices = [item[1] for item in headings]
    temp2 = [item for item in all_heading_indices if item < result_last and item > intro_last] # Get all the heading indices that are earlier than the last concl paragraph and later than the last intro paragraph.
    counter1 = result_last
    first_concl_para_index = []
    p = re.compile('this report', re.IGNORECASE)
    q = re.compile('conclusion', re.IGNORECASE)
    while 1:
        if counter1 >= 0:
            temp = ' '.join(text[counter1][0])
            if re.search(p, temp): # If the first sentence of this paragraph contains the phrase 'this report', it's prob the first para of the conclusion. Put in for H810_Guy_Cowley_C1264876_TMA01_latin9
                first_concl_para_index = counter1
                break
            if re.search(q, temp): # If the first sentence of this paragraph contains the phrase 'conclusion', it's prob the first para of the conclusion. Put in for H810_Guy_Cowley_C1264876_TMA01_latin9
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

# Function: find_no_concl_heading_indices(section_name, headings, text,nf,nf2, dev)
# Returns the indices of the first and last paragraph of the conclusion.
# Works out which is the last paragraph, then uses that to find the first.
# Calls find_first_concl_para_index.
# Is called by find_section_paras only if no 'Conclusion' heading has been found.
def find_no_concl_heading_indices(section_name, headings, text,nf,nf2, dev):
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
                    first = find_first_concl_para_index(text,last,headings,nf,nf2,dev) # and find the first para
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 -= 1
        else:
            break # Stop looping when you've dealt with the first paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,last)        

# Function: find_title_indices(index, text)
# Returns the index of the title.
# Called by find_section_paras.
# Currently configured to allow only on paragraph to be returned (first title para and last title para are the same).
def find_title_indices(index, text): # 'index' is the first paragraph of the introduction
    counter1 = 0
    first = []
    p = re.compile('title', re.IGNORECASE)
    while 1: # Cycle through every sentence of the text 
        if counter1 <= len(text)-1:
            temp = ' '.join(text[counter1][0])
            if (text[counter1][0][0] == '#dummy#'
                and counter1 < index
                and re.search(p, temp)):
                    first = counter1
                    break
            elif (text[counter1][0][0] == '#dummy#' # See if this paragraph-initial sentence has label 'dummy'
                and len(text[counter1][0][0]) > 5
                and len(text[counter1][0][0]) < 28
                and counter1 < index):# and position3 == counter1):                    
                    first = counter1
                    break
            else: # If this isn't a likely section para, move on to the next para                    
                counter1 += 1
        else:
            break # Stop looping when you've dealt with the last paragraph. If you've got this far without finding the section, return [] as position of intro.
    return (first,first)

# Function: find_section_paras(text, section_name, headings, nf,nf2,dev)
# Is called by 'main' with each section type.
# First counts the number of headings for that section type, then uses the result to decide how to determine which are the section paragraphs.
# Calls different functions depending on section name and number of headings found.
# Uses information found about certain sections to find the index of the title.
# Called by pre_process_struc in file se_procedure.py.
def find_section_paras(text, section_name, headings, nf,nf2,dev):
    list_this_heading = count_this_heading(section_name, headings, text)
    if section_name == 'Preface': # Once you have counted the heading occurrences, treat prefaces exactly the same as summaries
        section_name = 'Summary'
    heading_count = len(list_this_heading) # heading_count is the number of 'section_name' headings found. Typically 2, 1, or 0. If 2, the first is probably in a contents section.
    first = []
    last = []
    title_indices = ([],[])
    headingQ = []
    if heading_count == 0 and section_name == 'Summary':
        if dev == 'DGF':
           headingQ = False
        True # Don't do anything, para indices remain empty. Not assuming that there is unlabelled Summary section, as we do with Introduction and Conclusion.        
    elif heading_count == 0 and section_name == 'Introduction': # If no 'Introduction' section heading has been found
        (first,last) = find_no_intro_heading_indices(text, headings)
        title_indices = find_title_indices(first, text)
        if dev == 'DGF':
            print '\nNo "Introduction" heading has been found\n'
            headingQ = False
    elif heading_count == 0 and section_name == 'Conclusion': # If no 'Conclusion' section heading has been found
        (first,last) = find_no_concl_heading_indices(section_name, headings, text,nf,nf2,dev)
        if dev == 'DGF':
            print '\nNo "Conclusion" heading has been found\n'
            headingQ = False
    elif heading_count == 2 and section_name == 'Introduction': # If there are two occurrences of 'Introduction' heading, first is prob contents page, and second prob body section
        first_heading = list_this_heading[1][1] # So take second occurrence as heading of body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        contents_heading_index = list_this_heading[0][1]
        title_indices = find_title_indices(contents_heading_index, text)
        if dev == 'DGF':
            print '\nAn "Introduction" heading has been found (1) \n'
            headingQ = True
    elif heading_count == 2 and section_name == 'Conclusion': # If there are two occurrences of 'Conclusion' heading, first is prob contents page, and second prob body section
        first_heading = list_this_heading[1][1] # So take second occurrence as heading of body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            print '\nA "Conclusion" heading has been found\n'
            headingQ = True
    elif section_name == 'Introduction': # In all other Introduction cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_intro_para_index(section_name, first_heading, text, headings)
        title_indices = find_title_indices(first, text)
        if dev == 'DGF':
            headingQ = True
            print '\nA heading has been found for section name:', section_name             
    elif section_name == 'Conclusion': # In all other 'conclusion' cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            headingQ = True
            print '\nA heading has been found for section name:', section_name     
    else: # In all other cases
        first_heading = list_this_heading[0][1] # So take it as heading for body intro section
        (first,last) = find_first_section_para_index(section_name, first_heading, text)
        if dev == 'DGF':
            print '\nA heading has been found for section name:', section_name
            headingQ = True
    para_indices = (first, last)
    return (para_indices, title_indices, headingQ)

# Function: find_and_label_headings(text)
# Label things that are probably headings as headings.
# so that later on you can exclude them from the results that are
# returned to the user, but don't exclude them from the ranking calculations.
# Called by pre_process_struc in file se_procedure.py.
def find_and_label_headings(text):
    mylist2 = []
    for para0 in text:
        para2 = [s for s in para0 if s[0] == '#dummy#'] # Delete from the para those sentences that are numerics and puncs leaving only those with label 'dummy'
        mylist1 = []
        counter_s = 0
        paraindex = text.index(para0)
        nextpara = paraindex+1
        previouspara = paraindex-1
        while 1:
            if counter_s <= len(para0)-1:
                sent = para0[counter_s]
                index_previous_s = counter_s - 1
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
                    q = re.compile('word count', re.IGNORECASE)
                    if (firstword.startswith('Appendix') # If first word of sentence is 'Appendix'
                        and counter_s == 0): # and this is the first sentence of the paragrah (note that some discussion sentences can start with 'Appendix', 'Figure'...)
                            temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                            mylist1.append(temp)
                    elif firstword.startswith('Figure') and counter_s == 0:  # If first word of sentence is 'Figure' and this is the first sentence of the paragraph
                        temp = ['#-s:h#'] + sent[1:] # label the sentence 'not a sentence' (replace dummy label) currently meaning probably a heading
                        mylist1.append(temp)
                    elif re.search(p, untokend) or re.search(q, untokend): # This concerns 'table of contents' and 'word count' headings. Added for one essay TMA01_H810_CG4535_Griffiths_latin9 whose last sentence is not part of the conclusion, but it was not being picked up as a heading
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif firstword == '*' and counter_s == 0 and len(sent) <= 7: # if this sent starts with a bullet point, and it is short, it's probably a heading
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif (index_previous_s == 0 #  If the previous sentence is the first sentence in the paragraph
                        and para0[index_previous_s][0] == '#-s:n#'): # and the label of the previous sentence is 'numeric s'
                        temp = ['#-s:h#'] + sent[1:] # then this is probably a heading, e.g., "2. A Very Long Heading With Lots And Lots Of Words That Would Not Get Recognised Later As A Heading...."
                        mylist1.append(temp)
                    elif len(sent0) <= 3 and counter_s == 0: # If this sent is very short (two or fewer words), it's probably a heading, even if it's not a whole paragraph. TMA0001_Torrance_latin9.txt
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif (nextpara <= len(text)-1 # This clause is needed to stop prog looking for a next para that doesn't exist, otherwise it fails
                        and len(text[nextpara][0]) > 1
                        and text[nextpara][0][1] == '*' # if the next paragraph starts with a bullet point
                        and len(sent) <= 4
                        and counter_s == 0): # and this is a very short sentence, it is probably a heading. For H810_TMA01_Jelfs_final.
                        temp = ['#-s:h#'] + sent[1:]
                        mylist1.append(temp)
                    elif (nextpara <= len(text)-1
                        and len(text[nextpara][0]) > 1
                        and text[nextpara][0][1] == '*'
                        and counter_s == 0):  # if the next paragraph starts with a bullet point, this is probably not a heading
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
                        elif len(temp2) <= 8 and sent[0] != '#-s:n#': #and sent[0] != '#-s:p#' # If the sentence has less than 8 words in it and is not a numeric sent. Note that this essay needs the number to be 8 or many headings are missed: Fleckhammer_B5843667_TMA01_H810_2012_latin9.txt. Also H810_TMA01_9Oct12_White_latin9 needs 8.
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
# Called by pre_process_struc in file se_procedure.py.
# The headings and their indices are used in different ways to find section indices.
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
# Returns the essay with further headings marked as headings.
# This takes the list of headings found so far and goes through the essay
# to see if any sentences not marked as headings match any of the headings.
# This is done because entries in the contents page are typically picked
# up as headings because they end in a number (the page number), but the twin
# entry in the essay body may be missed if it is particularly long, as it doesn't
# end in a number. If I had time to sort this out, I might use the contents
# earlier on in the process to get headings from the essay body. But I'm
# sticking with this version for now.
# Called by pre_process_struc in file se_procedure.py.
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
        x = temp[1][1] # So take second heaading as heading for body intro section                                  
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




