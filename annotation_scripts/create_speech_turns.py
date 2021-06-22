#!/usr/bin/env python
# coding: utf-8

### Create speech_turns.jsonl file for speaker.py recipe
### Output : jsonl file with a list of speech turns without available characters

"""Usage:
create_speech_turns.py <episode> <path_to_corpora>
"""
from docopt import docopt
from pathlib import Path
from forced_alignment import ForcedAlignment

import os
import json

# path to plumcot-prodigy
PATH = Path(__file__).absolute().parent.parent

# load forces alignment
forced_alignment = ForcedAlignment()

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # path to shows directories
    DATA_PLUMCOT = args["<path_to_corpora>"]
    
    ep = args["<episode>"]

    speech_file = f'{PATH}/speech_turns.jsonl'
    
    # data to dump
    data = []

    for episode in [ep]:
        
        serie = episode.split('.')[0]
        
        # load aligned transcript
        episode_path = f'{DATA_PLUMCOT}/{serie}/{episode}.txt'
        episode_sentences = forced_alignment(episode_path)
        sentences = sentences = list(episode_sentences.sents)
        
        # find path to mkv
        if os.path.isfile(f"{DATA_PLUMCOT}/{serie}/{episode}.mkv") : 
            mkv =f"{DATA_PLUMCOT}/{serie}/{episode}.mkv"
        
        print("Looking for sentences without speaker...")
        c = 0
        # find sentences w/ speaker
        for idx, sentence in enumerate(sentences):
            if sentence._.speaker == 'not_available':
                if sentence._.end_time - sentence._.start_time >= 0.5:
                    c+=1
                    # find mkv and dump data
                    data.append({'meta': {'episode':episode, 'start' : sentence._.start_time, 'end': sentence._.end_time},
                                'sentence': f'{sentence}',
                                 'id' : idx,
                                'audio' : f'{DATA_PLUMCOT}/{serie}/{episode}.en.wav',
                                'mkv' : mkv,
                                'answer':'reject',
                                 'plumcot_path': DATA_PLUMCOT,
                                })

    print(f"Found {c} sentences.\nWrite json file to {PATH}")

    # dump data into jsonl file
    with open(speech_file, 'w') as fp:
        fp.write('\n'.join(json.dumps(i) for i in data)
            )
    print("DONE.")
        



