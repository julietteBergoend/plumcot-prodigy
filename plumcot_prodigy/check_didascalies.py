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

    return examples


def stream_text(episode, conf, user_path):
    """ Displays sentences with confidence index under conf argument.
    
        Arguments : ep : episode to annotate,
                    conf : float number corresponding to confidence of sentences
    
        Start prodigy : prodigy check_didascalies.py correction_data <show_name> <season> <episode> <confidence_index> -F plumcot_prodigy/check_didascalies.py
    """
    
    # path to Plumcot data
    DATA_PLUMCOT = user_path
    
    # process serie or film
    if len(episode.split('.')) == 3:
        series, _, _ = episode.split('.')
    elif len(episode.split('.')) == 2:
        series, _ = episode.split('.')
    
    # load episodes list
    episodes_list = load_episodes(DATA_PLUMCOT, episode)
    
    for episode in episodes_list:
        print("\nCurrent Episode :", episode)
        print("Confidence index :", conf)
            
        mkv, aligned, sentences = load_files(series, episode, DATA_PLUMCOT)
        
        if mkv == "" and aligned == "":
            continue
            
        else:
            # sort sentences by confidence, add unique identifier to sentences
            confidence_per_sentence = {(sentence, sentences.index(sentence)) : sentence._.confidence for sentence in sentences}
            sorted_confidence_per_sentence = {k: v for k, v in sorted(confidence_per_sentence.items(), key=lambda item: item[1])} 
            # select sentences with a confidence lower than x
            sentences_choice = [(sentence[0], sentence[1]) for sentence, confidence in sorted_confidence_per_sentence.items() if  confidence <= conf ]
            ponct = "\'\"-.,!?<>/"

            for sentence, idx in sentences_choice :

                # be aware of video excerpt of len(0)
                if str(sentence) not in ponct and sentence._.end_time-sentence._.start_time != 0.0:
                    
                    # context of the sentences, if exists
                    try :
                        if sentences.index(sentence) != 0:
                            left = sentences[idx-1]
                            right = sentences[idx+1]
                        # beug : left index = last sentence index in the list when current sentence is 0
                        else:
                            left = " "
                            right = sentences[idx+1]

                    except IndexError:
                        left = " "
                        right = " "  

                    # video
                    if str(left) != " " and str(right) != " ":
                        start_time = left._.start_time -2.00
                        end_time= right._.end_time+2.00
                    else:
                        start_time = sentence._.start_time
                        end_time = sentence._.end_time+0.01

                    speaker = sentence._.speaker
                    confidence = sentence._.confidence
                    print(sentence, confidence)

                    # extract corresponding video excerpt
                    video_excerpt = mkv_to_base64(mkv, start_time, end_time)

                    yield {
                                        "video": video_excerpt,
                                       "speaker": f"{speaker}",
                                        "text": f"{sentence}",
                                        "left": f"{left}",
                                        "right": f"{right}",
                                        "sentence_id" : idx,
                                       "meta": {"confidence": confidence, "start": start_time, 
                                                "end": end_time, "episode": episode, "mkv_path": mkv},
                                   }
                    
@prodigy.recipe(
    "check_didascalies",
    dataset=("The dataset to save to", "positional", None, str),
    episode=("Episode to annotate (e.g : TheWalkingDead.Season01.Episode01)", "positional", None, str),
    conf=("Display sentences under this confidence score", "positional", None, float),
    user_path=("Path to corpus directory", "positional", None, str),
)
     
def select_text(dataset: Text, episode: Text, conf: float, user_path : Text) -> Dict:      

    def disable_left_right(stream, lang="en"):  
        """
        Enable selection of context sentences
        """
        nlp = spacy.blank(lang)
        
        for eg in stream :
            
            # new token list for ner_manual
            token_list = []
            
            # add tags to left and right contexts
            left = ' '.join(["<L>" + token.text for token in nlp(str(eg["left"]))])
            right = ' '.join(["<R>" + token.text for token in nlp(str(eg["right"]))])
            
            # gather left and right contexts with initial sentence
            sentence = eg["text"]
            text = left + "\n" + sentence + "\n" + right
  
            # assign an id to each token for efficient highlighting 
            tokens = text.split()
            for (idx, token) in enumerate(tokens):
                # disable hightlighting for context sentences
                if '<L>' in token :
                    token_list.append({"text": token.strip("<L>"), "id":idx, "disabled":True, "ws":True})
                elif '<L>' not in token and '<R>' not in token:                        
                    token_list.append({"text": token, "id":idx, "disabled":False, "ws":True})
                elif '<R>' in token :
                    token_list.append({"text": token.strip("<R>"), "id":idx, "disabled":True, "ws":True})

            eg["sentence"] = sentence
            eg["tagged_context"] = text
            eg["text"] = text.replace("<L>", "").replace("<R>", "")
            eg["tokens"] = token_list

            yield eg
                
    #stream
    stream = stream_text(episode, conf, user_path)   
    stream = disable_left_right(stream) 

    return {
        "dataset": dataset,
        "stream": stream,
        "before_db": remove_video_before_db,        
        "view_id": "blocks",  
        "config": {
            "labels": ["DELETE"],
            "blocks": [  
                {"view_id": "audio"},
                {"view_id": "ner_manual"},
            ],
            "allow_newline_highlight": False,
            "audio_loop": True,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
            "show_flag": True,
        },
        
    }