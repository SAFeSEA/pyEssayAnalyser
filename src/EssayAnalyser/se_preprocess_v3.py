import re # For regular expressions

from nltk.corpus import stopwords # For removing uninteresting words from the text
#from nltk import PunktSentenceTokenizer 
from nltk.tokenize import WordPunctTokenizer # Word tokeniser that separates punctuation marks from words
from nltk.stem.wordnet import WordNetLemmatizer
from EssayAnalyser.utils import sbd # This is an alternative sentence splitter
"""
This file contains the functions for doing all the NLP pre-processing, but not the structure pre-processing.
Functions names:
# Function: get_essay_body(text2,nf,dev)
# Function: update_text(text, x, y, counter)
# Function: restore_quote(text, counter)
# Function: tidy_up_latin9(text)
# Function: sentence_tokenize(model,text)
# Function: word_tokenize(text)
# Function: remove_punc_fm_sents(sent)
# Function: count_words(text)
# Function: process_sents(do_this, text)
# Function: remove_stops_fm_sents(sent)
# Function: find_and_label_numeric_sents
# Function: get_lemmas(sent)

"""
# Function: get_essay_body(text2,nf,dev)
# Currently this gets all that occurs before the bibliography
#(actually before the last occurrence of the term 'references' (or ...)). 
# Note: I have not used case-insensitive matching, because I don't want to
# match lower-case instances because of ambiguity of 'reference' and 'references'.
# I have tried various ways of using a disjunction for this, but have not yet succeeded.
# Called by pre_process_text_se in file se_procedure.py.
def get_essay_body(text2,nf,dev):
    if 'References' in text2:
        a = text2.rfind('References') # Find the LAST occurrence of 'References', not the first, in case there is a contents page or other xref.        
        b = text2[:a] # Get all the text2 of the essay occurring before the bibliography (the body).
        return b, 'yes'    
    elif 'REFERENCES' in text2:
        a = text2.rfind("REFERENCES") 
        b = text2[:a] 
        return b, 'yes'
    elif 'Reference' in text2: # One essay I looked at had the bibliography section title: 'Reference list'.
        a = text2.rfind("Reference") 
        b = text2[:a] 
        return b, 'yes'
    elif 'REFERENCE' in text2: # One essay I looked at had: 'REFERENCE'.
        a = text2.rfind("REFERENCE") 
        b = text2[:a] 
        return b, 'yes'         
    elif 'Bibliography' in text2:
        a = text2.rfind("Bibliography") 
        b = text2[:a] 
        return b, 'yes'
    else:
        if dev == 'DGF':
            print '\n********* Cannot find a references section. *********\n'
            nf.write('\n********* Cannot find a references section. *********\n')
        return text2, 'no' # If none of those terms are in text, just return text.

# Function: update_text(text, x, y, counter)
# A basic substitution operation that carries out character substitution in a text (a list of words).
# Called by restore_quote.
# Returns updated text.
def update_text(text, x, y, counter):
    list.remove(text, x) # Substitute the new string you have made for the old string.
    list.insert(text, counter, y) # (There must be a better way of doing this.)
    return text             

# Function: restore_quote(text, counter)
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
    
# Function: tidy_up_latin9(text)
# Text saved in encoding Latin9 substitutes a question mark for
# curly speech marks and curly apostrophes and en-dashes and em-dashes.
# Among other tidying up, this function replaces dashes with hyphens and puts back apostrophes and speech marks.
# It does not cover every case, but it does a reasonable job.
# Returns updated text.
# Called by pre_process_text_se in file se_procedure.py.
# Will become obselete or radically different when I change over to unicode.
def tidy_up_latin9(text):
    counter = 0
    text = [re.sub('^i\.e\.', "ie", w) for w in text] # 'i.e.' with 'ie'
    text = [re.sub('^e\.g\.', "eg", w) for w in text] # 'e.g.' with 'eg'
    text = [re.sub('^e-', "e", w) for w in text] # 'e-' with 'e'    
    text = [re.sub('\n\?$', "\n* ", w) for w in text] # paragraph-initial question mark followed by whitespace replaced with paragraph marker then a star then a space
    text = [re.sub('\\xfc', "u", w) for w in text] # 'u umlaut' 
    text = [re.sub('\\xf6', "o", w) for w in text] # 'o umlaut' 
    text = [re.sub('\\xb9', "", w) for w in text] # footnote marker     
    text = [re.sub('\\xe9', "e", w) for w in text] # 'e accute' 
    text = [re.sub('\\xa3', "GBP ", w) for w in text] # British pound sign
    text = [re.sub('\\xa0', " ", w) for w in text] 
    text = [re.sub('\t', " ", w) for w in text] # Just getting rid of tab characters that are attached to words
    text = [re.sub('\r', " ", w) for w in text] # Just getting rid of '\r' characters that are attached to words
    #text = [re.sub('\n', "", w) for w in text] # Just getting rid of '\n' characters that are attached to words    
    text = [re.sub('\?t$', "'t", w) for w in text] # Apostrophe: "don?t" becomes "don't"
    text = [re.sub('^\?$', "--", w) for w in text]   # Em-dashes and en-dashes: 'access ? enrolment' becomes 'access -- enrolment'
    text = [re.sub('\?s$', "'s", w) for w in text]   # Apostrophe: "Frankenstein?s" becomes "Frankenstein's"
    text = [re.sub('^p\.$', "p", w) for w in text]   # change 'p.' to 'p'
    ### TODO: added substitution for missing characters
    text = [re.sub(u'\u2022', "*", w) for w in text]
    text = [re.sub(u'\u2019', "'", w) for w in text]
    text = [re.sub(u'\u2018', "'", w) for w in text]
    text = [re.sub(u'\u201c', "\"", w) for w in text]
    text = [re.sub(u'\u201d', "\"", w) for w in text]

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

# Function: sentence_tokenize(model,text)
# An alternative sentence tokenizer that does a better job with abbreviations,
# but it takes several seconds to load the model.
# Returns tokenised text.
# Not currently being called, but wd be called by pre_process_text_se in file se_procedure.py.
def sentence_tokenize(model,text):
    mylist1 = []
    for para in text:
        temp = sbd.sbd_text(model, para)
        mylist1.append(temp)
    return mylist1

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
# Don't remove double hyphens or stars, which can be used as list markers.
# Returns updated sentence.
# Called by pre_process_text_se in file se_procedure.py via process_sents.
def remove_punc_fm_sents(sent):
    temp1 = [re.sub('--', "*", w) for w in sent] # Change double hyphens to stars, and then don't delete stars. Used as list markers. Useful for recognising non-headings.            
    temp = [w for w in temp1 if not re.search('[\.\|\?\+\(\)\{\}\[\]\^\$\\\'!,;:/-]+', w)]
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
    mylist = []
    for para in text:
        for sent in para:
            x = sum(1 for w in sent[1:]) # Don't count the structure label in the word count!
            mylist.append(x)
            y = sum(mylist)
    return y

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

# Function: remove_stops_fm_sents(sent)
# Given a sentence, remove all word tokens that are stopwords
# (uninteresting and usually very frequent words).
# Also removes some other tokens I consider unimportant.
# xxxx Needs watching.
# Called by pre_process_struc in file se_procedure.py.
def remove_stops_fm_sents(sent):
    eng_stopwords=stopwords.words('english')
    temp = [w for w in sent if w[0] not in eng_stopwords]
    mylist = ['et', 'al', 'eg', 'ie', 'etc', 'may', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
              'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
              '&' ] # 'o' is missing, because it is used as a bullet point sometimes in Latin9. I take it out later for the key word graph.
    return [w for w in temp if w[0] not in mylist]

# Function: find_and_label_numeric_sents
# If this sentence contains only tokens that contain numbers, label it as a numeric sentence: '#-s:n#'
# Called by pre_process_struc in file se_procedure.py.
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
# and len(text[position2]) > 1: 

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
    sent = [w for w in sent if not re.match('^[o*0-9]+$',w[0])] # Gets rid of tokens that are 'o' or '*' or an integer. # [('#dummy#', 'NN'), ('write', 'NNP'), ('report', 'NN')
    mylist = []
    lmtzr = WordNetLemmatizer()
    sent1 = sent[1:] # Redefine sent so it doesn't include the struc label
    wordnet_tag ={'NN':'n','NNS':'n','NNP':'n','NNPS':'n','JJ':'a','JJR':'a','JJS':'a','VB':'v','VBD':'v','VBG':'v','VBN':'v','VBP':'v','VBZ':'v','RB':'r','RBR':'r','RBS':'r'}
    for t in sent1:
	try:
	    temp = lmtzr.lemmatize(t[0],wordnet_tag[t[1][:2]])
	except:
	    temp = lmtzr.lemmatize(t[0])    # put in an exception in case it finds a POS tag that you haven't accounted for
	mylist.append((t[0],temp))
    mylist.insert(0,sent[0]) # Put the label back at the beginning of the sentence
    return mylist
