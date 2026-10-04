"""
This scrippt translates the results from the systematic search to a pandas dataframe.

This pandas dataframes are an easy way of processing the data and saving it.
"""
import os
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
plt.ion()
# -----------------------------------------------------------------------------
# %% Settings
# -----------------------------------------------------------------------------
output_folder = "SearchResults"
publishersFile = "publisherFilters.yaml"
config_file = "wordsSpanish.yaml"
outputFile = os.path.join(output_folder, 'databaseSpanishNoArticles.csv')
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)
print('Successfully read the configuration file: %s' % config_file)
# Move all the words from the configuration file to a single string, separated with OR, to search in google. If the string has more than 250 characters, we create a new one
wordsBlock1 = config['block1']
wordsBlock2 = config['block2']
wordsBlock3 = config['block3']
# -----------------------------------------------------------------------------
# %% Read the data
# -----------------------------------------------------------------------------
# Load, if any, the existing database
databaseFile = os.path.join(output_folder, 'databaseSpanishNoArticles.pkl')
if os.path.exists(databaseFile):
    database = pd.read_pickle(databaseFile)
else:
    # Create an empty dataframe
    database = pd.DataFrame()
# Open the done file (write-read acess)
# if not os.path.exists(doneFile):
#     flag = True
# else:
#     flag = False
# doneFileID = open(doneFile, "a+")
# if not flag:
#     # Read the lines
#     done = doneFileID.readlines()
#     # Remove the new line character
#     done = [x.strip() for x in done]
#     # Remove the empty lines
#     done = [x for x in done if x]
# else:
#     done = []
# Loop over the files in the output folder
for file in tqdm(os.listdir(output_folder)):
    if file.endswith("_NoArticle.pkl"):
        # check if the file is done
        # if file in done:
        #     continue
        # Read the data
        # Get the first word, to check if it is in the desired list
        words = file.split('_')
        # Check if the first word is in the list
        if words[0] not in wordsBlock1:
            continue
        with open(os.path.join(output_folder, file), "rb") as f:
            data = pd.read_pickle(f)
        # Add only the 'organic results' to the database
        for results in data:
            if 'organic_results' in results:
                dummy = pd.DataFrame(results['organic_results'])
                # Now, we need to clean a bit the dataframe. Get the publication info
                pub_info = dummy.pop('publication_info')
                # Add the publication info to the dataframe
                dummy['authors'] = None
                dummy['year'] = None
                dummy['publisher'] = None
                dummy['domain'] = None
                dummy['Ncoauthors'] = None
                dummy['citedBy'] = None
                dummy['cites_id'] = None
                dummy['PDFlink'] = None
                dummy['NeedsCheck'] = False
                for i, item in enumerate(pub_info):
                    # The key which will be always the same is the summary, containing the author list, publisher and year (mostly)
                    summary = item.pop('summary').strip()
                    # Normaly, the summarey will be: author list - publisher - year
                    try:
                        [authors, info, domain] = summary.split(' - ')
                    except ValueError:  # Something is missing
                        # If the last 4 characters are digits, then the year is there and the domain is missing
                        if summary[-4:].isdigit():
                            [authors, info] = summary.split(' - ')
                            domain = ''
                        else:
                            # Assume that all the info is the authors and set it
                            # For manual check
                            authors = summary
                            info = ''
                            domain = ''
                            dummy.at[i, 'NeedsCheck'] = True
                    authors = authors.split(',')
                    # Now the info is published, year, strip the string and take as year the last 4 digit, this will avoid the issues where the publisher as commas in the name
                    info = info.strip()
                    try:
                        year = int(info[-4:])
                    except ValueError:
                        # The year is missing in the info, just set it to NaN
                        year = np.nan
                    # The publisher is the rest of the string
                    publisher = info[:-4].strip()[:-1] # Remove the last comma
                    # Add the new columns to the dataframe
                    dummy.at[i, 'authors'] = authors
                    dummy.at[i, 'year'] = year
                    dummy.at[i, 'publisher'] = publisher
                    dummy.at[i, 'domain'] = domain
                    dummy.at[i, 'Ncoauthors'] = len(authors)
                    
                    keys = list(item.keys())
                    for key in keys:
                        if key =='authors':
                            continue
                            # The authors returned are not the authors of the 
                            # paper, but those with a google scholar profile
                        # If the key is not in the database, add it
                        if key not in dummy.columns:
                            database[key] = None
                        dummy.at[i, key] = item[key]
                # Now we can proceed with the citations, there are some publications which may not have this info, so we just need to try:
                inline_links = dummy.pop('inline_links')
                for i, item in enumerate(inline_links):
                    if 'cited_by' in item:
                        try:
                            dummy.at[i, 'citedBy'] = int(item['cited_by'])['total']
                        except TypeError:
                            dummy.at[i, 'citedBy'] = -1
                        try:
                            dummy.at[i, 'cites_id'] = item['cited_by']['cites_id']
                        except KeyError:
                            dummy.at[i, 'cites_id'] = ''
                    else:
                        dummy.at[i, 'citedBy'] = -1
                        dummy.at[i, 'cites_id'] = ''
                # Now the PDF link (aka resource)
                try:
                    resources = dummy.pop('resources')
                    for i, item in enumerate(resources):
                        # Check that item is not None nor NaN
                        if item is not None and not np.any(pd.isna(item)):
                            dummy.at[i, 'PDFlink'] = item[0]['link']
                except KeyError:
                    pass
                database = pd.concat([database, dummy], ignore_index=True)
                # Remove duplicates
                database = database.drop_duplicates(subset=['result_id'])
        # Write the file name to the done file
        # doneFileID.write(file + '\n')
# doneFileID.close()
# -----------------------------------------------------------------------------
# %% Save the database
# -----------------------------------------------------------------------------
# Set the proper types for each column:
# Position: integer
database['position'] = database['position'].astype(int)
# Title: string
database['title'] = database['title'].astype(str)
# Result_id: string
database['result_id'] = database['result_id'].astype(str)
# Link: string
database['link'] = database['link'].astype(str)
# Publisher: string
database['publisher'] = database['publisher'].astype(str)
# Domain: string
database['domain'] = database['domain'].astype(str)
# Ncoauthors: integer
database['Ncoauthors'] = database['Ncoauthors'].astype(int)
# snippet: strings
database['snippet'] = database['snippet'].astype(str)
# Save the database
# Set the dtype of the year column to int
database['year'] = database['year'].astype(float)
# Same with cited by
database['citedBy'] = database['citedBy'].astype(int)
# Filter the database to keep only the uniques result_id
database = database.drop_duplicates(subset=['result_id'])
# Save as pkl for latter user
database.to_pickle(databaseFile)
# Save as csv for easy reading for Silvia
# outputFile = os.path.join(output_folder, 'database.csv')
database.to_csv(outputFile, index=False)

# ---------------------------------------------------------------------------
# %% Analyse the database
# ---------------------------------------------------------------------------
# Figure 1: Publications per year
fig1, ax1 = plt.subplots()
database.hist('year', ax=ax1, bins=np.arange(1964, 2025))
ax1.set_title('Publications per year')
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of publications')
plt.show()

# %% Figure 2: Publications per publisher
# fig2, ax2 = plt.subplots()
# database['publisher'].value_counts().plot.bar(ax=ax2)
# ax2.set_title('Publications per publisher')
# ax2.set_ylabel('Number of publications')
# fig2.show()


# %% Figure 3: Publications per domain
# fig3, ax3 = plt.subplots()
# database['domain'].value_counts().plot.bar(ax=ax3)
# ax3.set_title('Publications per domain')
# ax3.set_ylabel('Number of publications')
# plt.tight_layout()
# fig3.show()

# %% Figure 4: Publications per number of coauthors
# fig4, ax4 = plt.subplots()
# database['Ncoauthors'].value_counts().plot.bar(ax=ax4)
# ax4.set_title('Publications per number of coauthors')
# ax4.set_ylabel('Number of publications')
# ax4.set_xlabel('Number of coauthors')

# plt.tight_layout()
# fig4.show()

# %% Figure 6: Publications per author
# # The fisr step is to create a list of all the authors, in each row, the field authors is a list of authors
# authors = []
# # Loop over the rows
# for i, row in database.iterrows():
#     authors.extend(row['authors'])
# # Now we have a list of authors, we need to count the number of publications per author
# authors = pd.Series(authors)
# authors = authors.value_counts()
# # Now we have a series with the number of publications per author
# fig6, ax6 = plt.subplots()
# authors.plot.bar(ax=ax6)
# ax6.set_title('Publications per author')
# ax6.set_ylabel('Number of publications')
# ax6.set_xlabel('Author')
# plt.tight_layout()
# fig6.show()

# %% Figure 7: Publications per number of citations
# fig7, ax7 = plt.subplots()
# # order the x axis by the number of citations
# database = database.sort_values(by='citedBy')
# # Make the plot with the x axis orderred by citations
# database['citedBy'].value_counts().plot.bar(ax=ax7)
# ax7.set_title('Publications per number of citations')
# ax7.set_ylabel('Number of publications')
# ax7.set_xlabel('Number of citations')
# plt.tight_layout()
# fig7.show()


