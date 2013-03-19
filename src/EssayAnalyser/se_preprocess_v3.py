import re # For regular expressions

from nltk.corpus import stopwords # For removing uninteresting words from the text
#from nltk import PunktSentenceTokenizer 
from nltk.tokenize import WordPunctTokenizer # Word tokeniser that separates punctuation marks from words
from nltk.stem.wordnet import WordNetLemmatizer
from se_stops import essay_stop_words
from H810_TMA01_textbook_seale_index import textbook_index_terms
"""
This file contains the functions for doing all the NLP pre-processing, but not the structure pre-processing.
Functions names:
# Function: get_essay_body(text2,nf,dev)
# Function: update_text(text, x, y, counter)
# Function: restore_quote(text, counter)
# Function: edit_text_detail(text)
# Function: sentence_tokenize(model,text)
# Function: word_tokenize(text)
# Function: remove_punc_fm_sents(sent)
# Function: count_words(text)
# Function: process_sents(do_this, text)
# Function: remove_stops_fm_sents(sent)
# Function: find_and_label_numeric_sents
# Function: get_lemmas(sent)

"""

# This is used for testing purposes only at the moment.
def remove_unwanted_pos(text):
    #tags=['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'RB', 'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    #newtext = [item for item in text if item[1] in tags]
    tags = ['CD'] # This will get 'one', 'twenty', etc., and the integers.
    newtext = [item for item in text if item[1] not in tags]
    #print item
    #print item[1]
    return newtext


##def print_function_name(sent):
##    if sent.startswith('# Function:'):        
##        print sent

def print_unicode_name(sent):
    c = unicode(sent)
    #print c
    if c.startswith("u'\u"): #u'\u03c31'
        #s = str(sent)
        #c = s.decode('unicode-escape')
        #nf2.write(c)    
        #nf2.write('\n')
        print sent


# Function: get_essay_body(parasenttok,nf,dev)
# This discards everything following the references section.
# It takes parasenttok, looks for a references section,
# and returns everything occurring before the references section for further processing.
# If it doesn't find a references section, it looks for an occurrence of phrase 'word count'
# in the second half of the essay (to avoid front pp), and discards everything following 'word count'.
# Essay U451953X-H810-10I does not have a 'references' heading, and also contains
#'Reference software :dictionary and thesaurus' as a bullet point.
# This means that we need to stop 'find_refs' falsely identifying
# the refs section from the bullet point. We also need to add a new way
# of identifying the refs section. This essay has a 'word count' following the body,
# as many do, so I am using that.
# Called by pre_process_text_se in file se_procedure.py.
def get_essay_body(parasenttok,nf,dev):
    refs_head_index,newtext,responseR = find_refs_heading(parasenttok,nf,dev)
    if responseR == True:
        last_body_para_index = refs_head_index - 1
        appendix_head_index, responseA = find_appendix_head(parasenttok,refs_head_index,nf,dev) # See if there is an appendix following the refs section
        if appendix_head_index != []:
            refs = parasenttok[refs_head_index:appendix_head_index]
            #print '\n\n~~~~~~~~~~~~APPENDIX SECTION~~~~~~~~:', responseA, parasenttok[appendix_head_index:]
        else:
            refs = parasenttok[refs_head_index:] # Get the references section
        #print '\n\n~~~~~~~~~~~~REFS SECTION~~~~~~~~\n', refs, len(refs)
        if dev == 'DGF':
            print '~~~~~~~~~~~~get_essay_body found a refs heading~~~~~~~~~~~'
        return last_body_para_index, newtext, len(refs)-1, responseR,[],responseA # If you don't look for word count, return nil as word count answer.
    elif responseR == False:          # If no refs heading has been found
        wc_index,newtext,responseW = find_word_count_index(parasenttok,nf,dev) # Look for string 'word count' (any case, search from end backwards)
        if responseW == True:
            if dev == 'DGF':
                print '~~~~~~~~~~~~get_essay_body found a word count phrase~~~~~~~~~~~'
            last_body_para_index = wc_index
            x = wc_index + 1
            appendix_head_index, responseA = find_appendix_head(parasenttok,wc_index,nf,dev) # See if there is an appendix following the refs section
            if appendix_head_index != []:
                refs = parasenttok[x:appendix_head_index]
                #print '\n\n~~~~~~~~~~~~APPENDIX SECTION~~~~~~~~:', responseA, parasenttok[appendix_head_index:]
            else:
                refs = parasenttok[x:] # Get the references section
                #refs = parasenttok[x:] # Get the references section
            #print '\n\n~~~~~~~~~~~~REFS SECTION~~~~~~~~\n', refs, len(refs)
            return last_body_para_index, newtext, len(refs), responseR,responseW,responseA
        elif responseW == False: # If no refs found and no wc found, return parasenttok without cutting. xxxx Note, not bothering to look for an appendix in these cases.
            if dev == 'DGF':
                print '~~~~~~~~~~~~ESSAY BODY NOT ISOLATED~~~~~~~~'
            return len(parasenttok),parasenttok,0, responseR,False,False

def find_appendix_head(parasenttok,refs_head_index,nf,dev):       
    p_counter = refs_head_index # Start at the REFS heading and work forwards
    while 1:
        if p_counter <= len(parasenttok)-1:
            #print '######################THIS IS parasenttok[p_counter]', parasenttok[p_counter]
            para = ' '.join(parasenttok[p_counter])
            if 'Appendix' in para: # 
                #newtext = parasenttok[:p_counter]
                #print '~~~~~~~~~~~~~find_refs SUCCEEDS 1~~~~~~~~~~~'
                return p_counter, True                
            elif 'APPENDIX' in para:
                newtext = parasenttok[:p_counter] 
                #print '~~~~~~~~~~~~~find_refs SUCCEEDS 2~~~~~~~~~~~'
                return p_counter, True                                
            elif 'Appendices' in para:
                newtext = parasenttok[:p_counter] 
                #print '~~~~~~~~~~~~~find_refs SUCCEEDS 3~~~~~~~~~~~'                
                return p_counter, True                
            else:
                p_counter += 1      
        else:
            #print '~~~~~~~~~~~~~find_refs FAILS~~~~~~~~~~~'   
            break                
    return [], False # If none of those terms are in text, just return nil and false.

def find_word_count_index(parasenttok,nf,dev):
    p_counter = len(parasenttok)-1 # Start at the end of the essay and work back
    p = re.compile('word count', re.IGNORECASE)              
    while 1:
        if p_counter >= 0:
            para = ' '.join(parasenttok[p_counter])
            #print '\n This is para:', para
            #print '\n This is p:', p
            if re.search(p,para) and p_counter > len(parasenttok)/2: # If phrase 'word count' occurs in this para, and this para is in the second half of the essay (avoids matching cases in the front pages)
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
# This looks for a 'references'-type heading, and it finds one,
# it discards all the text from the refs heading onwards.
# Called by get_essay_body.
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
# I have tried various ways of using a disjunction for this, but have not yet succeeded.
def find_refs_heading(parasenttok,nf,dev):
    p_counter = len(parasenttok)-1 # Start at the end of the essay and work back
    while 1:
        if p_counter >= 0:
            #print '######################THIS IS parasenttok[p_counter]', parasenttok[p_counter]
            para = ' '.join(parasenttok[p_counter])
            if 'Reference' in para and len(parasenttok[p_counter][0]) < 20: # This len condition is for U451953X-H810-10I_01-1-U_utf8.txt which has 'Reference software :dictionary and thesaurus' as a bullet point, and does not have a 'references' heading at all.
                newtext = parasenttok[:p_counter]
                #print '~~~~~~~~~~~~~find_refs SUCCEEDS 1~~~~~~~~~~~'
                return p_counter, newtext, True                
            elif 'REFERENCE' in para:
                newtext = parasenttok[:p_counter] 
                #print '~~~~~~~~~~~~~find_refs SUCCEEDS 2~~~~~~~~~~~'
                return p_counter, newtext, True                                
            elif 'Bibliography' in para:
                newtext = parasenttok[:p_counter] 
                #print '~~~~~~~~~~~~~find_refs SUCCEEDS 3~~~~~~~~~~~'                
                return p_counter, newtext, True                
            else:
                p_counter -= 1      
        else:
            #print '~~~~~~~~~~~~~find_refs FAILS~~~~~~~~~~~'   
            break                
    return [], parasenttok, False # If none of those terms are in text, just return text.


    
# Function: edit_text_detail(text)
# Returns updated text.
# Called by pre_process_text_se in file se_procedure.py.
# Used to be called 'tidy_up_latin9', but most of that function now obsolete under Unicode.
# Not sure if I want to edit text in this way, but keeping in for now.
def edit_text_detail(text):
    counter = 0
    text = [re.sub('^i\.e\.', "ie", w) for w in text] # 'i.e.' with 'ie'
    text = [re.sub('^\(e\.g\.', "eg", w) for w in text] # '(e.g.' with '(eg'
    text = [re.sub('^,\we\.g\.', "eg", w) for w in text] # ', e.g.' with ', eg'
    text = [re.sub('^e-', "e", w) for w in text] # 'e-' with 'e'
    text = [re.sub('^on-', "on", w) for w in text] # 'on-' with 'on' (for 'on-line')
    text = [re.sub('^self-', "self", w) for w in text] # 'self-' with 'self' (for 'self-motivated') TMA01_H810_V_1.0_T5218396_Romers_utf8.txt
    text = [re.sub('-based', "based", w) for w in text] # TMA001_Blase_utf8_E29.txt
#text = [re.sub('\n', "", w) for w in text] # Just getting rid of '\n' characters that are attached to words    
    #text = [re.sub('\t', " ", w) for w in text] # Just getting rid of tab characters that are attached to words
    #text = [re.sub('\r', " ", w) for w in text] # Just getting rid of '\r' characters that are attached to words
    #text = [re.sub('^p\.$', "p", w) for w in text]   # change 'p.' to 'p'

##    #text = [re.sub('\\xfc', "u", w) for w in text] # 'u umlaut' 
##    #text = [re.sub('\\xf6', "o", w) for w in text] # 'o umlaut' 
##    #text = [re.sub('\\xb9', "", w) for w in text] # footnote marker     
##    #text = [re.sub('\\xe9', "e", w) for w in text] # 'e accute' 
##    #text = [re.sub('\\xa3', "GBP ", w) for w in text] # British pound sign
##    #text = [re.sub('\\xa0', " ", w) for w in text] 
    
    return text

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
# A basic list processor that works through a para-sent-tok text and calls the function 'do_this' with each sentence.
# Is called by 'main'.
# Called by pre_process_text_se and pre_process_struc in file se_procedure.py. 
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
# Word-tokenise a paragraph-sentence-tokenised text.
# There are different word tokenisers available in NLTK. This one
# "divides a text into sequences of alphabetic and non-alphabetic characters".
# This means that punctuation marks are represented as separate tokens from
# the words they adjoin.
# This tokeniser uses quotation marks as word delimiters.
# In the output square brackets are now used to delimit paragraphs AND sentences.
# Returns tokenised text.
# Called by pre_process_text_se in file se_procedure.py.
def word_tokenize(text):
    mylist = []
    for para in text:
         temp = [WordPunctTokenizer().tokenize(t) for t in para]
         mylist.append(temp)
    return mylist
 
# Function: remove_punc_fm_sents(sent)
# Remove from a word-tok sentence all word-tokens that contain
# punctuation marks or series of punctuation marks. 
# Also remove fancy non-ASCII chars typically used by MS Word (curly quotes, ellipsis, em dash, en dash, etc.) but leave in the bullet point (u'\u2022') for headings analysis later.
# Returns updated sentence.
# Called by pre_process_text_se in file se_procedure.py via process_sents.
def remove_punc_fm_sents(sent):
    #temp1 = [re.sub('--', "*", w) for w in sent] # Change double hyphens to stars, and then don't delete stars. Used as list markers. Useful for recognising non-headings.            
    #temp = [w for w in sent if not w.startswith(u'({\\')] # xxxx temporary for latex testing
    #temp = [w for w in temp if not w.startswith(u'{\\')] # xxxx temporary for latex testing
    #temp = [w for w in temp if not w.startswith(u'\\')] # xxxx temporary for latex testing
    #temp = [w for w in temp if not w.startswith(u'cite')] # xxxx temporary for latex testing

    temp = [w for w in sent if not re.search('[\.\|\?\+\(\)\{\}\[\]\^\$\\\'\"`!,;:/\-\
                                             \=%\*@\&\<\>\[\]\{\}~#\^]+', w)] # This gets rid of ASCII punctuation and symbols
    myfunnychars = [u'\u2019', u'\u2018', u'\u201a', u'\u201b', u'\u201c', # A crib for these symbols is in file unicode_symbol_codes.xlsx
                    u'\u201d', u'\u201e', u'\u201f', u'\ufeff',
                    u'\u2026', u'\u27a2', u'\ufeff', u'\xb9', u'\xb2',
                    u'\xb3', u'\u2013', u'\u2014', u'\u20AC', u'\xa3', u'\xb7', u'\x5c',

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

    temp = [w for w in temp if w not in myfunnychars] # xxxx note that this doesn't get rid of sequences of funny characters
    if temp == []: # If removing all the punc marks leaves an empty sentence
        result = ['#-s:p#']  # label this sentence as punctuation                
    else:
        result = ['#dummy#'] + temp # Otherwise put a 'dummy' label in as a place-holder for proper labels to be added later.
    return result

# Function: count_words(text)
# Count the words in a para-sent-word-tok text.
# Returns number of words. Done after punctuation tokens removed.
# Called by pre_process_text_se in file se_procedure.py.
def count_words(text):
    #print text[:50]
    mylist = []
    mylabels = ['#dummy#','#+s:i#','#+s:c#','#+s:s#','#+s:p#']
    y = 0
    for para in text:
        for sent in para:
            if sent[0] in mylabels: # Only count the words of the true sentences, not headings, not tables, not title
                x = sum(1 for w in sent[1:]) # Don't count the structure label in the word count!
                mylist.append(x)
                y = sum(mylist)
    return y

# Function: find_and_label_numeric_sents
# If this sentence contains only tokens that contain numbers, label it as a numeric sentence: '#-s:n#'
# Called by pre_process_struc in file se_procedure.py.
def find_and_label_numeric_sents(sent):
    temp2 = [item for item in sent if not re.search('[0-9]+',item)] # Get every item in the sent that doesn't contain numbers
    #temp2 = [item for item in temp0 if not re.search('[\.\|\*\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', item)] # Get every item in the sent that doesn't contain punc
    if sent[0] == '#-s:p#': # Just pass on sents that have already been labelled as punc
        result = sent
    elif temp2 == ['#dummy#']: # If the sentence is empty (apart from a 'dummy' label) after all tokens that contain numbers and punc have been removed 
        temp = ['#-s:n#'] + sent[1:] # Label it as a numeric sentence (replace 'dummy' label with new label)
        result = temp
    else:
        result = sent               
    return result
# and len(text[position2]) > 1: 

### Function: lowercase_sents(sent) 
### Given a word-tok sentence, put all word tokens into lower case.
# Called by pre_process_struc in file se_procedure.py.
def lowercase_sents(sent):
    mylist = []
    for w in sent:
        temp = w[0].lower()
        mylist.append((temp, w[1]))
    return mylist
    #return [w[0].lower() for w[0] in sent]



# Function: remove_stops_fm_sents(sent)
# Given a sentence, remove all word tokens that are stopwords
# (uninteresting and usually very frequent words).
# Also removes some other tokens I consider unimportant.
# xxxx Needs watching.
# Called by pre_process_struc in file se_procedure.py.
def remove_stops_fm_sents(sent):
    #eng_stopwords=stopwords.words('english')
    #temp = [w for w in sent if w[0] not in eng_stopwords]
    #mylist = ['eg', 'ie', 'etc',
    #mystopwords
    temp = [i for i in essay_stop_words if i not in textbook_index_terms] # Check that none of the stop words is in the index terms
    return [w for w in sent if w[0] not in temp]

    # 'o' is missing, because it is used as a bullet point sometimes in Latin9. I take it out later for the key word graph.
    #return [w for w in temp if w[0] not in mylist]



# Function: get_lemmas(sent)
# Puts each word in a tuple with its lemma, word first, then lemma
# The POS tag disappears.
# Note that for the lemmatiser to work properly, it needs to know the POS-tag, hence the POS-tagging.
# Test sentence: [('#+s:i#', 'NN'), ('*', '-NONE-'), ('usual', 'JJ'), ('counter', 'NN'), ('questions', 'NNS'), ('one', 'CD'), ('meets', 'NNS'), ('looking', 'VBG'), ('answers', 'NNS'), ('system', 'NN'), ('builders', 'NNS'), ('test', 'NN'), ('creations', 'NNS'), ('cleverest', 'JJS'), ('users', 'NNS'), ('instead', 'RB'), ('trying', 'VBG'), ('dumbest', 'JJS'), ('handicapped', 'JJ'), ('users', 'NNS'),('#-s:h#', 'NN'), ('tma01', 'NNP'), ('#-s:h#', 'NN'), ('michele', 'NNP'), ('farmer', 'NNP'), ('#-s:h#', 'NN'), ('c2907684', 'NNP'),('#dummy#', 'NN'), ('person', 'NN'), ('disability', 'NN'), ('purposes', 'NNS'), ('act', 'NNP'), ('physical', 'JJ'), ('mental', 'JJ'), ('impairment', 'NN'), ('impairment', 'NN'), ('substantial', 'JJ'), ('long', 'JJ'), ('term', 'NN'), ('adverse', 'NN'), ('effect', 'NN'), ('ability', 'NN'), ('carry', 'VB'), ('normal', 'JJ'), ('day', 'NN'), ('day', 'NN'), ('activities', 'NNS'), ('s6', 'NNP'), ('1', 'CD'), ('12', 'CD'), ('122', 'CD'), ('#dummy#', 'NN'), ('o', 'VBD'), ('visually', 'NNP'), ('impaired', 'VBD'), ('student', 'NN'), ('received', 'VBN'), ('tactile', 'JJ'), ('diagrams', 'NNS'), ('geography', 'NN'), ('course', 'NN'), ('#dummy#', 'NN'), ('o', 'VBD'), ('student', 'NNP'), ('fatigue', 'JJ'), ('received', 'VBN')]
# I am cleaning the text a little by getting rid of chars that were used to mark headings and that we couldn't get rid of earlier.
# These were needed until now to derive essay structure, but we don't want them as nodes in the graphs.
# xxxx Note that I am getting rid of integers, which means that years (from citations) are going.
# We may want to change this.
def get_lemmas(sent):
    #sent = [w for w in sent if not re.match('^[o*0-9]+$',w[0])] # Gets rid of tokens that are 'o' or '*' or an integer. # [('#dummy#', 'NN'), ('write', 'NNP'), ('report', 'NN')
    sent = [w for w in sent if not re.match('^[o0-9]+$',w[0])] # Gets rid of single letter 'o' (used as a bullet point) and integers.
    sent = [w for w in sent if not re.match(u'\u2022',w[0])] # Gets rid of bullet points.
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
    mylist.insert(0,sent[0]) # Put the label back at the beginning ofs the sentence
    return mylist
