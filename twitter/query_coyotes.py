from utility.save_query_to_cvs import *
from utility.get_twitter import *


def new_query(api, query, coords, location, model_path, directory, all_queries_path):
    df = query_in_df(api, query=query, coordinates=coords, radius='50mi', max_tweets=500)
    if df.shape[0] == 0:
        print(f'No tweets found in {location} query')
        return
    df = normalize_df(df)
    df = add_classification_to_df(df, model_path)
    df = add_sentiment_to_df(df)
    save_query(df, name=location, add_to_main=True, path_to_main=all_queries_path, dir=directory)


def main():
    """
    Run this program at least once a week. This will query the tweets from the past 7 days from LA
    and San Diego and save them into a csv. It will also be added to the csv with all entries.
    :return: None
    """
    irrelevant_words = ['ugly', 'drugs', 'movie', 'team', 'halloween', 'season', 'hawks',
                        'predictions', 'sports', 'restaurant', 'soccer', 'basketball', 'tennis', 'ball',
                        'indian', 'ducks', 'game', 'school', 'arizona', 'nhl', 'win']

    api = authenticate('/Users/Isaacbolo/Licenses/twitter.csv')
    all_queries_path = 'coyotes/data/all_queries.csv'
    # query = f'coyotes OR coyote -{" -".join(irrelevant_words)} -is:retweet'
    query = f'coyotes OR coyote -is:retweet'
    model_path = 'coyotes/bayes_model/best_bayes_pipeline.pkl'

    # --- LA ---
    new_query(api, query, LA_coords, 'la', model_path, 'coyotes', all_queries_path)
    # # --- SD ---
    new_query(api, query, SD_coords, 'sd', model_path, 'coyotes', all_queries_path)
    # # --- SF ---
    new_query(api, query, SF_coords, 'sf', model_path, 'coyotes', all_queries_path)
    # --- Redding ---
    new_query(api, query, REDD_coords, 'redding', model_path, 'coyotes', all_queries_path)
    # --- Sacramento ---
    new_query(api, query, SAC_coords, 'sac', model_path, 'coyotes', all_queries_path)
    # --- Fresno ---
    new_query(api, query, FRES_coords, 'fresno', model_path, 'coyotes', all_queries_path)


if __name__ == "__main__":
    main()
