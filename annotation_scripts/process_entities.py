#!/usr/bin/env python
# coding: utf-8

"""Usage:
add_entity_linking.py <episode> <data_base_name>
"""

### Adding Entity Linking annotations (3rd person & names) - fgyrom Prodi

#    Arguments : episode to process, database 

import os
import json
from forced_alignment import ForcedAlignment
from docopt import docopt
from pathlib import Path


# path to databases
DATABASE_PATH = Path(__file__).absolute().parent.parent / "prodigy_databases"

# path to Plumcot data
DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # episode name & json file
    episode = args["<episode>"]
    database_name = args["<data_base_name>"]

    with open(os.path.join(DATABASE_PATH, database_name), 'r') as json_file:
        json_list = list(json_file)

    serie = episode.split('.')[0]
    episode_path = f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.aligned'


    # ### Create temp file & load sentences
    temp_file = open(f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.temp', 'w')
    with open(episode_path, 'r') as f:
        for line in f :
            line = line.strip('\n')
            if len(line.split()) == 8:
                temp_file.write(f'{line}\n')
            else:
                print("Bad line length, shoud be 8 (entity + addressee annotated)")
    temp_file.close()

    # load aligned sentences
    forced_alignment = ForcedAlignment()
    episode_path = f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.temp'
    episode_sentences = forced_alignment(episode_path)
    sentences = list(episode_sentences.sents)

    # ### Extract annotations
    container = {}

    for el in json_list:

        # read json
        el = json.loads(el)

        meta = el["meta"]

        if meta["episode"] == episode and el["answer"] == "accept":
            print("\n")

            annotations = []

            # if input 1 is full
            if "input_1" in el:

                # take annotation from "spans"
                for span in el["spans"]:

                    if span["label"] == "EL1":
                        # find  entities
                        token = el["text"][span["start"]: span["end"]+1]
                        label = span["label"]
                        annotation = (token, el["input_1"])
                        annotations.append(annotation)

            # if input 2 is full
            if "input_2" in el:

                # récupérer les annotations dans "spans"
                for span in el["spans"]:

                    if span["label"] == "EL2":
                        # find  entities
                        # find  entities
                        token = el["text"][span["start"]: span["end"]+1]
                        label = span["label"]
                        annotation = (token, el["input_2"])
                        annotations.append(annotation)

            # if input 3 is full
            if "input_3" in el:

                # récupérer les annotations dans "spans"
                for span in el["spans"]:

                    if span["label"] == "EL3":

                        # find  entities
                        token = el["text"][span["start"]: span["end"]+1]
                        label = span["label"]
                        annotation = (token, el["input_3"])
                        annotations.append(annotation)

            container[meta["sentence_id"]] = {"id": int(meta["sentence_id"]), "sentence":el["text"], 
                                                     "entities":annotations, "type":"EL"}

    print("Total entity annotations :", len(container))
    print(container)

    # ### Apply annotations
    # Find sentence to annotate, then word to annotate

    for idx, el in container.items():
        # find word in sentence corresponding to entity
        # when EL is selected
        if el['type'] == "EL":

            # for entity in entities list
            for e in el["entities"] :
                for word in sentences[int(idx)]:
                    # find word corresponding to annotation
                    if str(word) == e[0].strip(' '):

                        if word._.entity_linking == "_" or word._.entity_linking == "?":
                            print(word)
                            word._.entity_linking = e[1].strip(' ')


    # ### Update alignment file

    new_file = open(f"{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.aligned", "w")
    print(f"Writing alignment file to {DATA_PLUMCOT}/{serie}/forced-alignment")
    for sentence in sentences:
        for word in sentence:
            confidence = "{:.2f}".format(word._.confidence)
            start_time = "{:.2f}".format(word._.start_time)
            end_time = "{:.2f}".format(word._.end_time)
            
            if word._.entity_linking == "" or word._.addressee == " " :
                word._.entity_linking = "_"
                
            new_file.write(f'{episode} {word._.speaker} {start_time} {end_time} {word} {confidence} {word._.entity_linking} {word._.addressee}\n')

    new_file.close()
    print("DONE.")





