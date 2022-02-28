import utility.get_twitter as gt
import utility.pagination_new as new_page
import tweepy
import json
from math import inf
import time


def authenticate_research(research_auth_filename, wait_on_rate_limit=False):
    """
    Return twitter Client object for research license
    """
    consumer_key, consumer_secret, access_token, access_token_secret, bearer = gt.loadkeys(research_auth_filename)
    client = tweepy.Client(bearer_token=bearer,
                           consumer_key=consumer_key,
                           consumer_secret=consumer_secret,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           return_type='response',         # Returns python dictionary instead of response object
                           wait_on_rate_limit=wait_on_rate_limit)  # Whether to wait when rate limit is reached
    return client


def query_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


def coyote_query_string(coords:list) -> str:
    # Contructs the query that searches a geo-polygon.
    # The geopolygon is queried using "bounding_box:[west_long south_lat east_long north_lat]"
    # `coords` is a list in the form [west_long, south_lat, east_long, north_lat]
    query = f'(coyotes OR coyote -is:retweet -is:reply has:geo lang:en) (bounding_box:[{coords[0]} {coords[1]} {coords[2]} {coords[3]}])'
    return query


def format_response(pages):
    """
    Formats response object into a dictionary with 3 keys: data, user, places.
    - data is a dictionary with {tweet_id: tweet_data}
    - users is a dictionary with {user_id: user_data}
    - places is a dictionary with {place_id: place_data}

    :return:
    """
    results = []
    for p in pages:
        results.append(p)
    # print(results)

    if len(results) < 3:
        return None

    tweet_info = results[:-2]
    user_info = results[-2]
    place_info = results[-1]
    # print(user_info)

    info = {
        'data': {str(tweet.data['id']): tweet.data for tweet in tweet_info},
        'users': {str(user.data['id']): user.data for user in user_info},
        'places': {str(place.data['id']): place.data for place in place_info}
    }

    return info


def search_twitter(client, query, start_time=None, end_time=None, limit=inf):
    """
    Queries one page and returns the next token and data in a dictionary.
    :param limit: Total number of tweets to return
    :param client:
    :param query:
    :param start_time:
    :param end_time:
    :return: data, next_token, num_tweets
    """
    place_fields = ['full_name', 'country_code', 'geo', 'contained_within', 'country', 'name', 'place_type']
    tweet_fields = ['created_at', 'attachments', 'author_id', 'conversation_id', 'geo', 'lang', 'possibly_sensitive', 'public_metrics']
    user_fields = ['created_at', 'description', 'entities', 'location', 'public_metrics', 'protected', 'profile_image_url', 'pinned_tweet_id', 'verified']
    time.sleep(1)
    p = new_page.Paginator2(
        client.search_all_tweets,
        query=query,
        tweet_fields=tweet_fields,
        expansions=['geo.place_id', 'author_id'],
        place_fields=place_fields,
        user_fields=user_fields,
        max_results=500,
        start_time=start_time,
        end_time=end_time
    ).flatten(100)

    data = format_response(p)

    return data


def paginator(client, geopolygon, start_time=None, end_time=None, max_tweets=100, file_path=None):
    """
    Returns dictionary with num_tweets number of tweets
    :param max_tweets:
    :param geopolygon: list with coordinates: [west_long south_lat east_long north_lat]
    :param file_path:
    :param client:
    :param start_time:
    :param end_time:
    :return:
    """
    query = coyote_query_string(geopolygon)

    data = search_twitter(
        client,
        query,
        start_time=start_time,
        end_time=end_time,
        limit=max_tweets
    )

    if file_path and data is not None:
        query_to_json(data, file_path)

    return data
