# coding=utf-8
'''
Created on 14 Mar 2013

@author: Nicolas Van Labeke (https://github.com/vanch3d)


    essay['parasenttok'] # The whole text (up to the references) tokenised for paragraphs and sentences.
    essay['se_stats']['paras'] # Total number of paragraphs (includes everything that occurs before refs)
    essay['se_stats']['len_body'] # Total number of paragraphs minus the total number of headings
    essay['se_stats']['len_headings'] # Total number of headings
    essay['se_stats']['all sents'] # Total number of sentences (up to refs, including all headings, captions, etc.)
    essay['se_stats']['countTrueSent'] # Total number of true sentences (not headings, captions, title,  ass_q, toc)
    essay['se_stats']['number_of_words'] # Total number of words (I think this version includes every word that occurs before refs)
    essay['se_stats']['countAvSentLen'] # Mean average length of a tidysent
    essay['se_data']['se_ranked']  
    essay['se_graph']['nodes'] # Total number of nodes in the key sentence graph (not necessarily the same as 'all sents')
    essay['se_graph']['edges'] # Total number of edges in the key sentence graph
    essay['se_graph']['edges_over_sents'] # Number of edges in key sentence graph divided by number of true sentences
    essay['refs']['refs_present'] # Boolean: Is there a references section?
    essay['intro']['introheaded'] # Boolean: Is there an introduction heading?
    essay['intro']['i_first'] # Index: First paragraph of introduction section
    essay['intro']['i_last'] # Index: Last paragraph of introduction section
    essay['intro']['countIntroSent'] # Number of sentences in the introduction
    essay['intro']['percent_body_i'] # Percentage of the essay body that constitutes introduction
    essay['intro']['i & toprank'] # Number of the top N key sentences that are in introduction section    
    essay['concl']['conclheaded'] # Boolean: Is there a conclusion heading?
    essay['concl']['c_first'] # Index: First paragraph of conclusion section
    essay['concl']['c_last'] # Index: Last paragraph of conclusion section
    essay['concl']['countConclSent'] # Number of sentences in the conclusion
    essay['concl']['percent_body_c'] # Percentage of the essay body that constitutes conclusion
    essay['concl']['c & toprank'] # Number of the top 30 key sentences that are in conclusion section
    essay['ke_data']['fivemostfreq'] # List of the five most frequent lemmas
    essay['ke_data']['myarray_ke'] # list of lemmas and their associated inflected forms 
    essay['ke_data']['keylemmas'] # List of key lemmas
    essay['ke_data']['keywords'] # List of distinct key words  
    essay['ke_data']['all_bigrams'] # List of bigrams
    essay['ke_data']['bigram_keyphrases'] # List of distinct bigrams
    essay['ke_data']['trigram_keyphrases'] # List  of distinct trigrams
    essay['ke_data']['quadgram_keyphrases'] # List of distinct quadgrams    
    essay['ke_data']['kls_in_ass_q_long'] # List of the essay's key lemmas that occur in assignment question (long version)
    essay['ke_data']['kls_in_ass_q_short'] # List of the essay's key lemmas occurring in assignment question (short version)
    essay['ke_data']['scoresNfreqs'] # List of all the key lemmas presented like: (lemma,score,rank,frequency): "('student', 0.332893, 0, 38)"
    essay['ke_stats']['avfreqsum'] # Mean average frequency of five most frequent lemmas
    essay['ke_stats']['sum_kls_in_ass_q_long'] # Sum of the frequences of the essay's key lemmas that occur in the assignment question (long version)
    essay['ke_stats']['sum_kls_in_ass_q_short'] # Sum of the frequences of the essay's key lemmas that occur in the assignment question (short version)


'''
from EssayAnalyser.se_main_v3 import top_level_procedure

__mapkeyscore = {}

def getScore(keyword):
    if keyword in __mapkeyscore:
        return __mapkeyscore[keyword]
    else:
        return 0


def ngramToTree(ngram_list):
    treenode = []
    for [win_words,count] in ngram_list:
        subtree = []
        for kk in win_words:
            keywords = [ {'name': kk , 'mysize': getScore(kk), 'mycount': count, "colour":"#f9f0ab" } for x in range(count)]
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



def Flask_process_text(text0):
    essay = top_level_procedure(text0, None, None, None, "NVL")
    
    # Build an associative array out of the keywords list    
    
    myarray_ke = essay['ke_data']['scoresNfreqs']
    
    for (word,score,r,c) in myarray_ke:
        __mapkeyscore[word] = score

    #g = 1/0
    
    
    return essay


if __name__ == '__main__':
    import json
    import textwrap, string, pprint

    text = u'''The resource had some accessibility features that were achieved by keeping the document Microsoft® Office Word based, 
    thereby accessible for students using assistive technologies such as screen readers or voice controlled packages. I was then able 
    to make the navigation of the text primarily through headings and styles. Headings can indicate sections and subsections in a 
    long document and help any reader to understand different parts of the document and levels of importance. Students who use screen 
    reading software such as JAWS can use the Document Map to navigate, which in turn helps the student to understand the content and 
    to move around the document. If I had used direct formatting, which unfortunately I did on some occasions, then although I could 
    make the text have the same visual effect it would not appear in the document map and any screen reading software would not have 
    used it as a navigation tool. An added feature is that as a Word document a blind student could run the document through a Braille 
    embossing printer to give a Braille written document.
    '''
    essay = Flask_process_text(string.replace(textwrap.dedent(text),'\n',' '))

    print(json.dumps(essay, indent=4))

