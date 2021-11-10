import pandas as pd
from get_twitter import *
from datetime import datetime
from classify_tweets import *
from sentiment import *


LA_coords = '34.052235,-118.243683'
SD_coords = '32.715736,-117.161087'
irrelevant_words = ['ugly', 'having', 'drugs', 'movie', 'team', 'halloween', 'season', 'hawks',
                    'predictions', 'sports', 'restaurant', 'soccer', 'basketball', 'tennis', 'ball']


def load_full_df() -> pd.DataFrame:
    df_full = pd.read_csv('data/all_queries.csv')
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


def join_dfs(df1, df2) -> pd.DataFrame:
    """
    Stacks two dataframes and remove duplicate rows
    :param df1:
    :param df2:
    :return: df
    """
    df_joined = pd.concat([df1, df2], axis=0)
    df_joined = df_joined.reset_index(drop=True)
    df_joined = df_joined.drop_duplicates(subset=['tweet_id'])
    return df_joined


def save_query(df_today: pd.DataFrame, add_to_main=False) -> None:
    """
    Save the given dataframe to a csv file in the format `query_YEAR-MONTH-DAY_HOUR:MINUTE.csv`.
    If add_to_main is True, the given dataframe with be joined with the dataframe containing all tweets.
    :param df_today:
    :param add_to_main:
    :return: None
    """
    date_and_time = datetime.now().strftime('%Y-%m-%d_%H:%M')
    df_today.to_csv(f'data/query_{date_and_time}.csv', index=False, encoding='utf-8-sig')
    if add_to_main:
        df_main = load_full_df()
        df_joined = join_dfs(df_main, df_today)
        df_joined.to_csv('data/all_queries.csv', index=False, encoding='utf-8-sig')
        print(f'{df_joined.shape[0] - df_main.shape[0]} tweets added')


def add_classification_to_df(df) -> pd.DataFrame:
    """
    Add relevant column to dataframe that has been passed through normalized_df()
    :param df:
    :return: df with 'relevant' column
    """
    tweets = df['tweet']
    classification_values = classify_tweets(tweets)
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


def main():
    """
    Run this program at least once a week. This will query the tweets from the past 7 days from LA
    and San Diego and save them into a csv. It will also be added to the csv with all entries.
    :return: None
    """
    api = authenticate('/Users/Isaacbolo/Licenses/twitter.csv')
    query = f'coyotes OR coyotes -{" -".join(irrelevant_words)} -is:retweet -is:reply'
    df_la = query_in_df(api, query=query, coordinates=LA_coords, radius='50mi', max_tweets=500)
    df_sd = query_in_df(api, query=query, coordinates=SD_coords, radius='50mi', max_tweets=500)
    df_la = normalize_df(df_la)
    df_sd = normalize_df(df_sd)
    df_both = join_dfs(df_la, df_sd)
    df_both_classified = add_classification_to_df(df_both)
    df_both_classified_sent = add_sentiment_to_df(df_both_classified)
    save_query(df_both_classified_sent, add_to_main=True)


if __name__ == "__main__":
    main()
