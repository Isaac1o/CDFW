# CDFW
Welcome to the repository for University of San Francisco' master's of data science practicum for California Department of Fish and Wildlife.

# Objectives

The main focus of this practicum is using social media data to understand the public's view on human-wildlife interactions. We are  currently working to achieve this by using machine learning to classify relevant tweets and performing sentiment analysis on them. Additionally, we plan to incorporate other covariates such as rainfall, temperate, and population density to see how they influence the number of occurrences and sentiment towards human-wildlife interactions.

# Current Progress

## Human-Coyote Interactions

### Initial Analysis

Coyotes are one of the most common wildlife animals spoted in California. Currently, there is a huge gap in human-coyote conflict reports. Of the reports submitted to the state, the majority of them are negative. 

We are attempting to use Twitter to fill this information gap. Twitter provides a plethora of unfilters individual personal experiences and by querying tweets that contain the keywords "coyote" or "coyotes" we are able to retrieve data regarding human-coyote interactions. 

We then performed sentiment analysis on these tweets using a sentiment analysis model pretrained on tweets.

Feel free to read more about this project [here](https://medium.com/@isaac1o/human-and-coyote-interactions-a-data-science-view-5f39e47e24a9).



# How to Create a Branch

A branch allows you to work independly of the master branch. After you have contributed to your branch you can make a pull request to merge it with the master branch.

## Steps

First, pull changes from upstream before creating a new branch.

`$ git pull`

Create a branch on your local machine and switch into this branch:

`$ git checkout -b [name_of_your_branch]`

Commit your contributions to this branch.

`$ git commit -a -m 'commit message'`

Push your branch onto github:

`$ git push origin [name_of_your_branch]`

Pushing your branch will create a pull request that can be reviewed before merging it with the master branch.

This is how to create a local branch without switching into it:

`$ git branch <name_of_your_branch>`