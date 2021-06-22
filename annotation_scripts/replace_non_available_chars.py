#!/usr/bin/env python
# coding: utf-8

"""Usage:
replace_non_available_chars.py <episode> <data_base_name> <path_to_corpora>
"""

# ### Replace "not_available" characters by a character name selected in select_characters or speaker.py recipes
from pathlib import Path
from docopt import docopt
from forced_alignment import ForcedAlignment

import os
import json

# path to databases
DATABASE_PATH = Path(__file__).absolute().parent.parent / "prodigy_databases"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # path to corpora
    DATABASE_PLUMCOT = args["<path_to_corpora>"]

    # episode name & json file
    episode_to_process = args["<episode>"]
    database_name = args["<data_base_name>"]
    
    with open(os.path.join(DATABASE_PATH,database_name) , 'r') as json_file:
        json_list = list(json_file)
        
    # #### Load forced alignment
    forced_alignment = ForcedAlignment()
    
    serie = episode_to_process.split('.')[0]

    # path to forced alignment
    if os.path.isfile(f"{DATA_PLUMCOT}/{serie}/{episode_to_process}.txt"):
        aligned = f"{DATA_PLUMCOT}/{serie}/{episode_to_process}.txt"
    else:
        print("No aligned file for")
        aligned = ""

    # load forced alignment        
    transcript = forced_alignment(aligned)      
    sentences = list(transcript.sents)

    # annotations dictionary
    for dictionary in json_list:
        result = json.loads(dictionary)
        meta = result['meta']

    # save annotations in a list
    liste = []
    
    for dictionary in json_list:
        
        # load jsonl & metadata
        result = json.loads(dictionary)
        meta = result['meta']
        
        # find the annotated character
        for idx, sentence in enumerate(sentences):
            
            if episode_to_process in meta['episode']:
                if result['answer'] == 'accept':
                    if not result['accept']:                        
                        if idx == result['sentence_id']:
                            if "other_speaker" in result:
                                liste.append((idx,([result["other_speaker"]], sentence)))
                        else:                        
                            continue
                    else:
                        # if one character is selected
                        if len(result['accept']) == 1:
                            if idx == result['sentence_id']:
                                liste.append((idx,(result['accept'], sentence)))
                        elif len(result['accept']) != 1:
                            # if multiple characters are selected
                            if idx == result['sentence_id']:
                                multiple_speakers = '@'.join(result['accept'])
                                liste.append((idx,(multiple_speakers, sentence)))

    print("Apply annotations")                            
    # for each sentence in aligned sentences
    for idx, sentence in enumerate(sentences):
        # for each annotated sentence
        for el in liste:
            
            sentence_id = el[0]
            speaker_sentence = el[1]
            
            # use sentences idx to apply annotations
            if sentence_id == idx:
                
                for word in sentences[idx]:
                    # add speaker to the word
                    word._.speaker = " ".join(speaker_sentence[0])

    # ## Create temp file with previous transcript
    print("Writing new file")
    temp_file = open(f"{DATA_PLUMCOT}/{serie}/{episode_to_process}.temp", 'w')
    
    with open(f"{DATA_PLUMCOT}/{serie}/{episode_to_process}.txt", 'r') as f:
        for line in f :
            line = line.strip('\n')
            if len(line.split()) == 8:
                temp_file.write(f'{line}\n')
            elif len(line.split()) == 7:
                temp_file.write(f'{line} _\n')            
            elif len(line.split()) == 6:
                temp_file.write(f'{line}_ _\n')
    temp_file.close()

    # ## Write new aligned file
    new_file = open(f"{DATA_PLUMCOT}/{serie}/{episode_to_process}.txt", "w")

    # use aligned sentences to write the new aligned file
    for sentence in sentences:
        for word in sentence:
            confidence = "{:.2f}".format(word._.confidence)
            start_time = "{:.2f}".format(word._.start_time)
            end_time = "{:.2f}".format(word._.end_time)
            new_file.write(f'{episode_to_process} {word._.speaker} {start_time} {end_time} {word} {confidence} {word._.entity_linking} {word._.addressee}\n')

    new_file.close()
    print("DONE.")