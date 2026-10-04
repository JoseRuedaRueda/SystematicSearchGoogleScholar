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
input_file = "SearchResults/database.pk"
output_folder = 'SearchResults/Databases'
words_file = "wordsEnglish.yaml"
createPublisherFile = True
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
# %% Create publisher file
# -----------------------------------------------------------------------------
# Save all publishers to a text file
if createPublisherFile:
    publishers = database['publisher'].unique()
    with open(os.path.join(output_folder, 'publishers.txt'), 'w') as f:
        for publisher in publishers:
            f.write(f"{publisher}\n")


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
dbpress.to_pickle(output_folder + '/Press.pk')
dbpress.to_csv(output_folder + '/Press.csv')

# -----------------------------------------------------------------------------
# %% Get the publications from the journals
# -----------------------------------------------------------------------------
# Get the publications from the journals
journals = []
idWithBlock3Words = []
for identry, name in zip(database['result_id'],database['title'], ):
    for word in wordsBlock3:
        if word in name:
            idWithBlock3Words.append(identry)
with open(output_folder + '/AcademicJournals.txt', 'r') as f:
    for line in f:
        journals.append(line.strip())
dbjournals = database[database['publisher'].isin(journals)]
print(f"Publications from the journals: {len(dbjournals)}")
dbjournals.to_pickle(output_folder + '/Journals.pk')
dbjournals.to_csv(output_folder + '/Journals.csv')
# For those dbjournals, we need to check if they have the words from block 3
dbjournalsAndGroup3 = dbjournals[dbjournals['result_id'].isin(idWithBlock3Words)]
print(f"Publications from the journals with block 3 words: {len(dbjournalsAndGroup3)}")
# Save to file
dbjournalsAndGroup3.to_pickle(output_folder + '/JournalsAndGroup3.pk')
dbjournalsAndGroup3.to_csv(output_folder + '/JournalsAndGroup3.csv')
database = database[~database['publisher'].isin(journals)]
# -----------------------------------------------------------------------------
# %% Filter
# -----------------------------------------------------------------------------
# Recover the Journal from the unknwons:
journalsPublishers = []
unknowns = []
idWithBlock3Words = []
for identry, name, line in zip(database['result_id'],database['title'], database['publisher']):
    unknowns.append(line.strip())
    if 'Journal of' in line:
        journalsPublishers.append(line.strip())
    elif 'journal' in line:
        journalsPublishers.append(line.strip())
    elif 'Journal' in line:
        journalsPublishers.append(line.strip())
    for word in wordsBlock3:
        if word in name:
            idWithBlock3Words.append(identry)
# Save to files
with open(output_folder + '/Unknown.txt', 'w') as f:
    for unknown in unknowns:
        f.write(f"{unknown}\n")
with open(output_folder + '/JournalsFromUnknowns.txt', 'w') as f:
    for journal in journalsPublishers:
        f.write(f"{journal}\n")
# -----------------------------------------------------------------------------
# %% Get the publications from the Posible Journals
# -----------------------------------------------------------------------------
dbjournalsUnknown = database[database['publisher'].isin(journalsPublishers)]
print(f"Publications from the posible journals: {len(dbjournalsUnknown)}")
dbjournalsUnknown.to_pickle(output_folder + '/JournalsUnknown.pk')
dbjournalsUnknown.to_csv(output_folder + '/JournalsUnknown.csv')
# For those dbjournalsUnknown, we need to check if they have the words from block 3
dbjournalsUnkownAndGroup3 = dbjournalsUnknown[dbjournalsUnknown['result_id'].isin(idWithBlock3Words)]
print(f"Publications from the posible journals with block 3 words: {len(dbjournalsUnkownAndGroup3)}")
# Save to file
dbjournalsUnkownAndGroup3.to_pickle(output_folder + '/JournalsUnknownAndGroup3.pk')
dbjournalsUnkownAndGroup3.to_csv(output_folder + '/JournalsUnknownAndGroup3.csv')
database = database[~database['publisher'].isin(journalsPublishers)]
# -----------------------------------------------------------------------------
# %% Save the rest of the database
# -----------------------------------------------------------------------------
database.to_pickle(output_folder + '/Unknown.pk')
database.to_csv(output_folder + '/Unknown.csv')
print(f"Publications from the unknown: {len(database)}")
# for those dbjournalsUnknown, we need to check if they have the words from block 3
databaseAndGroup3 = database[database['result_id'].isin(idWithBlock3Words)]
print(f"Publications from the unknown with block 3 words: {len(databaseAndGroup3)}")
# Save to file
databaseAndGroup3.to_pickle(output_folder + '/UnknownAndGroup3.pk')
databaseAndGroup3.to_csv(output_folder + '/UnknownAndGroup3.csv')

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



