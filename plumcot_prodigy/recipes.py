import prodigy
from plumcot_prodigy.forced_alignment import ForcedAlignment
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text

import random


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

    for episode in [
        "TheBigBangTheory.Season01.Episode14",
    ]:

        series, _, _ = episode.split('.')
        
        # path to mkv -- hardcoded for now
        mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"

        # path to forced alignment -- hardcoded for now
        aligned = f"/vol/work1/bergoend/point_prodigy/plumcot-prodigy/{episode}.aligned"

        # load forced alignment
        transcript = forced_alignment(aligned)
        sentences = list(transcript.sents)

        while True:

            # choose one sentence randomly
            sentence = random.choice(sentences)

            # load its attributes from forced alignment
            speaker = sentence._.speaker
            start_time = sentence._.start_time
            end_time = sentence._.end_time

            # extract corresponding video excerpt
            video_excerpt = mkv_to_base64(mkv, start_time, end_time)

            yield {
                "video": video_excerpt,
                "text": f"{speaker}: {sentence}",
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