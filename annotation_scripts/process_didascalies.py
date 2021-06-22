#!/usr/bin/env python
# coding: utf-8

"""Usage:
process_didascalies.py <episode> <data_base_name> <user_path>
"""

# ### Delete didascalies in show transcripts (.txt files)

import os
import json
from docopt import docopt
from forced_alignment import ForcedAlignment
from pathlib import Path

# path to databases
DATABASE_PATH = Path(__file__).absolute().parent.parent / "prodigy_databases"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # path to Plumcot data
    DATA_PLUMCOT = args["<user_path>"]
    
    # episode name & json file
    episode_to_process = args["<episode>"]
    database_name = args["<data_base_name>"]
    
    with open(os.path.join(DATABASE_PATH,database_name) , 'r') as json_file:
        json_list = list(json_file)

    # load aligned sentences
    forced_alignment = ForcedAlignment()

    # ### Correction dictionary creation
    # 
    # - Load the aligned sentences of the corresponding episode
    # - Find annotated sentences in annotation data
    # - Find words to delete in annotated sentences (use word position)

    # modifications for the new transcript
    corrections = {}

    for el in json_list:

        # read json
        el = json.loads(el)

        # find elements to delete
        if 'reject' in el['answer'] :

            # displayed tokens in Prodigy (left and right context + sentence)
            tokens = el['tokens']            
            # words to delete
            delete = el['spans']
            meta = el['meta']
            # processed sentence in Prodigy (without context)
            initial_sent = el['sentence']
            # context (disabled)
            left = el['left']
            right = el['right']

            # token list of tokens displayed in Prodigy
            token_list = [token['text'] for token in tokens]
            print("\nEpisode :", meta['episode'])

            # load forced alignment
            episode = meta['episode'].split('.')        
            aligned = f"{DATA_PLUMCOT}/{episode[0]}/{meta['episode']}.txt"       
            transcript = forced_alignment(aligned)      
            sentences = list(transcript.sents)

            for idx, sentence in enumerate(sentences):

                # find left context
                if idx == el["sentence_id"]:
                    print("\nAnnotated sentence in Prodigy :", str(sentence))
                    # delete
                    for dic in delete:
                        if dic['label'] == "DELETE":                            
                            # find the words group to delete in initial sentence
                            to_delete = " ".join(token_list[dic['token_start']:dic['token_end']+1])

                            # delete didascalie
                            if to_delete in str(sentence):                                
                                new_sent = str(sentence).replace(to_delete, '')
                                print("New sentence :", new_sent)
                                center = " "
                                corrections[(meta['episode'], idx)] = (center, new_sent)

                # continue until initial sentence is found
                else:
                    continue


    print("\nDone. Number of processed sentences :", len(corrections))

    # ### Episodes to process
    episode_list = set([el[0] for el in corrections])
    print("Processed episode", episode_list)

    # ### Write new transcript file
    print("\nWRITE NEW TRANSCRIPT FILE\n")
    for episode in episode_list:
        # load forced alignment
        aligned = f"{DATA_PLUMCOT}/{episode.split('.')[0]}/{episode}.txt"    
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)
        sentences_str = [str(sentence) for sentence in sentences]

        # modifications for the current episode
        corrects = []

        for key, val in corrections.items():        
            if key[0] == episode:
                corrects.append((key[1],val))

        # correct sentences
        for idx, s in enumerate(sentences_str):
            # for the current sentence, find the modification to afford
            for el in corrects:
                # if sentence's index equals index in corrections (current episode)            
                if idx == el[0]:
                    # correct the sentence
                    sentences_str[el[0]] = el[1][1]

        # write temp file with the previous version
        temp_name = f"{DATA_PLUMCOT}/{episode.split('.')[0]}/{episode}.temp"
        with open(temp_name, 'w') as writer:
            for sentence in sentences :
                writer.write(f"{sentence._.speaker} {sentence}\n")
                    
        # write new file
        name = f"{DATA_PLUMCOT}/{episode.split('.')[0]}/{episode}.txt"
        with open(name, 'w') as f:
            writer = f        
            for sentence, str_s in zip(sentences, sentences_str):
                # do not write corrections if they are white spaces
                if str_s != '':                
                    writer.write(f"{sentence._.speaker} {str_s}\n")

        print("\nDONE")