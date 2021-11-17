from utility.save_query_to_cvs import *
from utility.get_twitter import *


# def main():
#     """
#     Run this program at least once a week. This will query the tweets from the past 7 days from LA
#     and San Diego and save them into a csv. It will also be added to the csv with all entries.
#     :return: None
#     """
#     irrelevant_words = ['ugly', 'having', 'drugs', 'movie', 'team', 'halloween', 'season', 'hawks',
#                         'predictions', 'sports', 'restaurant', 'soccer', 'basketball', 'tennis', 'ball',
#                         'indian', 'ducks', 'game', 'school', 'arizona', 'nhl', 'win']
#
#     api = authenticate('/Users/Isaacbolo/Licenses/twitter.csv')
#     query = f'coyotes OR coyotes -{" -".join(irrelevant_words)} -is:retweet -is:reply'
#     df_la = query_in_df(api, query=query, coordinates=LA_coords, radius='50mi', max_tweets=500)
#     df_sd = query_in_df(api, query=query, coordinates=SD_coords, radius='50mi', max_tweets=500)
#     df_sf = query_in_df(api, query=query, coordinates=SF_coords, radius='50mi', max_tweets=500)
#     df_la = normalize_df(df_la)
#     df_sd = normalize_df(df_sd)
#     df_sf = normalize_df(df_sf)
#     df_la = add_classification_to_df(df_la)
#     df_sd = add_classification_to_df(df_sd)
#     df_sf = add_classification_to_df(df_sf)
#     df_la = add_sentiment_to_df(df_la)
#     df_sd = add_sentiment_to_df(df_sd)
#     df_sf = add_sentiment_to_df(df_sf)
#     save_query(df_la, add_to_main=True, name='LA', main_dir='coyotes/data/all_queries.csv')
#     save_query(df_sd, add_to_main=True, name='SD', main_dir='coyotes/data/all_queries.csv')
#     save_query(df_sf, add_to_main=True, name='SF', main_dir='coyotes/data/all_queries.csv')
#
#
# if __name__ == "__main__":
#     main()


def main():
    """
    Run this program at least once a week. This will query the tweets from the past 7 days from LA
    and San Diego and save them into a csv. It will also be added to the csv with all entries.
    :return: None
    """
    irrelevant_words = ['ugly', 'having', 'drugs', 'movie', 'team', 'halloween', 'season', 'hawks',
                        'predictions', 'sports', 'restaurant', 'soccer', 'basketball', 'tennis', 'ball',
                        'indian', 'ducks', 'game', 'school', 'arizona', 'nhl', 'win']
    api = authenticate('/Users/Isaacbolo/Licenses/twitter.csv')
    all_queries_path = 'coyotes/data/all_queries.csv'
    query = f'coyotes OR coyotes -{" -".join(irrelevant_words)} -is:retweet -is:reply'
    model_path = 'coyotes/bayes_model/bayes_pipeline.pkl'

    df_la = query_in_df(api, query=query, coordinates=LA_coords, radius='50mi', max_tweets=500)
    df_la = normalize_df(df_la)
    df_la = add_classification_to_df(df_la, model_path)
    df_la = add_sentiment_to_df(df_la)
    save_query(df_la, name='la', add_to_main=True, path_to_main=all_queries_path)

    df_sd = query_in_df(api, query=query, coordinates=SD_coords, radius='50mi', max_tweets=500)
    df_sd = normalize_df(df_sd)
    df_sd = add_classification_to_df(df_sd, model_path)
    df_sd = add_sentiment_to_df(df_sd)
    save_query(df_sd, name='sd', add_to_main=True, path_to_main=all_queries_path)


if __name__ == "__main__":
    main()