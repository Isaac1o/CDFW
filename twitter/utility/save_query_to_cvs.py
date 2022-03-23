import os

import pandas as pd
import json
from datetime import datetime

from utility.get_twitter import *
from datetime import datetime
from utility.classify_tweets import *
from utility.sentiment import *


LA_coords = '34.052235,-118.243683'
SD_coords = '32.715736,-117.161087'
SF_coords = '37.7749,-122.4194'
REDD_coords = '40.585040,-122.361139'
SAC_coords = '38.592792,-121.480819'
FRES_coords = '36.767301,-119.788392'


def load_full_df(path_to_data) -> pd.DataFrame:
    df_full = pd.read_csv(path_to_data)
    return df_full


def normalize_df(df) -> pd.DataFrame:
    """
    Create two new columns: date and time, and remove the `created` column.
    Rearrange the columns so date and time are the first two columns respectively
    :param df: Dataframe from query_in_df()
    :return: df
    """
    df['date'] = df['created'].dt.date
    df['time'] = df['created'].dt.time
    df.drop(columns=['created'], axis=1, inplace=True)
    df = df[['date', 'time'] + [c for c in df.columns.values if c not in ['date', 'time']]]
    return df


def add_location_column(df, location:str):
    df['query_location'] = location


def join_dfs(df1, df2) -> pd.DataFrame:
    """
    Stacks two dataframes and remove duplicate rows
    :param df1:
    :param df2:
    :return: df
    """
    df_joined = pd.concat([df1, df2], axis=0)
    df_joined = df_joined.reset_index(drop=True)
    df_joined = df_joined.drop_duplicates(subset=['tweet'])
    return df_joined


def save_query(df_today: pd.DataFrame, name, dir, add_to_main=False, path_to_main=None) -> None:
    """
    Save the given dataframe to a csv file in the format `query_YEAR-MONTH-DAY_HOUR:MINUTE.csv`.
    If add_to_main is True, the given dataframe with be joined with the dataframe containing all tweets.
    :param name:
    :param path_to_main: Path to csv with all the tweets
    :param df_today:
    :param add_to_main:
    :return: None
    """
    date_and_time = datetime.now().strftime('%Y-%m-%d_%H:%M')
    print(f'{name}: saving {df_today.shape[0]} tweets')
    df_today.to_csv(f'{dir}/data/{name}/query_{name}_{date_and_time}.csv', index=False, encoding='utf-8-sig')

    # Add query to all queries for specific location
    try:
        df_name = pd.read_csv(f'{dir}/data/{name}/all_queries_{name}.csv')
    except Exception as e:
        print(e)
        print(f'Main CSV for {name} does not exist, attempting to create it')
        df_name = df_today

    df_name_full = join_dfs(df_name, df_today)
    df_name_full.to_csv(f'{dir}/data/{name}/all_queries_{name}.csv', index=False, encoding='utf-8-sig')
    print(f'{name}: {df_name_full.shape[0] - df_name.shape[0]} tweets added to {name} main csv')

    if add_to_main:
        try:
            df_main = load_full_df(path_to_main)
            df_joined = join_dfs(df_main, df_today)
            df_joined.to_csv(path_to_main, index=False, encoding='utf-8-sig')
            print(f'{name}: {df_joined.shape[0] - df_main.shape[0]} tweets added to main csv')
        except Exception as e:
            print(e)
            print('Path to data not included')


def add_classification_to_df(df, model_path) -> pd.DataFrame:
    """
    Add relevant column to dataframe that has been passed through normalized_df()
    :param df:
    :return: df with 'relevant' column
    """
    tweets = df['tweet']
    classification_values = classify_tweets(tweets, model_path)
    df['relevant'] = classification_values

    return df


def add_sentiment_to_df(df) -> pd.DataFrame:
    """
    Add five columns consisting of sentiment data:
    - negative_sent_score
    - neutral_sent_score
    - positive_sent_score
    - compound_sent_score
    - sent_classification
    :param df:
    :return:
    """
    tweets = df['tweet']
    sentiment_values = [score_tweet(tweet) for tweet in tweets]
    df_sent = pd.DataFrame.from_records(sentiment_values)
    df = pd.concat([df, df_sent], axis=1)

    return df


def parse_json(filename):
    """
    Given a json file queried from get_twitter_research.py, parse tweet text, grid_id, tweet_id,
    author_id, created_at, full_name, place_type, place_id.
    :param filename:
    :return:
    """
    with open(filename, 'r') as f:
        content = f.read()
        data = json.loads(content)

    if len(data['tweets']) == 0:
        # return empty df if there is no data

        return pd.DataFrame(data={
            'grid_id': int(data['grid_id']),
            'tweet_id': None,
            'created_at': None,
            'text': None,
            'author_id': None,
            'place_id': None,
            'lat': None,
            'long': None,
            'full_name': None,
            'name': None,
            'place_type': None
        }, index=[0])

    records = []
    for tweet_id in data['tweets'].keys():
        tweet_data = data['tweets'][tweet_id]
        record = {}
        record['grid_id'] = int(data['grid_id'])
        record['tweet_id'] = str(tweet_id)
        record['created_at'] = datetime.strptime(tweet_data['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
        record['text'] = tweet_data['text']
        record['author_id'] = str(tweet_data['author_id'])
        # record['place_id'] = tweet_data.get('geo', None).get('place_id', None)
        geo_info = tweet_data.get('geo', None)
        if geo_info and len(geo_info) > 0:
            record['place_id'] = geo_info.get('place_id', None)
            if record['place_id']:
                str(record['place_id'])
            coords = geo_info.get('coordinates', None)
            if coords:
                record['lat'] = coords['coordinates'][0]
                record['long'] = coords['coordinates'][1]
            else:
                record['lat'] = None
                record['long'] = None

            if record['place_id'] and record['place_id'] in data['places'].keys():
                try:
                    record['full_name'] = data['places'][record['place_id']]['full_name']
                except:
                    print(data)
                record['name'] = data['places'][record['place_id']]['name']
                record['place_type'] = data['places'][record['place_id']]['place_type']
            else:
                record['full_name'] = None
                record['name'] = None
                record['place_type'] = None
        else:
            record['lat'] = None
            record['long'] = None
            record['full_name'] = None
            record['name'] = None
            record['place_type'] = None

        records.append(record)

    return pd.DataFrame.from_records(records)


def combine_records(dir_path):
    df = pd.DataFrame()
    for filename in os.listdir(dir_path):
        if filename.endswith('.json'):
            path = os.path.join(dir_path, filename)
            df_ = parse_json(path)
            df = pd.concat([df, df_], axis=0)
    return df.sort_values('grid_id').reset_index(drop=True)


if __name__ == '__main__':
    # pd.set_option('display.max_columns', None)
    # df = parse_json('../coyotes/data/grid_data/grid_1355.json')
    # print(df)
    p = '../coyotes/data/grid_data'
    df1 = combine_records(p)
    df1.to_parquet('coyote_tweets2.gzip', index=None)
