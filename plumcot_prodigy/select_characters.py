import prodigy
from prodigy.components.loaders import Audio, Video, JSONL, ImageServer
from plumcot_prodigy.forced_alignment import ForcedAlignment
from plumcot_prodigy.video import mkv_to_base64
from plumcot_prodigy.custom_loaders import *
from prodigy.components.preprocess import add_tokens, fetch_media
from prodigy.util import file_to_b64
from typing import Dict, List, Text

import random
import os
import json
import spacy
import ast


def remove_video_before_db(examples: List[Dict]) -> List[Dict]:
    """Remove (heavy) "video" and "pictures" key from examples before saving to Prodigy database
    Parameters
    ----------
    examples : list of dict
        Examples.
    Returns
    -------
    examples : list of dict
        Examples with 'video' or 'pictures' key removed.
    """
    for eg in examples:
        if "video" in eg:
            del eg["video"]
        if "video" in eg:
            del eg["options"]

    return examples

def stream_char():
        """ Annotate not_available characters
            Displays lines with "not_available" character in aligned file
            Display pictures of all the characters of the current episode
            
    Start prodigy : prodigy select_char select_characters -F plumcot_prodigy/recipes.py        
    """
    
    # path to shows directories
    path = "/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data"
    
    # load episodes list
    episodes_list = load_episodes(path)
    
    for episode in episodes_list:
        print("\nCurrent episode", episode)
        
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')        
        
        mkv, aligned, sentences = load_files(series, episode, path)
        
        if mkv == "" and aligned == "":
            continue
            
        else:            

            # credits for the current episode
            episode_characters = load_credits(episode, series, path)
            
            print("\nCHARACTERS\n")
            for idx, char in enumerate(episode_characters):
                print(idx+1, char)  

            # load pictures for the characters of the current episode
            pictures = load_photo(episode_characters, series, path)
            
            # options to load in the choice box
            options = []
            for name, val in pictures.items():
                # display photo in options
                if name != val:
                    options.append({"id":name, "image":file_to_b64(val)})
                elif name == val :                    
                    # display character's name when no picture
                    options.append({"id":name, "text": name})
            # selection for all@ and #unknown#
            options.append({"id":"all@","text": "all@"})
            options.append({"id":f"#unknown#{episode}","text":f"#unknown#{episode}"})

            #### 2. select sentences with non available characters ####
            
            # find all sentences with non available character
            sentences_choice_not_available = [(sentence, idx) for idx, sentence in enumerate(sentences) if sentence._.speaker == 'not_available' if str(sentence) != '']
            
            # take only 20% of the episode
            #random.shuffle(sentences_choice_not_available)
            #sentences_choice_not_available = sentences_choice_not_available[int(len(sentences_choice_not_available) * .00) : int(len(sentences_choice_not_available) * .20)]
            print("Sentences to annotate :", len(sentences_choice_not_available))
            count = 0
            
            for el in sentences_choice_not_available:              
                
                sentence = el[0]
                sentence_id = el[1]
                
                try :
                    if sentences.index(sentence) != 0:
                        left = sentences[sentences.index(sentence)-1]
                        right = sentences[sentences.index(sentence)+1]
                    # beug : left index = last sentence index in the list when current sentence is 0
                    else:
                        left = " "
                        right = sentences[sentences.index(sentence)+1]

                except IndexError:
                    left = " "
                    right = " "  

                # video
                if str(left) != " " and str(right) != " ":
                    start_time = left._.start_time
                    end_time= right._.end_time + 0.1
                else:
                    start_time = sentence._.start_time
                    end_time = sentence._.end_time +0.1             
                
                speaker = sentence._.speaker
                count +=1
                print(count, speaker, ':', sentence)

                # extract corresponding video excerpt
                video_excerpt = mkv_to_base64(mkv, start_time, end_time)

                yield {
                                    "video": video_excerpt,
                                   "speaker": f"{speaker}",
                                    "text": f"{sentence}",
                                    "pictures" : pictures,
                                    "options" : options,
                                    "start_time": f"{sentence._.start_time}",
                                    "end_time": f"{sentence._.end_time}",
                                    "sentence_id" : sentence_id,
                                   "meta": {"start_extract": start_time, "end_extract": end_time, 
                                            "episode": episode, "mkv_path": mkv},
                               }      

@prodigy.recipe(
    "select_char",
    dataset=("The dataset to save to", "positional", None, str),
    #file_path=("Path to texts", "positional", None, str),
)
def select_char(dataset):
        
    stream = stream_char() 
    
    return {
        "dataset": dataset,   # save annotations in this dataset
        "stream": stream,
        "before_db": remove_video_before_db,
        "view_id": "blocks",  
        "config": {
            "custom_theme": {
                "cardMaxWidth": 1500,
                "cardMinWidth": 1500,                
                            },
            #"global_css": " .c0181 {max-width : 100px;} .0156 { font-size: 15px !important; }",                       
            "blocks": [                
                {"view_id": "audio"},
                #{"view_id": "text"},
                {"view_id": "choice"}, # use the choice interface
            ],
            "audio_loop": True,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
            "choice_style":"multiple",
            # css for better alignment of the pictures
            "global_css": " .c01169 {width:50%;} .c0140 {cursor:pointer; width:60%; height:60%;} .c0156 {width:auto; font-size:15px; word-wrap: break-word; overflow-wrap: break-word; white-space: pre-wrap;} .c0163 {display: grid; grid-template-columns: repeat(10,auto); grid-gap:1px; padding: 1px;} .c0180 {max-width :100px;} .c0181 {max-width :100px;}",
        },
        
    }
