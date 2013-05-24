##nltk_stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',\
##             'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',\
##             'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who',\
##             'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',\
##             'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',\
##             'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',\
##             'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',\
##             'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',\
##             'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more'\
##             , 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',\
##             'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

                # personal pronouns
essay_stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                     'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                     'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                     # WH words
                     'what', 'which', 'who', 'whom','when', 'where', 'why', 'how',
                     # demonstrative pronouns
                     'this', 'that', 'these', 'those',
                     # definite and indefinite article
                     'a', 'an', 'the',
                     # coordinating conjunctions
                     'and', 'but','or', 'so', 'yet', 'nor',
                     # subordinating conjunctions
                     'if', 'because', 'as', 'until', 'while','after','although','though','before','since','than','unless'
                     'due', # A4192431-H810-10I_01-1-U_utf8
                     # conjunctive adverbs
                     "consequently", "finally", "furthermore", "hence", "however", "incidentally", 
                     "indeed", "instead", "likewise", "meanwhile", "nevertheless", "nonetheless", "unfortunately", "fortunately",
                     "otherwise", "still", #"then," #"therefore," and
                     "thus,"               
                     # adverbs to do with time
                     'now','then','already','again', 'always','yesterday','sometimes','nowadays','once', 
                     # adverbs expressing degree
                     'too', 'almost', 'only','just',
                     # adverbs expressing position
                     'here','there','further','here', 'there',
                     # other adverbs
                     'not', 'also', # A4285920-H810-10I_01-1-U_utf8
                     'rather',
                     # prepositions
                     'of', 'at', 'by', 'for', 'with','about', 'against', 'between', 'into', 'through',
                     'during',   'above', 'below','to', 'from', 'up', 'down', 'in',
                     'out', 'on', 'off', 'over', 'under','within',
                     # adjectives that quantify
                     'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',            
                     'many', # A1862829-H810-10I_01-1-U_utf8
                     'every', # A8394916-H810-11I_01-1-U_utf8, A1744983-H810-10I_01-1-U_utf8
                     # some meaning-poor adjectives
                     'own',
                     # auxiliary verbs
                     'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'having',
                     've', # A5180661-H810-10I_01-1-U_utf8               
                     'do', 'does', 'doesn', 'did', 'didn', 'doing','don',               
                     # modal verbs
                     'can', 'cannot', 'could', 'couldn', 'may', 'might', 'must','mustn','shall', 'shan',
                     'should', 'shouldn', 'will', 'would','wouldn',
                     # some meaning-poor main verbs # xxxx i don't think i can justify this 
                     # u'made', u'make', u'making', u'makes', # R0516059-H810-10I_01-1-U_utf8                                        
                     #'although', # A4683773-H810-10I_01-3-U_utf8
                     #'therefore', # B2481986-H810-10I_01-1-U_utf8
                     #'since', # B3892462-H810-10I_01-1-U_utf8
                     #'nowadays', # B3892462-H810-10I_01-1-U_utf8
                     #'still', # X8970537-H810-11I_01-1-U_utf8
                     #'already', # X8890063-H810-10I_01-1-U_utf8
                     #'though', # X7758072-H810-10I_01-1-U_utf8
                     #'however', # tma01_Amor_utf8.txt
                     #'rather', # T355460X-H810-10I_01-1-U_utf8
                     # single letters and Latin devices  
                     'eg', 'et', 'al', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                     'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# Copyright (c) 2013 Debora Georgia Field <deboraf7@aol.com>
