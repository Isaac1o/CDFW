import tweepy
from typing import List
import pandas as pd


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with format
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        keys = f.readlines()[1].strip().split(',')

    return keys


def authenticate(twitter_auth_filename):
    """
    Given a CSV file containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    consumer_key, consumer_secret, access_token, access_token_secret = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def authenticate_research(research_auth_filename):
    """
    Return twitter api object for research license
    """
    consumer_key, consumer_secret, access_token, access_token_secret, bearer = loadkeys(research_auth_filename)
    client = tweepy.Client(bearer_token=bearer,
                           consumer_key=consumer_key,
                           consumer_secret=consumer_secret,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           return_type=dict,         # Returns python dictionary instead of response object
                           wait_on_rate_limit=True)  # Whether to wait when rate limit is reached
    return client


def create_df(searched_tweets: List[dict]) -> pd.DataFrame:
    """
    Given list of dictionaries, where each dictionary is information from one tweet. Return a dataframe
    where each row is a tweet.
    :param searched_tweets:
    :return: Dataframe
    """
    return pd.DataFrame.from_records(searched_tweets)


def process_status(status) -> dict:
    """
    Parse select information from the given tweet (status).
    :param status: Tweet in JSON that the twitter api returns
    :return: dictionary containing wanted info from tweet
    """
    status_info = {'created': status.created_at,
                   'tweet': status.full_text,
                   'tweet_id': str(status.id),  # convert to string so excel doesn't convert to exponential
                   'hashtags': [hashtag['text'] for hashtag in status.entities['hashtags']],
                   'user_id': str(status.user.id),  # convert to string so excel doesn't convert to exponential
                   'username': status.user.screen_name,
                   'location': status.user.location,
                   'num_followers': status.user.followers_count,
                   'geo_enabled': status.user.geo_enabled}
    if status.coordinates:
        status_info['long'] = status.coordinates['coordinates'][0]
        status_info['lat'] = status.coordinates['coordinates'][1]
    else:
        status_info['long'] = None
        status_info['lat'] = None

    return status_info


def get_location_id(api, location, granularity='city'):
    """
    Get the id of parameter: location.
    Function currently not being used
    :param api:
    :param location:
    :param granularity:
    :return:
    """
    places = api.search_geo(query=location, granularity=granularity)
    place_id = places[0].id
    return place_id


def query_tweets(api, query, geocode=None, max_tweets=15) -> List[dict]:
    """
    Get all the tweets from the given query and geocode. Process each tweet (status) and
    append them to a list.
    :param api: twitter api object
    :param query: query to search
    :param geocode: area that tweet will be pulled from. The format is "lat,long,radius". ie "34.052235,-118.243683,50mi"
    :param max_tweets: maximum number of tweets
    :return: list of dictionaries, where each dictionary represents the information from one tweet
    """
    searched_tweets = [process_status(status) for status in tweepy.Cursor(api.search_tweets,
                                                                          q=query,
                                                                          geocode=geocode,
                                                                          lang='en',
                                                                          tweet_mode='extended'
                                                                          ).items(max_tweets)]

    return searched_tweets


def get_geocode_of_location(api, location, radius='30mi', search_type='neighborhood') -> str:
    """
    Returns the geocode for query_tweets() geocode parameter.
    :param api: twitter api object
    :param location: area to get geocode
    :param radius: search radius of location
    :param search_type: possible arguments for granularity are neighborhood, city, or country.
    :return: String in the format, "lat,long,radius"
    """
    query_result = api.search_geo(query=location, granularity=search_type)
    top_results = [result for result in query_result if location in result.name or location in result.full_name]
    if len(top_results) == 0:
        return None
    long, lat = top_results[0].centroid
    geocode = f'{str(lat)},{str(long)},{radius}'

    return geocode


def query_in_df(api,
                query,
                location=None,
                coordinates=None,
                radius='5mi',
                search_type='city',
                max_tweets=10) -> pd.DataFrame:
    """
    Searches for tweets with given query and puts the results in a dataframe.
    :param api: twitter api object
    :param query: query used to search for tweets
    :param location: location you want to search. ie. "San Francisco" or "Los Angeles"
    :param coordinates: coordinates of location in latitude and longitude
    :param radius: search radius from given coordinates or location. ie "50mi" or "30km"
    :param search_type: If location is given, specify the location is a "city", "country", or "neighborhood"
    :param max_tweets: Maximum number of tweets to return
    :return:
    """
    coords = None
    if location:
        coords = get_geocode_of_location(api, location, radius=radius, search_type=search_type)
    elif coordinates:
        coords = f'{coordinates},{radius}'
    query_results = query_tweets(api=api, query=query, geocode=coords, max_tweets=max_tweets)
    return create_df(query_results)
