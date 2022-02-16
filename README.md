# CDFW
Repository for MSDS practicum for California Department of Fish and Wildlife

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