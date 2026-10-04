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
input_file = "SearchResults/databaseSpanishSILVIA.pk"
output_folder = 'SearchResults/Databases'
words_file = "wordsSpanish.yaml"
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
    with open(os.path.join(output_folder, 'publishersSpanish.txt'), 'w') as f:
        with open(os.path.join(output_folder, 'publishersSpanishJournals.txt'), 'w') as f2:
            with open(os.path.join(output_folder, 'publishersSpanishnotjournalInName.txt'), 'w') as f3:
                for publisher in publishers:
                    f.write(f"{publisher}\n")
                    if 'Journal' in publisher or 'journal' in publisher or 'JOURNAL' in publisher:
                        f2.write(f"{publisher}\n")
                    else:
                        f3.write(f"{publisher}\n")
# Get all the publishers where journal or Journal is in the name
    
# -----------------------------------------------------------------------------
# %% combine the two lists of journals
# -----------------------------------------------------------------------------
journals = []
with open(os.path.join(output_folder, 'publishersSpanishJournals.txt'), 'r') as f2:
    for line in f2:
        journals.append(line.strip())
    
print(f"Number of journals: {len(journals)}")
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
dbpress.to_pickle(output_folder + '/PressSpanishSILVIA.pk')
dbpress.to_csv(output_folder + '/PressSpanishSILVIA.csv')

# -----------------------------------------------------------------------------
# %% Get the publications from the journals
# -----------------------------------------------------------------------------
# Get the publications from the press
dbJournals = database[database['publisher'].isin(journals)]
database = database[~database['publisher'].isin(journals)]
print(f"Publications from possible Journals: {len(dbJournals)}")
dbJournals.to_pickle(output_folder + '/journalsSpanishSILVIA.pk')
dbJournals.to_csv(output_folder + '/journalsSpanishSILVIA.csv')
database.to_pickle(output_folder + '/restSpanishSILVIA.pk')
database.to_csv(output_folder + '/restSpanishSILVIA.csv')
print(f"Rest of publications: {len(database)}")
# -----------------------------------------------------------------------------
# %% Get the publications from the the rest with the group 3 word in the name
# -----------------------------------------------------------------------------
idWithBlock3Words = []
for identry, name in zip(database['result_id'],database['title'], ):
    for word in wordsBlock3:
        if word in name:
            idWithBlock3Words.append(identry)
databaseW3 = database[database['result_id'].isin(idWithBlock3Words)]
print(f"Publications with block 3 words: {len(databaseW3)}")
databaseW3.to_pickle(output_folder + '/restSpanishWithBlock3SILVIA.pk')
databaseW3.to_csv(output_folder + '/restSpanishWithBlock3SILVIA.csv')

# -----------------------------------------------------------------------------
# %% Get the publications from the the journals with the group 3 word in the name
# -----------------------------------------------------------------------------
idWithBlock3Words = []
for identry, name in zip(dbJournals['result_id'],dbJournals['title'], ):
    for word in wordsBlock3:
        if word in name:
            idWithBlock3Words.append(identry)
databaseW3Journals = dbJournals[dbJournals['result_id'].isin(idWithBlock3Words)]
print(f"Publications with block 3 words and journals: {len(databaseW3Journals)}")
databaseW3Journals.to_pickle(output_folder + '/journalsSpanishhWithBlock3SILVIA.pk')
databaseW3Journals.to_csv(output_folder + '/journalsSpanishWithBlock3SILVIA.csv')



