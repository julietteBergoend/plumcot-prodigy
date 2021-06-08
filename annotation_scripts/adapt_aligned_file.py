#!/usr/bin/env python
# coding: utf-8

# ### Adapt aligned files
#
#     Each line in aligned file must have a length of 8 :
#     e.g : <episode_name_field> <speaker_field> <start_time_field> <end_time_field> <word_field> <confidence_field> 
#    <entity_linking_field> <addressee_field>
#

"""Usage:
process_alignment.py <episode_name>
"""
import os

from docopt import docopt
from pathlib import Path

# path to Plumcot data
DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    episode = args["<episode_name>"]
    show = episode.split('.')[0]
    
    # path to aligned file
    aligned_path = f'{DATA_PLUMCOT}/{show}/forced-alignment/{episode}.aligned'
    
    # temp file to write previous aligned file
    temp_file = open(f'{DATA_PLUMCOT}/{show}/forced-alignment/{episode}.temp', 'w')
    
    # write temp file
    with open(aligned_path, 'r') as f:
        for line in f :
            line = line.strip('\n')
            temp_file.write(f'{line}\n')
    temp_file.close()

    # write new aligned file 
    print(f"Writing new aligned file to {DATA_PLUMCOT}/{show}/forced-alignment/")
    temp_path = f'{DATA_PLUMCOT}/{show}/forced-alignment/{episode}.temp'
    
    aligned_file = open(f'{DATA_PLUMCOT}/{show}/forced-alignment/{episode}.aligned', 'w')
    
    with open(temp_path, 'r') as f:
        for line in f :
            line = line.strip('\n')
            # keep line if len == 8
            if len(line.split()) == 8:
                aligned_file.write(f'{line}\n')
            # add one field if len == 7
            elif len(line.split()) == 7:
                aligned_file.write(f'{line} ?\n')
            # add two fields if len == 6
            elif len(line.split()) == 6:
                aligned_file.write(f'{line} ? ?\n')
    aligned_file.close()
    print("DONE.")





