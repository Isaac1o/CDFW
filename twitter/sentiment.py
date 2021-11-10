from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


vader = None


def create_vader():
    global vader
    if vader is None:
        vader = SentimentIntensityAnalyzer()
    return vader


def score_tweet(tweet: str) -> list:
    """
    Given tweet return a list containing:
    [negative_score, neutral_score, positive_score, compound_score, sentiment_classification]
    :param tweet:
    :return:
    """
    sid = create_vader()
    score = sid.polarity_scores(tweet)
    neg = score['neg']
    neu = score['neu']
    pos = score['pos']
    compound = score['compound']

    # Cut offs based on vaderSentiment documentation
    if compound >= 0.05:
        sent_class = 'positive'
    elif compound <= - 0.05:
        sent_class = 'negative'
    else:
        sent_class = 'neutral'

    return [neg, neu, pos, compound, sent_class]

