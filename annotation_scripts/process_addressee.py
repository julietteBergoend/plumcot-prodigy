#!/usr/bin/env python
# coding: utf-8
"""Usage:
process_didascalies.py <episode> <data_base_name>
"""

import os
import json
from docopt import docopt
from forced_alignment import ForcedAlignment
from pathlib import Path

# path to databases
DATABASE_PATH = Path(__file__).absolute().parent.parent / "prodigy_databases"

# path to Plumcot data
DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"

# custom dictionary to store multiple values in one key
# helpful for sentences with multiple addressees
class DictList(dict):
    def __setitem__(self, key, value):
        try:
            # Assumes there is a list on the key
            self[key].append(value)
        except KeyError: # If it fails, because there is no key
            super(DictList, self).__setitem__(key, value)
        except AttributeError: # If it fails because it is not a list
            super(DictList, self).__setitem__(key, [self[key], value])

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # episode name & json file
    episode_to_process = args["<episode>"]
    database_name = args["<data_base_name>"]
    
    with open(os.path.join(DATABASE_PATH,database_name), 'r') as json_file:
        json_list = list(json_file)

    serie = episode_to_process.split('.')[0]
    episode_path = f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode_to_process}.aligned'

    # ## Create temp file
    temp_file = open(f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode_to_process}.temp', 'w')
    with open(episode_path, 'r') as f:
        for line in f :
            line = line.strip('\n')
            if len(line.split()) == 8:
                temp_file.write(f'{line}\n')
            elif len(line.split()) == 7:
                temp_file.write(f'{line} _\n')
            elif len(line.split()) == 6:
                temp_file.write(f'{line} _ _\n')
    temp_file.close()

    # load aligned transcript
    forced_alignment = ForcedAlignment()
    episode_path = f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode_to_process}.temp'
    episode_sentences = forced_alignment(episode_path)
    sentences = list(episode_sentences.sents)

    # ### Find addressees
    # 
    # Use "head_span" & "child_span" in selected relations

    # store annotated sentences (thanks to idx) into the ustom dictionary dictionary
    container = DictList()

    for el in json_list:

        # read json
        el = json.loads(el)

        #metadata
        meta = el["meta"]

        if episode_to_process in el["episode"] and "accept" in el["answer"]:
            
            print("Process annotations...")

            # find selected relations
            for relations in el["relations"]:

                # find head span & child span
                head_span = relations["head_span"]
                child_span = relations["child_span"]

                # find corresponding sentence and speaker
                sentence_head = el["text"][ head_span["start"]: head_span["end"]+1 ]
                speaker_child = el["text"][ child_span["start"]: child_span["end"]+1 ]

                # warning : line breaks
                sentence_head = sentence_head.strip("\n")
                speaker_child = speaker_child.strip("\n")

                # fill custom dictionary
                for sentence in meta:
                    if sentence_head == meta[sentence]["sentence"]:
                        # add selection to custom dictionary
                        container[ meta[sentence]["id"] ] = {"id": int(meta[sentence]["id"]), "speaker":meta[sentence]["speaker"], "sentence":meta[sentence]["sentence"], "addressee":speaker_child, "type":"SELECTING"}

            # find labelled relations
            for span in el["spans"]:

                # find annotated label
                if len(span) == 5 and span['label'] != "speaker":
                    sentence_head = el["text"][span["start"]: span["end"]+1]
                    speaker_child = span['label']

                    sentence_head = sentence_head.strip("\n")
                    speaker_child = speaker_child.strip("\n")

                    for sentence in meta:
                        if meta[sentence]["sentence"] == sentence_head:
                            container[ meta[sentence]["id"] ] = {"id": int(meta[sentence]["id"]), "speaker":meta[sentence]["speaker"], "sentence":meta[sentence]["sentence"], "addressee":speaker_child, "type":"LABELLING"}
        
        else:
            continue

    print("\nNumber of annotated setences :", len(container))

    print("Number of aligned sentences :", len(sentences))


    # keep id of the sentence + addressee
    final_annotations = {}

    for idx, annotations in container.items():
        # if the current element is a dictionary, there is one annotation
        if isinstance(annotations, dict):
            # store sentence id & addressee
            final_annotations[int(idx)] = annotations['addressee']

        # if the current element is a list, there are multiple annotations
        elif isinstance(annotations, list):

            # for each annotation, keep addressee
            ad_list = []
            for i in annotations:
                locutor = i["speaker"]
                sentence = i['sentence']
                addressee = i['addressee'].strip(' ')
                # except if its the same as the current locutor
                if addressee != locutor.strip(' ') and sentence == str(sentences[int(idx)]):
                    ad_list.append(addressee)

            # for each annotation, keep multiple addresses
            final_annotations[int(idx)] = "@".join(list(set(ad_list)))

    # find all sentences id with annotations
    ids_annotated = []
    for i in final_annotations.keys():
        ids_annotated.append(i)

    # apply annotations
    for i in final_annotations:
        if i in sorted(ids_annotated):
            # add addressee
            for word in sentences[i]:
                word._.addressee = final_annotations[i]


    # ## Write new alignment file
    print(f"Writing alignment file to {DATA_PLUMCOT}/{serie}/forced-alignment")
    new_file = open(f"{DATA_PLUMCOT}/{serie}/forced-alignment/{episode_to_process}.aligned", "w")

    for sentence in sentences:
        for word in sentence:
            confidence = "{:.2f}".format(word._.confidence)
            start_time = "{:.2f}".format(word._.start_time)
            end_time = "{:.2f}".format(word._.end_time)
            new_file.write(f'{episode_to_process} {word._.speaker} {start_time} {end_time} {word} {confidence} {word._.entity_linking} {word._.addressee}\n')

    new_file.close()
    print("DONE.")
