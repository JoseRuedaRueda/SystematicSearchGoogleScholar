"""
Filter database
"""
import os
import yaml
import pandas as pd

# -----------------------------------------------------------------------------
# %% Settings
# -----------------------------------------------------------------------------
# Input
input_file = "SearchResults/databaseSpanishNoArticles.pkl"
output_folder = 'SearchResults/Databases'
words_file = "wordsSpanish.yaml"
# -----------------------------------------------------------------------------
# %% Load data
# -----------------------------------------------------------------------------
database = pd.read_pickle(input_file)
# Load the words from the configuration file
with open(words_file, 'r') as file:
    config = yaml.safe_load(file)
print('Successfully read the configuration file: %s' % words_file)
# Move all the words from the configuration file to a single string, separated with OR, to search in google. If the string has more than 250 characters, we create a new one
wordsBlock1 = config['block1']
wordsBlock2 = config['block2']
wordsBlock3 = config['block3']

# -----------------------------------------------------------------------------
# %% Get the publications from the press
# -----------------------------------------------------------------------------
# Get the publications from the press
press = []
with open(output_folder + '/Press.txt', 'r') as f:
    for line in f:
        press.append(line.strip())
dbpress = database[database['publisher'].isin(press)]
database = database[~database['publisher'].isin(press)]
print(f"Publications from the press: {len(dbpress)}")
dbpress.to_pickle(output_folder + '/PressNoArticleSpanish.pk')
dbpress.to_csv(output_folder + '/PressNoArticleSpanish.csv')

# -----------------------------------------------------------------------------
# %% Filter
# -----------------------------------------------------------------------------
# Recover the Journal from the unknwons:
idWithBlock3Words = []
flags = np.zeros(len(database), dtype=bool)
counter = 0
for identry, name, line in zip(database['result_id'],database['title'], database['publisher']):
    for word in wordsBlock3:
        if word in name:
            idWithBlock3Words.append(identry)
            flags[counter] = True
            break
    counter += 1


# -----------------------------------------------------------------------------
# %% Get the publications from the Posible Journals
# -----------------------------------------------------------------------------
# for those dbjournalsUnknown, we need to check if they have the words from block 3
databaseAndGroup3 = database[flags]
print(f"Publications from the unknown with block 3 words: {len(databaseAndGroup3)}")
# Save to file
databaseAndGroup3.to_pickle(output_folder + '/databaseSpanishAndGroup3NoArticle.pk')
databaseAndGroup3.to_csv(output_folder + '/databaseSpanishAndGroup3NoArticle.csv')

# -----------------------------------------------------------------------------
# %% Social Siences
# -----------------------------------------------------------------------------
# socialJournals = []
# with open(output_folder + '/AcademicJournalsSocial.txt', 'r') as f:
#     for line in f:
#         socialJournals.append(line.strip())
# with open(output_folder + '/JournalsSocialFromUnknowns.txt', 'r') as f:
#     for line in f:
#         socialJournals.append(line.strip())
# dbsocialJournals = dbjournals[dbjournals['publisher'].isin(socialJournals)]
# print(f"Publications from the social journals: {len(dbsocialJournals)}")
# dbsocialJournals.to_pickle(output_folder + '/SocialJournals.pk')
# dbsocialJournals.to_csv(output_folder + '/SocialJournals.csv')

# dbsocialJournalsUnknown = dbjournalsUnknown[dbjournalsUnknown['publisher'].isin(socialJournals)]
# print(f"Publications from the social posible journals: {len(dbsocialJournalsUnknown)}")
# dbsocialJournalsUnknown.to_pickle(output_folder + '/SocialJournalsUnknown.pk')
# dbsocialJournalsUnknown.to_csv(output_folder + '/SocialJournalsUnknown.csv')



