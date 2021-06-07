#!/usr/bin/env python
# coding: utf-8

# ## Check text and audio alignment
# 
# Input : serie_uri, jsonl data
# Output : accepted or rejected answers
# 
# If rejected for the two excerpt of the episode, please check if the entire transcript corresponds to the audio or not

"""Usage:
process_alignment.py <id_series> <data_base_name>
"""

import json
import os
from docopt import docopt
from pathlib import Path

# path to alignment database
DATABASE_PATH = Path(__file__).parent.absolute().parent / "prodigy_databases"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    id_series = args["<id_series>"]
    database_name = args["<data_base_name>"]

    # import json file
    json_file = database_name

    with open(os.path.join(DATABASE_PATH, json_file), 'r') as json_file:
        json_list = list(json_file)

    print(f"\nNumber of annotations in the jsonl alignment file : {len(json_list)}\n")

    # find the annotations for the current show
    for el in json_list:
        # read json
        el = json.loads(el)
        meta = el['meta']
        if id_series in meta['episode']:
            print(meta['episode'], el['answer'])

