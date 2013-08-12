import re # For regular expressions
from nltk.tokenize import LineTokenizer, WordPunctTokenizer, PunktSentenceTokenizer  
from nltk.stem.wordnet import WordNetLemmatizer
from se_stops import essay_stop_words
# WordPunctTokenizer: Word tokeniser that separates punctuation marks from words
# PunktSentenceTokenizer: The standard sentence tokeniser used by NLTK
# LineTokenizer: "tokenizer that divides a string into substrings by treating any single newline character as a separator."

"""
This file contains the functions for doing all the NLP pre-processing,
but not the structure pre-processing.
Functions names:
def remove_unwanted_pos(text):
def print_function_name(sent):
def print_unicode_name(sent):
def parasent_tokenize(text):
def count_refs(text):
def get_essay_body(parasenttok,nf,dev):
def find_appendix_head(parasenttok,refs_head_index,nf,dev):       
def find_word_count_index(parasenttok,nf,dev):
def find_refs_heading(parasenttok,nf,dev):
def edit_text(text):
def reinstate_hyphens1(sent):
def reinstate_hyphens2(sent):
def process_sents(do_this, text):
def word_tokenize(text):
def remove_punc_fm_sents(sent):
def count_words(sent):
def find_and_label_numeric_sents(sent):
def lowercase_sents(sent):
def remove_stops_fm_sents(sent):
def get_lemmas(sent):
"""

### Called by 'pre_process_text' in file 'se_procedure.py'.
##def remove_unwanted_pos(text):
##    #tags=['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'RB', 'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
##    #newtext = [item for item in text if item[1] in tags]
##    tags = ['CD'] # This will get 'one', 'twenty', etc., and the integers.
##    newtext = [item for item in text if item[1] not in tags]
##    #print item
##    #print item[1]
##    return newtext

# Called by 'pre_process_text' in file 'se_procedure.py'.
##def print_function_name(sent):
##    if sent.startswith('def '):        
##        print sent


### Function:
# Called by 'pre_process_text' in file 'se_procedure.py'.
##def print_unicode_name(sent):
##    c = unicode(sent)
##    #print c
##    if c.startswith("u'\u"): #u'\u03c31'
##        #s = str(sent)
##        #c = s.decode('unicode-escape')
##        #nf2.write(c)    
##        #nf2.write('\n')
##        print sent

# Called by pre_process_text in file se_procedure.py.
def parasent_tokenize(text):
    # Paragraph-tokenisation results in having quotation marks as paragraph delimiters.
    paratok = LineTokenizer().tokenize(text)
    # Sentence-tokenisation results in having quotation marks as sentence delimiters,
    # and preserves the paragraph delimiters by using square brackets.
    result = [PunktSentenceTokenizer().tokenize(item) for item in paratok]     # xxxx normal NLTK sentence splitter   
    #parasenttok = sentence_tokenize(model,paratok) # This calls a sentence splitter that uses a model. The model takes a few seconds to load.
    return result

# Function: count_refs(text)
# Called by 'get_essay_body(parasenttok,nf,dev)' in this file.
# Counts the number of paragraphs of particular types contained by 'text'.
# Var 'text' is the subsection of the essay that has already been identified
# as being the references section.
def count_refs(text,numsq):
    refs_counter = 0
    p_counter = 0 # paragraph counter
    while 1:
        if p_counter <= len(text)-1:
            x = 0
            para = ' '.join(text[p_counter]) # Make the whole paragraph into a single string
            x = len(para)
            if (re.search('^[0-9]+',para[0]) and numsq=='nonums'): # If the first character of the paragraph is a number, this is probably not a reference but a footnote and should not be counted as a reference. See A1862829-H810-10I_02-1-U.
                p_counter +=1
                #print '\n~~~~~~~~~~~~get_essay_body 0', para
##            elif (re.search(u'^\u2022',para[0])): # If the first character of the paragraph is a bullet point, this is probably not a reference but a footnote and should not be counted as a reference. 
##                p_counter +=1
##                print '\n~~~~~~~~~~~~get_essay_body 1', para
            elif (not re.search('[a-zA-Z]+',para)): # If there are no alphabetic characters in this paragraph, this is not a reference. See X8204920-H810-10I_02-1-U.txt.
                p_counter +=1
                #print '\n~~~~~~~~~~~~get_essay_body 2', para
            elif x > 50 and x < 400: # Only count the remaining paragraphs whose total number of characters is more than 50 and less than 400. Note that B5081458-H810-10I_02-1-U has an unheaded appendix following the refs and I am trying to avoid it being identified as refs.                
                #print '\n~~~~~~~~~~~~get_essay_body 3 p_counter', p_counter
                refs_counter +=1
                p_counter +=1                
            else: # This is not a reference so just increment counter
                p_counter +=1
        else:
            break
    return refs_counter


# Function: get_essay_body(parasenttok,nf,dev)
# Called by pre_process_text in file se_procedure.py.
# This renames the passage of text before the references and appendices section as 'newtext'.
# It looks for a references heading, appendices headings, word count citation,
# and uses those to decide where the body of the essay finishes.
def get_essay_body(parasenttok,nf,dev):
    refs_head_index,newtext,responseR = find_refs_heading(parasenttok,nf,dev)
    #responseR = False # xxxx Need to swap this line with above line when printing function names
    if responseR == True:
        last_body_para_index = refs_head_index - 1
        position, appendix_head_index, responseA = find_appendix_head(parasenttok,refs_head_index,nf,dev) # See if there is an appendix following the refs section
        if appendix_head_index != [] and position == 'after': # If the appendix occurs after the refs...
            x = refs_head_index+1
            #print '\n\n\n\n\n**********refs_head_index', refs_head_index
            #print '\n\n\n\n\n**********appendix_head_index', appendix_head_index            
            y = appendix_head_index-1
            refs_counter = count_refs(parasenttok[x:y],'nonums')  # Count refs from the refs heading to the beginning of the appendices          
        elif appendix_head_index != [] and position == 'before': # If the appendix occurs before the refs...
            last_body_para_index = appendix_head_index - 1 # Make the last paragraph of the body the paragraph before the appendix heading
            newtext = parasenttok[:last_body_para_index]
            x = refs_head_index+1
            refs_counter = count_refs(parasenttok[x:],'nonums')  # Count refs from the refs heading to the end of the text
            if refs_counter == 0 and x != parasenttok[-1]: # If no refs have been found despite there being a refs heading and there is text beyond the refs heading
                #print '\n\n\n\n\n******************refs_counter 1', refs_counter
                refs_counter = count_refs(parasenttok[x:],'nums') # This may be because the author has put numbers in front of the references, in which case, try counting the refs without dismissing number-initial lines.            
        else: # If no appendix head has been found
            x = refs_head_index+1
            refs_counter = count_refs(parasenttok[x:],'nonums') # Count refs from the refs heading to the end of the text
            if refs_counter == 0 and x != parasenttok[-1]: # If no refs have been found despite there being a refs heading and there is text beyond the refs heading
                #print '\n\n\n\n\n******************refs_counter 2', refs_counter
                refs_counter = count_refs(parasenttok[x:],'nums') # This may be because the author has put numbers in front of the references, in which case, try counting the refs without dismissing number-initial lines.
                #print '\n\n\n\n\n******************refs_counter 3', refs_counter
        if dev == 'DGF':
            print '~~~~~~~~~~~~~get_essay_body found a refs heading, refs_counter = ', refs_counter
        return last_body_para_index, newtext, refs_counter, responseR,[],responseA # If you don't look for word count, return nil as word count answer.
    elif responseR == False:          # If no refs heading has been found
        wc_index,newtext,responseW = find_word_count_index(parasenttok,nf,dev) # Look for string 'word count' (any case, search from end backwards)
        if responseW == True:
            if dev == 'DGF':
                print '~~~~~~~~~~~~get_essay_body found a word count phrase~~~~~~~~~~~'
            last_body_para_index = wc_index
            x = wc_index + 1
            position, appendix_head_index, responseA = find_appendix_head(parasenttok,wc_index,nf,dev) # See if there is an appendix following the refs section
            if appendix_head_index != []:
                y = appendix_head_index-1
                refs_counter = count_refs(parasenttok[x:y],'nonums') # Count refs from the word count to the appendix heading
                #print '\n\n~~~~~~~~~~~~APPENDIX SECTION~~~~~~~~:', responseA, parasenttok[appendix_head_index:]
            else:
                refs_counter = count_refs(parasenttok[x:],'nonums') # Count refs from the word count to the end of the text
                if refs_counter == 0 and x != parasenttok[-1]: # If no refs have been found despite there being a word count and there is text beyond the word count heading
                    print '\n\n\n\n\n******************refs_counter 2', refs_counter
                    refs_counter = count_refs(parasenttok[x:],'nums') # This may be because the author has put numbers in front of the references, in which case, try counting the refs without dismissing number-initial lines.                
            return last_body_para_index, newtext, refs_counter, responseR,responseW,responseA
        elif responseW == False: # If no refs found and no wc found, return parasenttok without cutting. xxxx Note, not bothering to look for an appendix in these cases.
            if dev == 'DGF':
                print '~~~~~~~~~~~~ESSAY BODY NOT ISOLATED~~~~~~~~'
            return len(parasenttok),parasenttok,0, responseR,False,False

# Called by get_essay_body             
def find_appendix_head(parasenttok,refs_head_index,nf,dev):
    result = []
    p_counter = refs_head_index # Start at the REFS heading
    print '~~~~~~~~~~~~~~~parasenttok[p_counter]', parasenttok[p_counter] 
    while 1:
        if p_counter <= len(parasenttok)-1: # ... and work forwards            
            para = ' '.join(parasenttok[p_counter])
            firstsent = parasenttok[p_counter][0] # Get the first sentence only of the paragraph. Note it is not word tokenised.            
            if len(firstsent)<70: # xxxx watch this
                if ('Appendix' in firstsent or 'APPENDIX' in firstsent or 'Appendices' in firstsent or 'Annex' in firstsent):
                    if dev == 'DGF':
                        result = True
                        print '~~~~~~~~~~~~~find_appendix_head succeeds 1 with p_counter =: ', p_counter, parasenttok[p_counter]
                    return 'after', p_counter, True
                else:
                    p_counter += 1
            else:
                p_counter += 1                
        else:
            #print '~~~~~~~~~~~~~find_refs FAILS~~~~~~~~~~~'   
            break
    p_counter = refs_head_index # Start at the REFS heading
    while 1: # Start at refs heading and work backwards 
        if p_counter >= 0: # ... and stop when you reach the beginning of the text
            para = ' '.join(parasenttok[p_counter])
            firstsent = parasenttok[p_counter][0] # Get the first sentence only of the paragraph. Note it is not word tokenised.
            if len(firstsent)<50: # Note I'm not sure what this number should be. Needs to be lower than 54 for this essay: Y432872X-H810-12I_02-1-M.txt
                if ('Appendix' in firstsent or 'APPENDIX' in firstsent or 'Appendices' in firstsent or 'Annex' in firstsent):
                    if dev == 'DGF':
                        result = True
                        print '~~~~~~~~~~~~~find_appendix_head succeeds 2 with p_counter =: ', p_counter                    
                    return 'before', p_counter, True
                else:
                    p_counter -= 1
            else:
                p_counter -= 1
        else: 
            break
    return [],[], False # If none of those terms are in text, just return nil and false.

# Called by get_essay_body
# Note we only look for a word count index if no references section heading has been found.
def find_word_count_index(parasenttok,nf,dev):
    p_counter = len(parasenttok)-1 # Start at the end of the essay and work back
    p = re.compile('word count', re.IGNORECASE)
    q = re.compile('[0-9][0-9][0-9][0-9] words',re.IGNORECASE) 
    while 1:
        if p_counter >= 0:
            para = ' '.join(parasenttok[p_counter])
            if re.search(p,para) and p_counter > len(parasenttok)/2: # If phrase 'word count' occurs in this para, and this para is in the second half of the essay (avoids matching cases in the front pages)
                #if dev == 'DGF':
                    #print '\n\n~~~~~~~~~~~~~find_wc_index SUCCEEDS~~~~~~~~~~~'
                a = p_counter + 1
                newtext = parasenttok[:a]
                return p_counter,newtext,True
            elif re.search(q,para) and p_counter > len(parasenttok)/2: # If phrase 'xxxx words' occurs in this para, and this para is in the second half of the essay (avoids matching cases in the front pages)
                #if dev == 'DGF':
                    #print '\n\n~~~~~~~~~~~~~find_wc_index SUCCEEDS~~~~~~~~~~~'
                a = p_counter + 1
                newtext = parasenttok[:a]
                return p_counter,newtext,True
            else:
                p_counter -= 1      
        else:
            #if dev == 'DGF':
                #print '\n\n~~~~~~~~~~~~~find_wc_index FAILS~~~~~~~~~~~'
            break                
    return [], parasenttok, False # If 'word count' not in 2nd half of text, return text and response False.


# Function: find_refs_heading(parasenttok,nf,dev)
# Called by get_essay_body.
# This looks for a 'references'-type heading, and if it finds one,
# it discards all the text from the refs heading onwards.
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
def find_refs_heading(parasenttok,nf,dev):
    p_counter = len(parasenttok)-1 # Start at the end of the essay and work back
    while 1:
        if p_counter >= 0:
            para = ' '.join(parasenttok[p_counter]) # Get the current paragraph
            firstsent = parasenttok[p_counter][0] # Get the first sentence only of the paragraph. Note it is not word tokenised.
            if (re.search(r'(^|\n)[0-9]+',para) # para starts with one or more numbers (For TMA01_H810_V_1.0_T5218396_utf8)
                  and re.search('REFERENCES',para) # and it contains 'REFERENCES'
                  and len(parasenttok[p_counter]) < 3): # and the sentence has fewer than three words in it 
                newtext = parasenttok[:p_counter] 
                print '~~~~~~~~~~~~~find_refs SUCCEEDS 6 with p_counter = ', p_counter, parasenttok[p_counter]
                #print '~~~~~~~~~~~~~and with refs heading', parasenttok[p_counter]
                #print '~~~~~~~~~~~~~and with length of refs heading = ', len(firstsent)
                return p_counter, newtext, True            
            elif (re.search(r'(^|\n)[0-9]+',para) # para starts with one or more numbers 
                  and re.search('References',para) # and it contains 'References'
                  and len(para) < 50): # and the heading has fewer than 50 chars in it  
                newtext = parasenttok[:p_counter] 
                print '~~~~~~~~~~~~~find_refs SUCCEEDS 7 with p_counter = ', p_counter, parasenttok[p_counter]
                #print '~~~~~~~~~~~~~and with refs heading', parasenttok[p_counter]
                #print '~~~~~~~~~~~~~and with length of refs heading = ', len(firstsent)
                return p_counter, newtext, True                        
            elif len(firstsent)<50: # xxxx This doesn't work even for tma01: and p_counter > len(parasenttok)/2: # The refs heading must be in the second half of paragraphs. This may not work for TMA02.
                # I need to be more careful about 'Resources' because there are lots of headings in tma02 with 'resource' in them. I've specified single-sentence para, short, must start with 'Resources'.
##                if (len(parasenttok[p_counter]) == 1 # if the current para has only one sentence                        
##                        and re.search(r'(^|\n)Resources', firstsent)): # and it starts with 'Resources'
##                    newtext = parasenttok[:p_counter]
##                    return p_counter, newtext, True 
                if ('References' in firstsent or 'Bibliography' in firstsent
                        or 'Reference' in firstsent or 'REFERENCES' in firstsent
                        or 'REFERENCE' in firstsent or 'Resource list' in firstsent): # TMA02 file B589993x_TMA_2.txt
                    newtext = parasenttok[:p_counter]
                    print '~~~~~~~~~~~~~find_refs SUCCEEDS 8 with p_counter = ', p_counter, parasenttok[p_counter]                    
                    p_counter_index = parasenttok.index(parasenttok[p_counter])
                    print '~~~~~~~~~~~~~find_refs index of p_counter is = ', p_counter_index                     
                    return p_counter, newtext, True                
                else:
                    p_counter -= 1
            else:
                p_counter -= 1      
        else:
            #print '~~~~~~~~~~~~~find_refs FAILS~~~~~~~~~~~'   
            break                
    return [], parasenttok, False # If none of those terms is in text, just return text.

   
# Function: edit_text(text)
# Returns updated text.
# Called by pre_process_text in file se_procedure.py.
# Includes regexs to replace hyphens with 'hhhhh'.
# Hyphens are put back in after word tokenisation and punctuation removal.
#[\|\+\(\{\}\[\]\^\$\\/\-\=%\*@\&\<\>\[\]\{\}~#\^]+
def edit_text(text):
    # Some changes need making before you split on whitespace... (those where the whitespace is important)
    text = re.sub(r'Ph\.\s*D\.', "PhD ", text) # 'Ph. D.' with 'PhD ' # Note you need to do this and all changes including spaces before text is split on whitespace.
    text = re.sub(r'Ph\.\s*D', "PhD ", text) # 'Ph. D' with 'PhD ' # Note you need to do this and all changes including spaces before text is split on whitespace.
    text = re.sub(r'et\s+al\.', "et al", text) # 'et al.' with 'et al' (varying whitespace)
    text = re.sub(r'et\.\s+al\.', "et al", text) # 'et. al.' with 'et al' (varying whitespace) # not correct but nevertheless used A2002667-H810-10I_02-1-U
    # Some changes are made after you split on whitespace...
    text = re.split(r' ', text) # Split the essay body on whitespace so you can make the following edits.
    counter = 0
    #print '\n'
    #for w in text:
     #   if re.match('^[a-zA-Z]+-[a-zA-Z]+', w): # xxxx Do not delete. To match a single or double-hyphenated word to print results to screen for identification of hyphenated words in a corpus. Note that this will match u're-prioritised.\r\nThere' from 2012 essay C1264876, and 'There' will be printed on the following line. If I make the test tighter than this, I lose valid candidates.
      #      print w
    # The part inside the round brackets is referred to by the numbered placeholders in the substituted expression.
    # The part inside the first pair of round brackets means 'this pattern is either token-initial or line-initial.      
    text = [re.sub(r'(^|\n)([a-zA-Z]+[hH])-([a-zA-Z]+)', r'\1\2hhhhhh\3' , w) for w in text]# 'graph-based' with 'graphhhhhhhbased'
    text = [re.sub(r'(^|\n)([a-zA-Z]+)-([a-zA-Z]+)-([a-zA-Z]+)', r'\1\2hhhhh\3hhhhh\4' , w) for w in text] # 'face-to-face' with 'facehhhhhtohhhhhface'  
    text = [re.sub(r'(^|\n)([a-zA-Z]+)-([a-zA-Z]+)', r'\1\2hhhhh\3' , w) for w in text]# 'face-off' with 'facehhhhhoff'
    text = [re.sub(r'(^|\n)([A-Z])\.([A-Z])\.([A-Z])\.', r'\1\2\3\4' , w) for w in text]# 'I.T.C.' with 'ITC'    
    text = [re.sub(r'(^|\n)([A-Z])\.([A-Z])\.', r'\1\2\3' , w) for w in text]# 'I.T.' with 'IT'
    text = [re.sub(r'(^|\n)(\d)\,(\d\d\d)', r'\1\2\3' , w) for w in text]# '1,234' with '1234'     
    text = [re.sub(r'(^|\n)(p)\.', r'\1\2', w) for w in text] # 'p.' with 'p'
    text = [re.sub(r'(^|\n)(vs)\.', r'\1\2', w) for w in text] # 'vs.' with 'vs'
    text = [re.sub(r'(^|\n)(cf)\.', r'\1\2', w) for w in text] # 'cf.' with 'cf'
    text = [re.sub(r'(^|\n)(ie)\.', r'\1\2', w) for w in text] # 'ie.' with 'ie'
    text = [re.sub(r'(^|\n)(etc)\.', r'\1\2', w) for w in text] # 'etc.' with 'etc'
    text = [re.sub(r'(^|\n)(n)\.(d)\.', r'\1\2\3', w) for w in text] # 'n.d.' with 'nd'
    text = [re.sub(r'(^|\n)(u)\.(d)\.', r'\1\2\3', w) for w in text] # 'u.d.' with 'ud'
    text = [re.sub(r'(^|\n)(u)\.(d)', r'\1\2\3', w) for w in text] # 'u.d' with 'ud'
    text = [re.sub(r'(^|\n)(i)\.(e)\.', r'\1\2\3', w) for w in text] # 'i.e.' with 'ie'
    text = [re.sub(r'(^|\n)(\(i)\.(e)\.', r'\1\2\3', w) for w in text] # '(i.e.' with '(ie'
    text = [re.sub(r'(^|\n)(\(e)\.(g)\.', r'\1\2\3', w) for w in text] # '(e.g.' with '(eg'
    text = [re.sub(r'(^|\n)(\(eg)\.', r'\1\2', w) for w in text] # '(eg.' with '(eg'
    text = [re.sub(r'(^|\n)(eg)\.', r'\1\2', w) for w in text] # 'eg.' with 'eg'
    text = [re.sub(r'(^|\n)(e)\.(g)\.', r'\1\2\3', w) for w in text] # 'e.g.' with 'eg'    
    text = ' '.join(text)     # Following the above tidy-up, un-split the body of the essay ready for sentence splitting.
    # xxxx these four lines added for testing system with Seale textbook, which returned a lot of 'for example' sentences in its top 25
    #p = re.compile('for example', re.IGNORECASE)
    #q = re.compile('for example,', re.IGNORECASE)
    #temp2 = re.sub(p, " ", text) # Remove all cases of 'for example' from this text
    #text = re.sub(q, " ", temp2) # Remove all cases of 'for example,' from this text
    ####temp = re.split(r' ', temp)
    return text

# Called by 'pre_process_text' in file 'se_procedure.py'.     
def reinstate_hyphens1(sent):
    # If the part after the hyphen starts with 'h', the regex in the next para does not work properly, so deal with those cases first.
    # xxxx Note that I have not yet covered double-hyphenated special cases.
    temp = [re.sub(r'([a-zA-Z][hH]+)hhhhhh([a-zA-Z]+)', r'\1-\2' , w) for w in sent] # 'graphhhhhhhbased' (any case) with 'graph-based'
    temp = [re.sub(r'([a-zA-Z]+)hhhhhh([a-zA-Z]+)', r'\1-h\2' , w) for w in temp] # 'stakehhhhhholder' with 'stake-holder'   
    temp = [re.sub(r'([a-zA-Z]+)hhhhh([a-zA-Z]+)hhhhh([a-zA-Z]+)', r'\1-\2-\3' , w) for w in temp] # 'facehhhhhtohhhhhface' with 'face-to-face' with 
    temp = [re.sub(r'([a-zA-Z]+)hhhhh([a-zA-Z]+)', r'\1-\2' , w) for w in temp] # 'facehhhhhoff' with 'face-off'
    return temp
    
# Called by 'pre_process_text' in file 'se_procedure.py'.
def reinstate_hyphens2(sent):
    sent = re.split(r' ', sent)
    temp = reinstate_hyphens1(sent)
    temp = ' '.join(temp)
    return temp


### Function: sentence_tokenize(model,text)
### An alternative sentence tokenizer that does a better job with abbreviations,
### but it takes several seconds to load the model.
### Returns tokenised text.
### Not currently being called, but wd be called by pre_process_text_se in file se_procedure.py.
##def sentence_tokenize(model,text):
##    mylist1 = []
##    for para in text:
##        temp = sbd.sbd_text(model, para)
##        mylist1.append(temp)
##    return mylist1


# Function: process_sents(do_this, text)
# Called by 'pre_process_text' in file 'se_procedure.py'.
# A basic list processor that works through a para-sent-tok text and calls the function 'do_this' with each sentence.
def process_sents(do_this, text):
    mylist2 = []
    for para in text:
        mylist1 = []
        for sent in para:
            temp = do_this(sent)
            mylist1.append(temp)
        mylist2.append(mylist1)
    return mylist2


# Function: word_tokenize(text)
# Called by 'pre_process_text' in file 'se_procedure.py'.
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

 
# Function: remove_punc_fm_sents(sent)
# Called by 'pre_process_text' in file 'se_procedure.py'.
# Remove from a word-tok sentence all word-tokens that contain
# punctuation marks or series of punctuation marks. 
# Also remove fancy non-ASCII chars typically used by MS Word (curly quotes, ellipsis, em dash, en dash, etc.)
# but leave in the bullet point (u'\u2022') and hyphen headings analysis later.
# Returns updated sentence.
# These items are removed because we don't want them appearing as key words or affecting the key sentence calculations.
def remove_punc_fm_sents(sent):
    #temp1 = [re.sub('--', "*", w) for w in sent] # Change double hyphens to stars, and then don't delete stars. Used as list markers. Useful for recognising non-headings.            
    #temp = [w for w in sent if not w.startswith(u'({\\')] # xxxx temporary for latex testing
    #temp = [w for w in temp if not w.startswith(u'{\\')] # xxxx temporary for latex testing
    #temp = [w for w in temp if not w.startswith(u'\\')] # xxxx temporary for latex testing
    #temp = [w for w in temp if not w.startswith(u'cite')] # xxxx temporary for latex testing
    # \- # I am not getting rid of hyphens, because they are often used as list enumerators.
    # Get rid of them later.
    temp = [w for w in sent if not re.search('[\.\|\?\+\(\)\{\}\[\]\^\$\\\'\"`!,;:/\
                                             \=%\*@\&\<\>\[\]\{\}~#\^]+', w)] # This gets rid of ASCII punctuation and symbols
    myfunnychars = [u'\u2019', u'\u2018', u'\u201a', u'\u201b', u'\u201c', # A crib for these symbols is in file unicode_symbol_codes.xlsx
                    u'\u201d', u'\u201e', u'\u201f', u'\ufeff',
                    u'\u2026', u'\u27a2', u'\ufeff', u'\xb9', u'\xb2',
                    u'\xb3', u'\u2013', u'\u2014', u'\u20AC', u'\xa3', u'\x5c', # u'\xb7',  # this 'middle dot' is used as a list enumerator by B4375120-H810-10I_01-1-U_utf8.txt

                    u'\u025b', u'\u025b\u03c9a', u'\u025b1',
                    u'\u025b3', u'\u025bp', u'\u025bu', u'\u03b112', u'\u03b12',
                    u'\u03b12\u03b21', u'\u03b121', u'\u03b13\u03b21', u'\u03b15', u'\u03b15\u03b21',
                    u'\u03b1i', u'\u03b1max', u'\u03b1tail', u'\u03b1wing', u'\u03b2',
                    u'\u03b2i', u'\u03b2j',
                    u'\u03b2m', u'\u03b2ngo', 
                    u'\u03b3', u'\u03b3\u03c4', u'\u03b3body',
                    u'\u03b3f', u'\u03b3i', u'\u03b3root', u'\u03b3tail', u'\u03b3tip', u'\u03b3w',
                    u'\u03b3x', u'\u03b4', u'\u03b40',
                    u'\u03b41', u'\u03b42', u'\u03b4c', u'\u03b4c', u'\u03b4e', u'\u03b4t',
                    u'\u03b4u', u'\u03b4v', u'\u03b4x', u'\u03b5', u'\u03b5i', 
                    u'\u03b6', u'\u03b61', u'\u03b61\u1e8b1', u'\u03b62', u'\u03b62\u1e8b2', u'\u03b6a\u03c9',
                    u'\u03b6n', u'\u03b6vs', u'\u03b7', u'\u03b70', u'\u03b7ut', u'\u03b7vis', 
                    u'\u03b8', u'\u03b80', u'\u03b8n', u'\u03b8ref', u'\u03ba',
                    u'\u03bb', u'\u03bb\u03c9a', u'\u03bbj', u'\u03bcb', u'\u03bd', u'\u03bd', u'\u03c0',
                    u'\u03c0',  u'\u03c1', u'\u03c1l3',
                    u'\u03c1ld\u03c9', u'\u03c1utt', u'\u03c3', 
                    u'\u03c30', u'\u03c31', u'\u03c32', u'\u03c3f', u'\u03c3i', u'\u03c3n', u'\u03c4', 
                    u'\u03c4', u'\u03c4\u03c9', u'\u03c41', u'\u03c42', u'\u03c42', u'\u03c4i',u'\u00A7'
                    u'\u03c4s', u'\u03c4w', u'\u03c4z', u'\u03c6', u'\u03c6fh', u'\u03c8', u'\u03c8', u'\u03c92',
                    u'\u03c9asin', u'\u03c9c', u'\u03c9cm', u'\u03c9d', u'\u03c9i', u'\u03c9iso', u'\u03c9l0\u03d50',
                    u'\u03c9t', u'\u03c9x', u'\u03d50', u'\u03d51', u'\u03d52', u'\u03d53', u'\u03d5max',
                    u'\u2033', u'\u2113', u'\u21130', u'\u21130k', u'\u2113i', u'\u2113max', u'\u2113n', u'\u2192',
                    u'\u21b5', u'\u21b5', u'\u21b5\u2020',
                    u'\u21b5\u2020', u'\u2202', u'\u2208', u'\u2211', u'\u221d', u'\u221e',
                    u'\u222b', u'\u223c', u'\u2260', u'\u2261', u'\u2264', 
                    u'\u226a', u'\u226b', u'\u3008', u'\u3009',
                    
                    u'\u2212', u'\u21B5\x2a' u'\xB0', u'\xB1',u'\xD7', u'\u03BB', u'\xA9',u'\u03BE',u'\u03C6',u'\u03B1', # xxxx From this line onwards were put in for the abstract analyses.
                    u'\u03D5', u'\u02D5',u'\u03BC',u'\u2032',u'\u03C9',u'\u2265',u'\u2248',u'\u225C'] 
    # Now label any sentence that only has punctuation marks in it as punctuation
    temp = [w for w in temp if w not in myfunnychars] # xxxx note that this doesn't find sequences of funny characters
    temp = [w for w in temp if not re.match(u'\u2026',w[0])] # This finds sequences of this character, needed for A4672317-H810-11I_01-1-U_utf8
    # Be careful not to remove the bullet points and hyphens from the text, just test to see if they are there.
    temp2 = [w for w in temp if not re.match(u'\u2022',w[0])] # This finds one or more bullet points. Note that bullet points are not being removed at this point. Nor are hyphens. 
    temp2 = [w for w in temp2 if not re.match('-',w[0])] # This finds one or more hyphens
    if (temp2 == []): # If removing all the punc marks leaves an empty sentence      # or re.match(\[[a-zA-Z]\] ,temp): # or a single letter
        result = ['#-s:p#'] + temp  # label this sentence as punctuation                
    else:
        result = ['#dummy#'] + temp # Otherwise put a 'dummy' label in as a place-holder for proper labels to be added later.
    return result
    
# Function: find_and_label_numeric_sents
# Called by 'pre_process_text' in file 'se_procedure.py'.
# If this sentence contains only numbers, label it as a numeric sentence: '#-s:n#'
# xxxx I have changed this rule a bit to try to spot list enumerators. However, it only succeeds
# for enumerators that are followed by a full stop, like "(iii)."
# Enumerators that are not followed by a full stop get joined to the beginning of the sentence/list.
# Those are dealt with later by 'find_and_label_headings'.
def find_and_label_numeric_sents(sent):
    if sent[0] == '#-s:p#': # Just pass on  a sent that has already been labelled as punc        
        return sent
    enums = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii'] # xxxx testing this. It might create odd results.
    temp = [item for item in sent if item not in enums]
    temp1 = [item for item in temp if not re.match('[0-9]+',item)] # Get every item in the sent that isn't a number
    temp2 = [item for item in temp1 if not re.match('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', item)] # Get every item in the sent that doesn't contain punc: [u'4', u'-', u'9'] from B8040371-H810-11I_02-1-U
    if temp2 == ['#dummy#']: # If the sentence is empty (apart from a 'dummy' label) after all tokens that contain numbers and list itemisers have been removed 
        temp = ['#-s:n#'] + sent[1:] # Label it as a numeric sentence (replace 'dummy' label with new label)
        result = temp
    else:
        result = sent               
    return result

# Called by 'pre_process_text' in file 'se_procedure.py'.
def count_words(sent):
    #print text[:50]
    mylist = []
    mylabels = ['#dummy#','#+s:i#','#+s:c#','#+s:s#','#+s:p#']
    if sent[0] in mylabels: # Only count the words of the true sentences, not headings, not tables, not title, not captions, etc.
        x = sum(1 for w in sent[1:]) # Don't count the structure label in the wrd count!
        mylist.append(x)
    return mylist

### Called by 'pre_process_text' in file 'se_procedure.py'.
### Second version which counts all the words, not just those in true sentences.
##def count_words(sent):
##    mylist = []
##    x = sum(1 for w in sent[1:]) # Don't count the structure label in the wrd count!
##    mylist.append(x)
##    return mylist

# Function: lowercase_sents(sent) 
# Called by 'pre_process_text' in file 'se_procedure.py'.
# Given a word-tok sentence, put all word tokens into lower case (note: but don't lowercase the label).
def lowercase_sents(sent):
    mylist = []
    counter = 0
    sent1 = sent[1:]            
    for w in sent1:
        temp = w[0].lower()
        mylist.append((temp, w[1]))
    sent2 = [sent[0]] + mylist
    return sent2

# Function: remove_stops_fm_sents(sent)
# Called by 'pre_process_text' in file 'se_procedure.py'.
# Given a sentence, remove all word tokens that are stop words (essay_stop_words).
# I _was_ checking that none of the stop words was in the index terms ('textbook_index_terms')
# but the result was nil, and it was taking a lot of time, so it has gone for now.
#[('#+s:i#', 'NN'), (u'a', 'DT'), (u'man', 'NN'), (u'had', 'VBD'), (u'a', 'DT'), (u'hen', 'VBN'), (u'that', 'IN'), (u'laid', 'JJ'), (u'a', 'DT'), (u'golden', 'JJ'), (u'egg', 'NN'), (u'for', 'IN'), (u'him', 'PRP'), (u'each', 'DT'), (u'and', 'CC'), (u'every', 'DT'), (u'day', 'NN')]
def remove_stops_fm_sents(sent):
    return [w for w in sent if w[0] not in essay_stop_words]

# Function: get_lemmas(sent)
# Called by 'pre_process_text' in file 'se_procedure.py'.
# Puts each word in a tuple with its lemma, word first, then lemma.
# The POS tag is removed.
# Note that for the lemmatiser to work properly, it needs to know the POS-tag, hence the POS-tagging.
# Test sentence: [('#+s:i#', 'NN'), ('*', '-NONE-'), ('usual', 'JJ'), ('counter', 'NN'), ('questions', 'NNS'), ('one', 'CD'), ('meets', 'NNS'), ('looking', 'VBG'), ('answers', 'NNS'), ('system', 'NN'), ('builders', 'NNS'), ('test', 'NN'), ('creations', 'NNS'), ('cleverest', 'JJS'), ('users', 'NNS'), ('instead', 'RB'), ('trying', 'VBG'), ('dumbest', 'JJS'), ('handicapped', 'JJ'), ('users', 'NNS'),('#-s:h#', 'NN'), ('tma01', 'NNP'), ('#-s:h#', 'NN'), ('michele', 'NNP'), ('farmer', 'NNP'), ('#-s:h#', 'NN'), ('c2907684', 'NNP'),('#dummy#', 'NN'), ('person', 'NN'), ('disability', 'NN'), ('purposes', 'NNS'), ('act', 'NNP'), ('physical', 'JJ'), ('mental', 'JJ'), ('impairment', 'NN'), ('impairment', 'NN'), ('substantial', 'JJ'), ('long', 'JJ'), ('term', 'NN'), ('adverse', 'NN'), ('effect', 'NN'), ('ability', 'NN'), ('carry', 'VB'), ('normal', 'JJ'), ('day', 'NN'), ('day', 'NN'), ('activities', 'NNS'), ('s6', 'NNP'), ('1', 'CD'), ('12', 'CD'), ('122', 'CD'), ('#dummy#', 'NN'), ('o', 'VBD'), ('visually', 'NNP'), ('impaired', 'VBD'), ('student', 'NN'), ('received', 'VBN'), ('tactile', 'JJ'), ('diagrams', 'NNS'), ('geography', 'NN'), ('course', 'NN'), ('#dummy#', 'NN'), ('o', 'VBD'), ('student', 'NNP'), ('fatigue', 'JJ'), ('received', 'VBN')]
# I am cleaning the text a little by getting rid of chars that were used to mark headings
# and that we therefore couldn't get rid of before the headings were identified.
# These were needed until now to derive essay structure, but we don't want them as nodes in the graphs.
# xxxx Note that I am getting rid of integers, which means that years (from citations) are going.
# This only happens in the key word graph. We don't lemmatise for the key sentence graph.
def get_lemmas(sent):
    # Note that the text is word-tokenised and POS-tagged, and so position relative to the text is now largely irrelevant.
    #sent = [w for w in sent if not re.match('^[o*0-9]+$',w[0])] # Gets rid of tokens that are 'o' or '*' or an integer. # [('#dummy#', 'NN'), ('write', 'NNP'), ('report', 'NN')
    sent = [w for w in sent if not re.match(r'[o0-9]+$',w[0])] # Gets rid of single letter 'o' (used as a bullet point) and integers.
    sent = [w for w in sent if not re.match(u'\u2022',w[0])] # Gets rid of bullet points.
    sent = [w for w in sent if not re.match(u'\xb7',w[0])] # Gets rid of middle dots.
    sent = [w for w in sent if not re.match(u'-',w[0])] # Gets rid of a token that is a hyphen (not hyphens in the middle of hyphenated words). These often used like bullet points. Should not interfere with hyphenated words.
    mylist = []
    lmtzr = WordNetLemmatizer()
    sent1 = sent[1:] # Redefine sent so it doesn't include the struc label
    wordnet_tag ={'NN':'n','NNS':'n','NNP':'n','NNPS':'n','JJ':'a','JJR':'a','JJS':'a','VB':'v','VBD':'v','VBG':'v','VBN':'v','VBP':'v','VBZ':'v','RB':'r','RBR':'r','RBS':'r'}
    for t in sent1:
	try:
	    temp = lmtzr.lemmatize(t[0],wordnet_tag[t[1][:2]])
	except:
	    temp = lmtzr.lemmatize(t[0])    # put in an exception in case it finds a POS tag that you haven't accounted for
	mylist.append((t[0],unicode(temp))) # A few of the lemmas in Wordnet lemmatizer are not in unicode, so I am forcing it here.
    mylist.insert(0,sent[0]) # Put the label back at the beginning of the sentence
    return mylist


# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
