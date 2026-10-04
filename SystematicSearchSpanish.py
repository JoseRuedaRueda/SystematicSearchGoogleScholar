"""
Systematic Google Scholar Search

Jose Rueda Rueda: jruedaru@uci.edu

This script searches for a given query in Google Scholar and returns the results.

To run this code, you need to add your own API key in the params dictionary

You can get your own key from serAPI
"""
# Import section, import the necesasry python packages
import os
import numpy as np   # To work with arrays
import pandas as pd  # To work with tables and dict
import pickle        # To save the data into a file
import yaml          # To read the configuration file
from serpapi import GoogleSearch   # To search in google Scholar
from unidecode import unidecode # To remove accents from the words
from copy import deepcopy # To copy the dictionaries
from tqdm import tqdm # To show the progress bar
# -----------------------------------------------------------------------------
# %% Settings
# -----------------------------------------------------------------------------
 
# Location of the configuration file with the words to search
config_file = "wordsSpanish.yaml"
output_folder = "SearchResults"
# Parameters for the search
params = {
  "api_key": "1111", # Your API key, do not share! 
  "engine": "google_scholar",
  "q": "kiwito", # Query, will be updated latter
  "hl": "es",    # Main language to interact with the API
  "as_ylo": "1960", # Year to start the search
  "as_yhi": "2024", # Year to end the search
  "lr": "es", # Languages to search
  "num": 20, # Number of results per page, maximum given by google search
}
searchsPerQuery = 4 # Number of searchs per query
testing = False # If true, we will only do the first word in each block
# -----------------------------------------------------------------------------
# %% Read the configuration file
# -----------------------------------------------------------------------------
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)
print('Successfully read the configuration file: %s' % config_file)
# Move all the words from the configuration file to a single string, separated with OR, to search in google. If the string has more than 250 characters, we create a new one
wordsBlock1 = config['block1']
wordsBlock2 = config['block2']
wordsBlock3 = config['block3']
# See how many configurations we need to try:
totalCombinations = len(wordsBlock1) * len(wordsBlock2) * len(wordsBlock3)
print('Number of configurations: %i' % (totalCombinations))
print('Numer of searches: %i' % (totalCombinations * searchsPerQuery))

# -----------------------------------------------------------------------------
# %% Search in google scholar
# -----------------------------------------------------------------------------
for iw1, w1 in enumerate(wordsBlock1):
    print('-----Starting a new word!: %s' % w1)
    # Testing, only do the first word
    if iw1 > 0 and testing:
        break
    for iw2, w2 in enumerate(wordsBlock2):
        # Testing
        if iw2 > 0 and testing:
            break
        for iw3, w3 in enumerate(wordsBlock3):
            if iw3 > 0 and testing:
                break
            name = unidecode('%s_%s_%s' % (w1, w2, w3))
            print('-----Starting a new word!: %s' % name)
            outputFile = os.path.join(output_folder, name+ '_NoArticle.pkl')
            if os.path.exists(outputFile):
                print('File already exists: %s' % name)
                continue
            # Allocate the list for the results
            localResults = []
            # Create the query
            query = w1 + ' ' + w2 + ' ' + w3 #+ ', type:article'
            # Update the search options with the requested query
            params['q'] = query
            params['start'] = 0
            # Search in google scholar
            for isearch in tqdm(range(searchsPerQuery)):
                # Update the start parameter
                params['start'] = isearch * params['num']
                # Search in google scholar
                search = GoogleSearch(params)
                results = search.get_dict()
                # Check if there are results
                localResults.append(deepcopy(results))

            # Save the results in a file
            print('----SUCCESSFULLY SEARCHED: %s' % query)
            print('Saving file')
            # Save the results in a file
            with open(outputFile, 'wb') as f:
                pickle.dump(localResults, f)
            
            
            

# %%
