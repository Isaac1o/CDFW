import pandas as pd
import numpy as np


def self_train(m, L, U, text_col, tar_col, proba_col, r=0.95, max_iter=5):
    """
    Given labeled, L, and unlabeled, U, data, expand the labeled data set by training the model on L.
    Use this model to predict on U and if the probability assigned is > the threshold, r, add it to U.
    Repeat this process until there are no more confident predictions.
    :param model: Model used to predict on U
    :param L: Labeled data
    :param U: Unlabeled data
    :param text_col: Column with text
    :param proba_col: Column with probability of 1
    :param r: Probability threshold
    :return: L, expanded labeled dataset
    """
    num_confident = 1e10
    i = 1
    while num_confident > 0 or i <= max_iter:
        print(f'-----Iteration {i}-----')
        print(f'Training on {L.shape[0]} observations')
        m.fit(L[text_col], L[tar_col])

        print(f'Predicting labels for {U.shape[0]} observations')
        U[tar_col] = m.predict(U[text_col])

        print(f'Predicting probabilities for {U.shape[0]} observations')
        U[proba_col] = m.predict_proba(U[text_col])[:, 1]

        confident_preds = U[(U[proba_col] >= r) | (U[proba_col] <= (1 - r))]  # Get confident preds
        num_confident = confident_preds.shape[0]

        print(f'{num_confident} added to L')
        if num_confident == 0:
            break

        L = pd.concat([L, confident_preds])  # add to labeled dataset
        U = U.drop(confident_preds.index.values)  # remove from unlabeled dataset
        i += 1

    return L
