import spacy
import re

"""
This library is used for preprocessing tweets which are fed into CountVectorizer() which creates a wordcount
matrix used for a Naive Bayes model.
"""

contractions_dict = {"ain't": "are not", "'s":" is", "aren't": "are not", "can't": "cannot", "can't've": "cannot have",
                     "‘cause": "because", "could've": "could have", "couldn't": "could not", "couldn't've": "could not have",
                     "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hadn't've": "had not have",
                     "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'd've": "he would have",
                     "he'll": "he will", "he'll've": "he will have", "how'd": "how did", "how'd'y": "how do you",
                     "how'll": "how will", "I'd": "I would", "I'd've": "I would have", "I'll": "I will",
                     "I'll've": "I will have", "I'm": "I am", "I've": "I have", "isn't": "is not", "it'd": "it would",
                     "it'd've": "it would have", "it'll": "it will", "it'll've": "it will have", "let's": "let us",
                     "ma’am": "madam", "mayn't": "may not", "might've": "might have", "mightn't": "might not",
                     "mightn't've": "might not have", "must've": "must have", "mustn't": "must not",
                     "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have",
                     "o'clock": "of the clock", "oughtn't": "ought not", "oughtn't've": "ought not have",
                     "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have",
                     "she'd": "she would", "she'd've": "she would have", "she'll": "she will", "she'll've": "she will have",
                     "should've": "should have", "shouldn't": "should not", "shouldn't've": "should not have",
                     "so've": "so have", "that'd": "that would", "that'd've": "that would have", "there'd": "there would",
                     "there'd've": "there would have", "they'd": "they would", "they'd've": "they would have",
                     "they'll": "they will", "they'll've": "they will have", "they're": "they are",
                     "they've": "they have", "to've": "to have", "wasn't": "was not", "we'd": "we would",
                     "we'd've": "we would have", "we'll": "we will", "we'll've": "we will have", "we're": "we are",
                     "we've": "we have", "weren't": "were not","what'll": "what will", "what'll've": "what will have",
                     "what're": "what are", "what've": "what have", "when've": "when have", "where'd": "where did",
                     "where've": "where have", "who'll": "who will", "who'll've": "who will have", "who've": "who have",
                     "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have",
                     "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have", "y'all": "you all",
                     "y'all'd": "you all would", "y'all'd've": "you all would have", "y'all're": "you all are",
                     "y'all've": "you all have", "you'd": "you would", "you'd've": "you would have", "you'll": "you will",
                     "you'll've": "you will have", "you're": "you are", "you've": "you have", "bc": "because", "w/": "with",
                     "2day": "today", "tmmrw": "tomorrow"}

sp = None
contraction_re = re.compile('|'.join(contractions_dict.keys()))


def load_spacy():
    global sp
    if sp is None:
        sp = spacy.load('en_core_web_sm')
    return sp


def expand_contractions(s, contraction_re, contractions_dict=contractions_dict):
    def replace(match):
        return contractions_dict[match.group(0)]
    return contraction_re.sub(replace, s)


def tweet_preprocessor_old(tweet: str) -> str:
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
    words = [w for w in words if len(w) >= 2]
    words = ' '.join(words)
    return words


def tweet_preprocessor(tweet: str) -> str:
    """
    Removes numbers, words that start with @, links, and words less than 2 characters
    :param tweet:
    :return:
    """
    # Lowercase
    # tweet = tweet.lower()

    # Replace '’' with "'"
    tweet = re.sub(r"’", "'", tweet)

    # Expand contractions.py
    tweet = expand_contractions(tweet, contraction_re)

    # Remove usernames and '#' from tweets
    tweet = re.sub(r'@\S+|#', '', tweet)

    # Replace '@' with at
    tweet = re.sub(r'\s@\s', ' at ', tweet)

    # Replace '&amp' or '&' with and
    tweet = re.sub(r'\s&amp\s', ' and ', tweet)
    tweet = re.sub(r'\s&\s', ' and ', tweet)

    # Remove all special characters
    tweet = re.sub(r'!|@|#|\$|%|\^|&|\*|\(|\)|_|~|\+', '', tweet).strip()

    sp = load_spacy()
    words = sp(tweet)
    # Remove urls
    words = [w for w in words if not w.like_url]

    # Remove digit tokens
    words = [w for w in words if not w.is_digit]

    # Remove punctuation
    words = [w for w in words if not w.is_punct]

    # Remove punctuation and lemmatize words
    words = [w.lemma_ for w in words]

    # Remove spaces
    words = [w for w in words if w != ' ']

    # Remove urls if they didn't get removed earlier
    words = [w for w in words if not w.startswith('http')]

    words = ' '.join(words)

    return words


def tweet_preprocessor_add_pos(tweet: str) -> str:
    """
    Removes numbers, words that start with @, links, and words less than 2 characters
    :param tweet:
    :return:
    """
    # Lowercase
    tweet = tweet.lower()

    # Replace '’' with "'"
    tweet = re.sub(r"’", "'", tweet)

    # Expand contractions.py
    tweet = expand_contractions(tweet, contraction_re)

    # Remove usernames and '#' from tweets
    tweet = re.sub(r'@\S+|#', '', tweet)

    # Replace '@' with at
    tweet = re.sub(r'\s@\s', ' at ', tweet)

    # Replace '&amp' or '&' with and
    tweet = re.sub(r'\s&amp\s', ' and ', tweet)
    tweet = re.sub(r'\s&\s', ' and ', tweet)

    # Remove all special characters
    tweet = re.sub(r'!|@|#|\$|%|\^|&|\*|\(|\)|_|~|\+', '', tweet).strip()

    sp = load_spacy()
    words = sp(tweet)
    # Remove urls
    words = [w for w in words if not w.like_url]

    # Remove digit tokens
    words = [w for w in words if not w.is_digit]

    # Remove punctuation
    words = [w for w in words if not w.is_punct]

    # Add pos tagging and remove punctuation
    words = [f'{w.lemma_} {w.pos_}' for w in words]

    # Remove spaces
    words = [w for w in words if w != ' ']

    # Remove urls if they didn't get removed earlier
    words = [w for w in words if not w.startswith('http')]

    words = ' '.join(words)

    return words


# text = "@john_cat hello, hadn’t last night I saw a coyote eating 3 squirrels. &amp !@# @ It### ~!@#$%^&*()_+ was HUGE and I saw blood everywhere 2day. Check it out here http:1232_photo.png"
# print(tweet_preprocessor(text))
