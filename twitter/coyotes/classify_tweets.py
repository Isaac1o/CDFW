# from text_normalizer import normalize_tweet
import joblib
import numpy as np


bayes_model = None


def load_model():
    global bayes_model
    if bayes_model is None:
        bayes_model = joblib.load('bayes_model/bayes_pipeline.pkl')

    return bayes_model


def classify_tweets(tweets: list) -> np.ndarray:
    """
    Given a list of tweets, return an array with the binary classifications
    1 for relevant, 0 for not relevant for all tweets.
    :param tweets:
    :return:
    """
    model = load_model()
    classification_array = model.predict(tweets)
    return np.array(classification_array)


# tweets = ['Yesterday I saw a cow run on the freeway',
#           'Last night there were coyotes howling like nuts!',
#           '@coyote_hunter Why do you like nachos so much?',
#           'Keep you pets inside. Coyotes are out tonight',
#           'Lets go Coyotes!!! Reclaim your championship title!']
#
# print(classify_tweets(tweets))
