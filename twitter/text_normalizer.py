import spacy
"""
This library is used for preprocessing tweets which are fed into CountVectorizer() which creates a wordcount
matrix used for a Naive Bayes model.
"""

sp = None


def load_spacy():
    global sp
    if sp is None:
        sp = spacy.load('en_core_web_sm')
    return sp


def tweet_preprocessor(tweet:str) -> str:
    """
    Removes numbers, words that start with @, links, and words less than 2 characters
    :param tweet:
    :return:
    """
    sp = load_spacy()
    words = sp(tweet)
    words = [w for w in words if w.is_alpha is True]
    words = [w.text for w in words]
    words = [w for w in words if not w.startswith('@') and not w.startswith('http')]
    words = [w for w in words if len(w) > 2]
    words = ' '.join(words)
    return words
