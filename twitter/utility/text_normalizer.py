import spacy
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.classes.tokenizer import SocialTokenizer
from ekphrasis.dicts.emoticons import emoticons
from ekphrasis.classes.spellcorrect import SpellCorrector


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
ekp = None
spellcheck = None
lem = None
sw = None
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


def tweet_preprocessor(tweet: str, lowercase=False) -> str:
    """
    Removes numbers, words that start with @, links, and words less than 2 characters
    :param lowercase:
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

    # Remove new lines
    tweet = tweet.replace('\n', ' ')

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
    words = [w for w in words if ' ' not in w]

    # Remove urls if they didn't get removed earlier
    words = [w for w in words if not w.startswith('http')]

    words = ' '.join(words)

    if lowercase:
        return words.lower()
    return words


def tweet_preprocessor_lowercased(tweet):
    return tweet_preprocessor(tweet, True)


def load_preprocessor():
    global ekp
    if ekp is None:
        ekp = TextPreProcessor(
            normalize=['url', 'email', 'percent', 'money', 'phone', 'user',
                       'time', 'url', 'date', 'number'],
            segmenter='twitter',
            corrector='twitter',
            unpack_hashtags=True,
            unpack_contractions=True,
            spell_correction=True,
            spell_correct_elong=True,
            tokenizer=SocialTokenizer(lowercase=True).tokenize,
            dicts=[emoticons],
            remove_tags=True
        )
    return ekp


def load_spellcheck():
    global spellcheck
    if spellcheck is None:
        spellcheck = SpellCorrector(corpus='twitter')
    return spellcheck


def load_lem():
    global lem
    if lem is None:
        lem = WordNetLemmatizer()
    return lem


def load_stopwords():
    global sw
    if sw is None:
        sw = set(stopwords.words('english'))
    return sw


def tweet_preprocessor2(tweet):
    # Remove usernames and '#' from tweets
    # tweet = re.sub(r'@\S+|#', '', tweet)
    # Replace '@' with at
    tweet = re.sub(r'\s@\s', ' at ', tweet)
    # Replace '&amp' or '&' with 'and'
    tweet = re.sub(r'\s&amp\s', ' and ', tweet)
    tweet = re.sub(r'\s&\s', ' and ', tweet)

    # Run tweet through tweet preprocessor and tokenize words
    text_preprocessor = load_preprocessor()
    tweet = text_preprocessor.pre_process_doc(tweet)

    # Remove punctuation and spell check
    punctuation= '''!()-[]{};:'"\<=>,./?@#$%^&*_~'''
    # sp = load_spellcheck()
    # tweet = [sp.correct(w) if (not w.startswith('<') or not w.endswith('>')) else w for w in tweet]
    # tweet = [sp.correct(w) for w in tweet]
    tweet = [w for w in tweet if w.isalnum()]
    tweet = [w for w in tweet if w not in punctuation]

    # Lemmatize and remove stop words
    lem = load_lem()
    # sw = load_stopwords()
    # tweet = [lem.lemmatize(w) for w in tweet if w not in sw]
    tweet = [lem.lemmatize(w) for w in tweet]

    return ' '.join(tweet)


def simple_tokenizer(tweet):
    return tweet.split(' ')

#
# text = '''@phoenixcoyotes. Nicccce starting the 3rd with the Power Play!!
#
# I beileved in us.
#
# Cash in COYOTES #runaway https://www.atttt.com'''
# a = tweet_preprocessor2(text)
# b = tweet_preprocessor(text)
# print(b)
# print(simple_tokenizer(b))
# # print(b)
# # a = a.split(' ')
# # print(a)
