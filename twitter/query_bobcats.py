from utility.save_query_to_cvs import *
from utility.get_twitter import *


def main():
    """
    Run this program at least once a week. This will query the tweets from the past 7 days from LA
    and San Diego and save them into a csv. It will also be added to the csv with all entries.
    :return: None
    """
    irrelevant_words = ['sports', 'Charlotte']

    api = authenticate('/Users/Isaacbolo/Licenses/twitter.csv')
    query = f'bobcat OR bobcats OR (mountain lion) OR (mountain lions) -{" -".join(irrelevant_words)} -is:retweet'

    # --- LA ---
    df_la = query_in_df(api, query=query, coordinates=LA_coords, radius='50mi', max_tweets=500)
    df_la = normalize_df(df_la)
    df_la = add_classification_to_df(df_la, model_path='bobcats/bayes_model/bayes_pipeline.pkl')
    df_la = add_sentiment_to_df(df_la)
    save_query(df_la, add_to_main=True, name='la', path_to_main='bobcats/data/all_queries.csv', dir='bobcats')

    # --- SD ---
    df_sd = query_in_df(api, query=query, coordinates=SD_coords, radius='50mi', max_tweets=500)
    df_sd = normalize_df(df_sd)
    df_sd = add_classification_to_df(df_sd, model_path='bobcats/bayes_model/bayes_pipeline.pkl')
    df_sd = add_sentiment_to_df(df_sd)
    save_query(df_sd, add_to_main=True, name='sd', path_to_main='bobcats/data/all_queries.csv', dir='bobcats')

    # --- SF ---
    df_sf = query_in_df(api, query=query, coordinates=SF_coords, radius='50mi', max_tweets=500)
    df_sf = normalize_df(df_sf)
    df_sf = add_classification_to_df(df_sf, model_path='bobcats/bayes_model/bayes_pipeline.pkl')
    df_sf = add_sentiment_to_df(df_sf)
    save_query(df_sf, add_to_main=True, name='sf', path_to_main='bobcats/data/all_queries.csv', dir='bobcats')


if __name__ == "__main__":
    main()
