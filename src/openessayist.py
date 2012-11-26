# Natural Language Toolkit: Dispersion Plots
#
# Copyright (C) 2001-2012 NLTK Project
# Author: Steven Bird <sb@csse.unimelb.edu.au>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

"""
A utility for displaying lexical dispersion.
"""


def dispersion_plot2(text, words, ignore_case=False):
    """
    Generate a lexical dispersion plot.

    :param text: The source text
    :type text: list(str) or enum(str)
    :param words: The target words
    :type words: list of str
    :param ignore_case: flag to set if case should be ignored when searching text
    :type ignore_case: bool
    """

    try:
        import pylab
    except ImportError:
        raise ValueError('The plot function requires the matplotlib package (aka pylab).'
                     'See http://matplotlib.sourceforge.net/')

    text = list(text)
    words.reverse()

    if ignore_case:
        words_to_comp = map(str.lower, words)
        text_to_comp = map(str.lower, text)
    else:
        words_to_comp = words
        text_to_comp = text

    points = [(x,y) for x in range(len(text_to_comp))
                    for y in range(len(words_to_comp))
                    if text_to_comp[x] == words_to_comp[y]]
    if points:
        x, y = zip(*points)
    else:
        x = y = ()
    pylab.plot(x, y, "r.", scalex=.1)
    pylab.yticks(range(len(words)), words, color="b")
    pylab.ylim(-1, len(words))
    pylab.title("Lexical Dispersion Plot")
    pylab.xlabel("Word Offset")
    pylab.show()

if __name__ == '__main__':

    import sys,nltk
    sys.path.append('c:\\nltk_data')
    import openessayist

    # from nltk.book import *
    from nltk.corpus import gutenberg
    from nltk.text import Text

    class Essay:
        def __init__(self,f,n):
            self.text = Text(gutenberg.words(f),n);
            self.fdist = nltk.FreqDist(self.text);
            self.words = sorted([w for w in set(self.text) if len(w) > 5 and self.fdist[w] > 7]);

    essay = Essay('tmah810.txt','TMA01')
    dispersion_plot2(essay.text, essay.words)
  
    #words = ['Elinor', 'Marianne', 'Edward', 'Willoughby']
    #dispersion_plot2(gutenberg.words('austen-sense.txt'), words)
