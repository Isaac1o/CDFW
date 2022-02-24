import get_twitter as gt
import tweepy
import json


def authenticate_research(research_auth_filename):
    """
    Return twitter Client object for research license
    """
    consumer_key, consumer_secret, access_token, access_token_secret, bearer = gt.loadkeys(research_auth_filename)
    client = tweepy.Client(bearer_token=bearer,
                           consumer_key=consumer_key,
                           consumer_secret=consumer_secret,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           # return_type=dict,         # Returns python dictionary instead of response object
                           wait_on_rate_limit=True)  # Whether to wait when rate limit is reached
    return client


def query_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


def format_response(response):
    """
    Formats response object into a dictionary with 3 keys: data, user, places.
    - data is a dictionary with {tweet_id: tweet_data}
    - users is a dictionary with {user_id: user_data}
    - places is a dictionary with {place_id: place_data}
    :param response: response object returned from twitter api
    :return:
    """
    info = {
        'data': {str(data['id']): data.data for data in response.data},
        'users': {str(user['id']): user.data for user in response.includes['users']},
        'places': {str(place['id']): place.data for place in response.includes['places']}
    }

    return info


def search_twitter(client, query, next_token=None, start_time=None, end_time=None, max_results=500):
    """
    Queries one page and returns the next token and data in a dictionary.
    :param next_token: Token for next page
    :param client:
    :param query:
    :param start_time:
    :param end_time:
    :param max_results
    :return: data, next_token, num_tweets
    """
    place_fields = ['full_name', 'country_code', 'geo', 'contained_within', 'country', 'name', 'place_type']
    tweet_fields = ['created_at', 'attachments', 'author_id', 'conversation_id', 'geo', 'lang', 'possibly_sensitive', 'public_metrics']
    user_fields = ['created_at', 'description', 'entities', 'location', 'public_metrics', 'protected', 'profile_image_url', 'pinned_tweet_id', 'verified']
    response = client.search_all_tweets(
        query,
        tweet_fields=tweet_fields,
        expansions=['geo.place_id', 'author_id'],
        place_fields=place_fields,
        user_fields=user_fields,
        max_results=max_results,
        start_time=start_time,
        end_time=end_time,
        next_token=next_token
    )
    data = format_response(response)

    return data, response.meta['next_token'], response.meta['result_count']


def paginator(client, query, start_time=None, end_time=None, num_tweets=100, file_path=None):
    """
    Returns dictionary with num_tweets number of tweets
    :param file_path:
    :param client:
    :param query:
    :param start_time:
    :param end_time:
    :param num_tweets:
    :return:
    """
    max_results = 500
    count = 0
    next_token = None
    if num_tweets < max_results:
        max_results = num_tweets
    while count < num_tweets:
        data, next_token, result_count = search_twitter(
            client,
            query,
            next_token=next_token,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results
        )




# client = authenticate_research('/Users/Isaacbolo/Licenses/twitter_research.csv')
# d = search_twitter(client, 'dog has:geo', max_results=10)
# query_to_json(d, '/tmp/test_json.json')

















