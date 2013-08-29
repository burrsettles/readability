"""
readability.py

Burr Settles (2013)
burrsettles.com

Simple python module that implements several different readability metrics 
for Western European languages.

For a pretty thorough overview of these and other metrics, see:
http://www.ideosity.com/ourblog/post/ideosphere-blog/2010/01/14/readability-tests-and-formulas

Also: http://en.wikipedia.org/wiki/Category:Readability_tests
"""

import re
import unicodedata
from math import sqrt

def readability_metrics(text):
    """ Returns a dictionary containing all readability scores for a given text """
    return {
        'flesch_kincaid_ease': flesch_kincaid_ease(text),
        'gulpease': gulpease(text),
        'douma': douma(text),
        'kandel_moles': kandel_moles(text),
        'fernandez_huerta': fernandez_huerta(text),
        'flesch_kincaid_grade': flesch_kincaid_grade(text),
        'gunning_fog': gunning_fog(text),
        'coleman_liau': coleman_liau(text),
        'smog': smog(text),
        'ari': ari(text),
        'lix': lix(text),
        'rix': rix(text)
    }


"""
Readability indices: higher scores imply "easier" reading
"""

def flesch_kincaid_ease(text):
    """ http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_Reading_Ease """
    text = preprocess(text)
    return 206.835 - (1.015 * avg_words_per_sentence(text)) - (84.6 * avg_syllables_per_word(text))

def douma(text):
    """ Variant of Flesch-Kincaid for Dutch: http://www.cnts.ua.ac.be/papers/2002/Geudens02.pdf """
    text = preprocess(text)
    return 206.84 - (0.33 * avg_words_per_sentence(text)) - (0.77 * avg_syllables_per_word(text))

def kandel_moles(text):
    """ Variant of Flesch-Kincaid for French (citation not easily traceable) """
    text = preprocess(text)
    return 209 - (1.15 * avg_words_per_sentence(text)) - (0.68 * avg_syllables_per_word(text))

def gulpease(text):
    """ https://it.wikipedia.org/wiki/Indice_Gulpease """
    text = preprocess(text)
    return 89.0 + (300.0 * sentence_count(text) - 10.0 * letter_count(text))/(word_count(text))

def fernandez_huerta(text):
    """ Developed for Spanish texts (citation not easily traceable) """
    text = preprocess(text)
    factor = 100.0 / word_count(text)
    return 206.84 - (0.6 * factor * syllable_count(text)) - (1.02 * factor * sentence_count(text))


"""
Grade level estimators: higher scores imply more advanced-level material
"""

def flesch_kincaid_grade(text):
    """ http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch.E2.80.93Kincaid_Grade_Level """
    text = preprocess(text)
    return (0.39 * avg_words_per_sentence(text)) + (11.8 * avg_syllables_per_word(text)) - 15.59

def gunning_fog(text):
    """ http://en.wikipedia.org/wiki/Gunning_Fog_Index """
    text = preprocess(text)
    return 0.4 * (avg_words_per_sentence(text) + percent_three_syllable_words(text, False))

def coleman_liau(text):
    """ http://en.wikipedia.org/wiki/Coleman-Liau_Index """
    text = preprocess(text)
    return  (5.89 * letter_count(text) / word_count(text)) - (0.3 * sentence_count(text) / word_count(text)) - 15.8

def smog(text):
    """ http://en.wikipedia.org/wiki/SMOG_Index """
    text = preprocess(text)
    return 1.043 * sqrt((three_syllable_word_count(text) * (30.0 / sentence_count(text))) + 3.1291)

def ari(text):
    """ http://en.wikipedia.org/wiki/Automated_Readability_Index """
    text = preprocess(text)
    return (4.71 * letter_count(text) / word_count(text)) + (0.5 * word_count(text) / sentence_count(text)) - 21.43

"""
Other indices (not grade levels): higher scores imply "more difficult" reading
"""

def lix(text):
    """ http://en.wikipedia.org/wiki/LIX """
    text = preprocess(text)
    num_words = word_count(text)
    return (100.0 * six_letter_word_count(text) / num_words) + (1.0 * num_words / sentence_count(text))

def rix(text):
    """ More generalized variant of LIX """
    text = preprocess(text)
    return 1.0 * six_letter_word_count(text) / sentence_count(text)


"""
Various utility functions
"""

def preprocess(text):
    # convert to ASCII
    if isinstance(text, unicode):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    # if the input is HTML, force-add full stops after these tags
    fullStopTags = ['li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dd']
    for tag in fullStopTags:
        text = re.sub(r'</'+tag+'>', '.', text)
    text = re.sub(r'<[^>]+>', '', text)                  # strip out HTML
    text = re.sub(r'[,:;()\-]', ' ', text)               # replace commas, hyphens etc (count as spaces)
    text = re.sub(r'[\.!?]', '.', text)                  # unify terminators
    text = re.sub(r'^\s+', '', text)                     # strip leading whitespace
    text = re.sub(r'[ ]*(\n|\r\n|\r)[ ]*', ' ', text)    # replace new lines with spaces
    text = re.sub(r'([\.])[\. ]+', '.', text)            # check for duplicated terminators
    text = re.sub(r'[ ]*([\.])', '. ', text)             # pad sentence terminators
    text = re.sub(r'\s+', ' ', text)                     # remove multiple spaces
    text = re.sub(r'\s+$', '', text);                    # strip trailing whitespace
    return text

def letter_count(text):
    """ Gives letter count (ignores non-letters). """
    text = preprocess(text)
    newText = re.sub(r'[^A-Za-z]+', '', text)
    return len(newText)

def sentence_count(text):
    text = preprocess(text)
    # note: might be tripped up by honorifics and abbreviations
    return max(1, len(re.sub(r'[^\.!?]', '', text)))

def word_count(text):
    text = preprocess(text)
    return 1 + len(re.sub(r'[^ ]', '', text)) # space count + 1 is word count

def avg_words_per_sentence(text):
    text = preprocess(text)
    return 1.0 * word_count(text) / sentence_count(text)

def total_syllables(text):
    text = preprocess(text)
    words = text.split()
    return sum([syllable_count(w) for w in words])

def avg_syllables_per_word(text):
    text = preprocess(text)
    num_words = word_count(text)
    words = text.split()
    num_syllables = sum([syllable_count(w) for w in words])
    return 1.0 * num_syllables / num_words

def six_letter_word_count(text, use_proper_nouns = True):
    text = preprocess(text)
    num_long_words = 0;
    num_words = word_count(text)
    words = text.split()
    for word in words:
        if len(word) >= 6:
            if use_proper_nouns or word[:1].islower():
                num_long_words += 1
    return num_long_words

def three_syllable_word_count(text, use_proper_nouns = True):
    text = preprocess(text)
    num_long_words = 0;
    num_words = word_count(text)
    words = text.split()
    for word in words:
        if syllable_count(word) >= 3:
            if use_proper_nouns or word[:1].islower():
                num_long_words += 1
    return num_long_words

def percent_three_syllable_words(text, use_proper_nouns = True):
    text = preprocess(text)
    return 100.0 * three_syllable_word_count(text, use_proper_nouns) / word_count(text)

def syllable_count(word):
    """ Pretty good heuristic: treat consecutive vowel strings as syllables. """
    word = word.lower()
    # remove non-alphanumeric characters
    word = re.sub(r'[^a-z]', '', word)
    word_bits = re.split(r'[^aeiouy]+', word)
    num_bits = 0
    for wb in word_bits:
        if wb != '':
            num_bits += 1
    return max(1, num_bits)
