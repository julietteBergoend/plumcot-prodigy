import prodigy
from prodigy.components.loaders import Audio, Video
from prodigy.components.loaders import JSONL
from plumcot_prodigy.forced_alignment import ForcedAlignment
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text

import random
import os

def remove_video_before_db(examples: List[Dict]) -> List[Dict]:
    """Remove (heavy) "video" key from examples before saving to Prodigy database

    Parameters
    ----------
    examples : list of dict
        Examples.

    Returns
    -------
    examples : list of dict
        Examples with 'video' key removed.
    """
    for eg in examples:
        if "video" in eg:
            del eg["video"]

    return examples


def stream():

    forced_alignment = ForcedAlignment()

    # gather all episodes of all series together
    all_episodes_series = ""
    # path to series directories
    path = "/vol/work/lerner/pyannote-db-plumcot/Plumcot/data"

    # series names
    with open("/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data/series.txt") as series_file :
        series = series_file.read()
    all_series = [serie.split(",")[0] for serie in series.split('\n') if serie != '']
    
    # series path
    all_series_paths = [os.path.join(path, name) for name in all_series]
    
    # read file_list.txt of each serie containing existing episodes list
    for serie_name in all_series_paths:
        with open(os.path.join(serie_name,"file_list.txt")) as file:  
            episodes_file = file.read() 
            all_episodes_series += episodes_file
    
    # final list of all episodes (season x)
    episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n') if 'Season01.' in episode]
    #episodes_list = ["TheBigBangTheory.Season01.Episode04", "TheBigBangTheory.Season01.Episode05"]
    
    for episode in episodes_list:
        print("Episode en cours", episode)

        series, _, _ = episode.split('.')

        # path to mkv -- hardcoded for now
        if os.path.isfile(f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv") : 
            mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"
        else:
            mkv = f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv"

        # path to forced alignment -- hardcoded for now
        aligned = f"/vol/work/lerner/pyannote-db-plumcot/Plumcot/data/{series}/forced-alignment/{episode}.aligned"
        # load forced alignment        
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)

        # choose first and last sentences based on time length            
        begining_sentences  = {i : i._.end_time-i._.start_time for i in sentences[0:10]}
        ending_sentences = {i : i._.end_time-i._.start_time for i in sentences[-10:]}
        max_beg_sentence = max(begining_sentences, key=begining_sentences.get)
        max_end_sentence = max(ending_sentences, key=ending_sentences.get)

        # load its attributes from forced alignment
        speaker = max_beg_sentence._.speaker
        start_time_b = max_beg_sentence._.start_time
        end_time_b = max_beg_sentence._.end_time

        # extract corresponding video excerpt
        video_excerpt_b = mkv_to_base64(mkv, start_time_b, end_time_b)

        yield {
                    "video": video_excerpt_b,
                    "speaker": f"{speaker}",
                    "text": f"{max_beg_sentence}",
                    "meta": {"start": start_time_b, "end": end_time_b, "episode": episode, "mkv_path": mkv},
                }
        # load its attributes from forced alignment
        speaker = max_end_sentence._.speaker
        start_time = max_end_sentence._.start_time
        end_time = max_end_sentence._.end_time

        # extract corresponding video excerpt
        video_excerpt_e = mkv_to_base64(mkv, start_time, end_time)

        yield {
                    "video": video_excerpt_e,
                    "speaker": f"{speaker}",
                    "text": f"{max_end_sentence}",
                    "meta": {"start": start_time, "end": end_time, "episode": episode, "mkv_path": mkv},
                }
        
"""        
def stream_chars():

    forced_alignment = ForcedAlignment()
    
    # gather all episodes of all series together
    all_episodes_series = ""
    # path to series directories
    path = "/vol/work/lerner/pyannote-db-plumcot/Plumcot/data"

    # series names
    with open("/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data/series.txt") as series_file :
        series = series_file.read()
    all_series = [serie.split(",")[0] for serie in series.split('\n') if serie != '']
    
    # series path
    all_series_paths = [os.path.join(path, name) for name in all_series]
    
    # read file_list.txt of each serie containing existing episodes list
    for serie_name in all_series_paths:
        with open(os.path.join(serie_name,"file_list.txt")) as file:  
            episodes_file = file.read() 
            all_episodes_series += episodes_file
    
    # final list of all episodes (season x)
    episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n') if 'Season01.' in episode]
    #episodes_list = ["TheBigBangTheory.Season01.Episode04", "TheBigBangTheory.Season01.Episode05"]
    
    for episode in episodes_list:
        print("Episode en cours", episode)

        series, _, _ = episode.split('.')

        # path to mkv -- hardcoded for now
        if os.path.isfile(f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv") : 
            mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"
        else:
            mkv = f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv"

        # path to forced alignment -- hardcoded for now
        aligned = f"/vol/work/lerner/pyannote-db-plumcot/Plumcot/data/{series}/forced-alignment/{episode}.aligned"
        # load forced alignment        
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)

        sentence = random.choice(sentences)

        # load its attributes from forced alignment
        speaker = sentence._.speaker
        start_time = sentence._.start_time
        end_time = sentence._.end_time

        # extract corresponding video excerpt
        video_excerpt = mkv_to_base64(mkv, start_time, end_time)

        # Load the directory of audio files and add options to each task
        stream = Video(video_excerpt)
        for eg in stream:
            eg["options"] = [
                {"id": "CAR", "text": "🚗 Car"},
                {"id": "PLANE", "text": "✈️ Plane"},
                {"id": "OTHER", "text": "Other / Unclear"}
            ]
            yield eg
"""

@prodigy.recipe(
    "check_forced_alignment",
    dataset=("Dataset to save annotations to", "positional", None, str),
)
def plumcot_video(dataset: Text) -> Dict:
    return {
        "dataset": dataset,
        "stream": stream(),
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

@prodigy.recipe(
    "select_char",
    dataset=("The dataset to save to", "positional", None, str),
    #file_path=("Path to texts", "positional", None, str),
)
def select_char(dataset):
  

    return {
        "dataset": dataset,   # save annotations in this dataset
        "stream": stream,
        "before_db": remove_video_before_db,
        "view_id": "blocks",  # use the choice interface
        "config": {
            "blocks": [                
                {"view_id": "audio"},
               
                {"view_id": "choice"},
            ],
            "audio_loop": True,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
        },
        
    }

def add_options(stream):
    # Helper function to add options to every task in a stream
    options = [
            {"id": "happy", "text": "😀 happy"},
            {"id": "sad", "text": "😢 sad"},
            {"id": "angry", "text": "😠 angry"},
            {"id": "neutral", "text": "😶 neutral"},
        ]
    for task in stream:
        task["options"] = options
        yield task
        
stream = stream()    # load in the JSONL file
stream = add_options(stream)  # add options to each task



