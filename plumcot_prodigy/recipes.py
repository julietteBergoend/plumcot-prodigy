import prodigy
from plumcot_prodigy.forced_alignment import ForcedAlignment
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text

import random
import os

# test
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
    # list containing all the series names
    all_series = ["TheBigBangTheory"] 

    # series path
    all_series_paths = [os.path.join(path, name) for name in all_series]
    
    # read episodes.txt of each serie containing episodes list
    for serie_name in all_series_paths:
        with open("/vol/work1/bergoend/episodes.txt") as file:  
            episodes_file = file.read() 
            all_episodes_series += episodes_file
    
    # final list of all episodes
    #episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n')]
    episodes_list = ["TheBigBangTheory.Season01.Episode04", "TheBigBangTheory.Season01.Episode05"]
    
    for episode in episodes_list:    
        series, _, _ = episode.split('.')

        # path to mkv -- hardcoded for now
        mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"

        # path to forced alignment -- hardcoded for now
        aligned = f"/vol/work/lerner/pyannote-db-plumcot/Plumcot/data/{series}/forced-alignment/{episode}.aligned"

        # load forced alignment        
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)

        # select the first and the last sentences of the episode
        sentence_begining = sentences[0]
        sentence_end = sentences[-1]

        # load its attributes from forced alignment
        speaker = sentence_begining._.speaker
        print(speaker)
        start_time_b = sentence_begining._.start_time
        print(start_time_b)
        end_time_b = sentence_begining._.end_time
        print(end_time_b)

        # extract corresponding video excerpt
        video_excerpt_b = mkv_to_base64(mkv, start_time_b, end_time_b)

        yield {
            "video": video_excerpt_b,
            "text": f"{speaker}: {sentence_begining}",
            "meta": {"start": start_time_b, "end": end_time_b, "episode": episode},
        }

        # load its attributes from forced alignment
        speaker = sentence_end._.speaker
        print(speaker)
        start_time = sentence_end._.start_time
        print(start_time)
        end_time = sentence_end._.end_time
        print(end_time)

        # extract corresponding video excerpt
        video_excerpt_e = mkv_to_base64(mkv, start_time, end_time)
        #print("Extrait video", type(video_excerpt))

        yield {
            "video": video_excerpt_e,
            "text": f"{speaker}: {sentence_end}",
            "meta": {"start": start_time, "end": end_time, "episode": episode},
        }


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
