import prodigy
from prodigy.components.loaders import Audio, Video, JSONL, ImageServer
from plumcot_prodigy.forced_alignment import ForcedAlignment
from plumcot_prodigy.video import mkv_to_base64
from plumcot_prodigy.custom_loaders import *
from prodigy.components.preprocess import add_tokens, fetch_media
from prodigy.util import file_to_b64
from typing import Dict, List, Text
from pathlib import Path

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

    return examples

def stream(show_name, season):
    """ Displays one excerpt from the begining of the current episode, and one from the end.  
        The aim is to check if the text in the begining and the end of the episode corresponds with the video.
    
        Arguments :show : show name (e.g Lost), 
                   season : season to annotate (e.g Season01), 
    
        Start prodigy : prodigy check_forced_alignment data_alignment <show_name> <season> -F plumcot_prodigy/check_alignment.py

        Displays begining and ending excerpts of each episode in the shows
    """
    # path to Plumcot
    DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"
    
    # load episodes list
    episodes_list = load_episodes(DATA_PLUMCOT, show_name, season, None)
    
    for episode in episodes_list:
            
        print("\nCurrent Episode :", episode)
        
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')
            
            
        # load mkv file and aligned sentences    
        mkv, aligned, sentences = load_files(series, episode, DATA_PLUMCOT)
        
        if mkv != "" and aligned != "" and sentences != "":

            # choose first and last sentences based on time length            
            begining_sentences  = {i : i._.end_time-i._.start_time for i in sentences[10:20] if i._.end_time-i._.start_time !=0}
            ending_sentences = {i : i._.end_time-i._.start_time for i in sentences[-30:] if i._.end_time-i._.start_time !=0}
            max_beg_sentence = max(begining_sentences, key=begining_sentences.get)
            max_end_sentence = max(ending_sentences, key=ending_sentences.get)
            print(max_beg_sentence, '\n', max_end_sentence)
            
            # load its attributes from forced alignment
            speaker = max_beg_sentence._.speaker
            start_time_b = max_beg_sentence._.start_time
            end_time_b = max_beg_sentence._.end_time +0.2

            # extract corresponding video excerpt
            video_excerpt_b = mkv_to_base64(mkv, start_time_b, end_time_b)

            # yield the begining excerpt
            yield {
                            "video": video_excerpt_b,
                            "speaker": f"{speaker}",
                            "text": f"{max_beg_sentence}",
                            "meta": {"moment": "begining sentence", "start": start_time_b, "end": end_time_b, 
                                     "episode": episode, "mkv_path": mkv, "aligned":aligned},
                        }
            
            # load its attributes from forced alignment
            speaker = max_end_sentence._.speaker
            start_time = max_end_sentence._.start_time - 0.2
            end_time = max_end_sentence._.end_time
            # extract corresponding video excerpt
            video_excerpt_e = mkv_to_base64(mkv, start_time, end_time)
            
            # yield the ending excerpt
            yield {
                            "video": video_excerpt_e,
                            "speaker": f"{speaker}",
                            "text": f"{max_end_sentence}",
                            "meta": {"moment": "ending sentence", "start": start_time, "end": end_time, 
                                     "episode": episode, "mkv_path": mkv, "aligned":aligned},
                        }
            
        else:
            
            continue
            
            
@prodigy.recipe(
    "check_forced_alignment",
    dataset=("Dataset to save annotations to", "positional", None, str),
    show=("Name of the show to annotate", "positional", None, str),
    season=("Season to annotate (e.g : Season01)", "positional", None, str),
)
def plumcot_video(dataset: Text, show: Text, season: Text) -> Dict:
    return {
        "dataset": dataset,
        "stream": stream(show, season),
        "before_db": remove_video_before_db,
        "view_id": "blocks",
        "config": {
            "blocks": [
                {"view_id": "audio"},
                {"view_id": "text"},
            ],
            "audio_loop": True,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
        },
    }