import pandas as pd

import get_twitter as gt
import pagination_new as new_page
import tweepy
import json
from math import inf
import time
import os


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
                           return_type='response',  # Returns python dictionary instead of response object
                           wait_on_rate_limit=wait_on_rate_limit)  # Whether to wait when rate limit is reached
    return client


def query_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


def coyote_query_string(coords: list) -> str:
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
    num_tweets = 0
    info = {
        'tweets': {},
        'users': {},
        'places': {}
    }

    for page_idx, p in enumerate(pages):
        time.sleep(1.1)
        result_count = p.meta['result_count']
        print(f'Page {page_idx}: {result_count} tweets')
        num_tweets += p.meta['result_count']
        if result_count == 0:
            continue

        if p.data is not None:
            for data in p.data:
                tweet_id = data['id']
                info['tweets'][tweet_id] = data.data

        if 'users' in p.includes:
            for user in p.includes['users']:
                user_id = user['id']
                info['users'][user_id] = user.data

        if 'places' in p.includes:
            for place in p.includes['places']:
                place_id = place['id']
                info['places'][place_id] = place.data

    return info

    # results = [p for p in pages]
    # info = {}
    # if len(results) == 0:
    #     return {}
    # return info

    # tweet_info = results[:-1]
    # response = results[-1]
    # info['tweets'] = {str(tweet.data['id']): tweet.data for tweet in tweet_info}
    # info['users'] = {str(user.data['id']): user.data for user in response.includes['users']}
    # if 'places' in response.includes:
    #     info['places'] = {str(place.data['id']): place.data for place in response.includes['places']}

    # user_info = results[-2]
    # place_info = results[-1]
    # print(user_info)

    # info = {
    #     'data': {str(tweet.data['id']): tweet.data for tweet in tweet_info},
    #     'users': {str(user.data['id']): user.data for user in user_info},
    #     'places': {str(place.data['id']): place.data for place in place_info}
    # }

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
    tweet_fields = ['created_at', 'attachments', 'author_id', 'conversation_id', 'geo', 'lang', 'possibly_sensitive',
                    'public_metrics']
    user_fields = ['created_at', 'description', 'entities', 'location', 'public_metrics', 'protected',
                   'profile_image_url', 'pinned_tweet_id', 'verified']
    time.sleep(1)
    p = tweepy.Paginator(
        client.search_all_tweets,
        query=query,
        tweet_fields=tweet_fields,
        expansions=['geo.place_id', 'author_id'],
        place_fields=place_fields,
        user_fields=user_fields,
        max_results=500,
        start_time=start_time,
        end_time=end_time
    )

    # p = new_page.Paginator2(
    #     client.search_all_tweets,
    #     query=query,
    #     tweet_fields=tweet_fields,
    #     expansions=['geo.place_id', 'author_id'],
    #     place_fields=place_fields,
    #     user_fields=user_fields,
    #     max_results=500,
    #     start_time=start_time,
    #     end_time=end_time
    # ).flatten(limit)

    data = format_response(p)

    return data


def paginator(client, geopolygon, start_time=None, end_time=None, max_tweets=100, dir_path=None, grid_id=None):
    """
    Returns dictionary with num_tweets number of tweets
    :param grid_id:
    :param dir_path:
    :param max_tweets:
    :param geopolygon: list with coordinates: [west_long south_lat east_long north_lat]
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
    data['grid_id'] = grid_id

    if None not in (dir_path, data, grid_id):
        # Saving data
        create_dir(dir_path)
        file_path = create_file_path(grid_id)
        path = f'{dir_path}/{file_path}'
        query_to_json(data, path)

    return data


def create_file_path(grid_id):
    # Creates a file path in the form "grid_{grid_id}.json"
    return f'grid_{grid_id}.json'


def create_dir(dir_path):
    # Check if directory exists. If it doesn't create it.
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def load_coords(filepath, get_county=None):
    # Returns array in formate [(grid_id, coordinates)]
    df = pd.read_csv(filepath)
    if get_county:
        df = df[df['county'] == get_county]
    col_format = ['id', 'xmin', 'ymin', 'xmax', 'ymax']
    df = df.drop(columns=[col for col in df.columns.values if col not in col_format])
    df = df.reindex(columns=col_format)
    data = df.to_numpy()
    id_coord_pairs = [(str(int(row[0])), list(row[1:])) for row in data]
    return id_coord_pairs


paginator_sleep_time = 1.5
if __name__ == '__main__':
    time_start = time.time()
    # client = authenticate_research('/home/ec2-user/twitter_research.csv', True)
    client = authenticate_research('/Users/Isaacbolo/Licenses/twitter_research.csv', True)
    start_time = '2010-01-01T00:00:00Z'
    end_time = '2022-03-02T00:00:00Z'
#    county = 'LOS ANGELES'

    county = None
    id_coords_pairs = load_coords('../coyotes/geo_grid/R_code_from_Brett/grid_out.csv',
                                  county)

    i = 0
#     i = 3798
    # iters = 0
    error_attempts = 0

    print(f'Searching from {start_time} to {end_time}')
    print('------------')
    # missing_grids = [3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3480, 3481, 3482, 3483, 3484, 3375, 3381, 3260, 3261, 3263, 3267, 3431, 3434, 3435, 3691, 1774, 3316, 3317, 3318]
    # for i in missing_grids:
    while i < len(id_coords_pairs):
    # while i < len(missing_grids):
        try:
            # grid = missing_grids[i]
            current_id = id_coords_pairs[i][0]
            coords = id_coords_pairs[i][1]

            # for grid_id, coords in id_coords_pairs:
            #     current_id = grid_id
            print('grid_id', current_id)
            time.sleep(1)
            try:
                results = paginator(client,
                                    coords,
                                        start_time,
                                    end_time,
                                        inf,
                                    '../coyotes/data/grid_data',
                                    current_id)
                count = 0
                if 'tweets' in results:
                    count = len(results['tweets'])
                    print(f'Found {count} tweets')
                    i += 1
                    error_attempts = 0
            except tweepy.errors.TwitterServerError as e:
                print(f'503 Error, restarting at grid_id {current_id}')
                print(e)
                time.sleep(3)
                error_attempts += 1
                paginator_sleep_time += 0.15
                if error_attempts == 20:
                        # After 20 errors on the same grid_id move on to the next grid_id
                    i += 1
                    print('Error attempts reached. Skipping grid_id', current_id)
                    continue

            print('------------')
        except Exception as e:
            print(e)
            continue
    print('time', time.time() - time_start)

