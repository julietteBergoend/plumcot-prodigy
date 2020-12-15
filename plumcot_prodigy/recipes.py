import prodigy
from prodigy.components.loaders import Audio, Video
from prodigy.components.loaders import JSONL
from plumcot_prodigy.forced_alignment import ForcedAlignment
from plumcot_prodigy.video import mkv_to_base64
from prodigy.components.preprocess import add_tokens
from typing import Dict, List, Text

import random
import os
import json
import spacy

def choose_char(characters, serie_uri, path):
    
    # open json file corresponding to the current show
    with open(os.path.join(path, f"{serie_uri}/images/images.json")) as f:
        data = json.load(f)
    # dictionary character : url to the character's picture
    char_pictures = {}
    
    for dic in data['allImages']:
        # character's name is stored in 'label'
        if 'label' in dic.keys():
            for character in characters:
                # choose an image with only one character on it
                if character in dic['label'] and len(dic['label']) ==1 and dic['msrc'] != None:
                    char_pictures[character] = dic['msrc']
    
    # characters with no picture                
    char_no_pictures = [char for char in characters if char not in char_pictures.keys() ]

    return char_pictures, char_no_pictures      

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
        elif "options" in eg:
            del eg["options"]

    return examples


def stream():

    forced_alignment = ForcedAlignment()

    # gather all episodes of all shows together
    all_episodes_series = ""
    # path to series directories
    path = "/vol/work/lerner/pyannote-db-plumcot/Plumcot/data"

    # shows' names
    with open(os.path.join(path, "series.txt")) as series_file :
        series = series_file.read()
    all_series = [serie.split(",")[0] for serie in series.split('\n') if serie != '']
    #all_series = ["BattlestarGalactica"]
    
    # shows' path
    all_series_paths = [os.path.join(path, name) for name in all_series]
    
    # read episodes.txt of each show
    for serie_name in all_series_paths:
        with open(os.path.join(serie_name,"episodes.txt")) as file:  
            episodes_file = file.read() 
            all_episodes_series += episodes_file
    
    # final list of all episodes (season x)
    episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n') if 'Season01.' in episode]
    
    for episode in episodes_list:
        print("Current Episode :", episode)

        series, _, _ = episode.split('.')

        # path to mkv
        if "Episode00" not in str(episode) and os.path.isfile(f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv") : 
            mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"
            print(mkv)
        elif "Episode00" not in str(episode) and os.path.isfile(f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv") :
            mkv = f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv" 
            print(mkv)
        else:
            print("No mkv file for", episode)
            yield { "video": video_excerpt_b,
                    "speaker": f"{speaker}",
                    "text": f"{max_beg_sentence}",
                   "meta": {"start": start_time_b, "end": end_time_b, "episode": episode, "mkv_path": "no mkv"}
                  }
            #continue
            

        # path to forced alignment -- hardcoded for now
        if os.path.isfile(os.path.join(path, f"{series}/forced-alignment/{episode}.aligned")):
            aligned = os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")
        else:
            print("No aligned file for", episode)
            #continue
            yield { "video": video_excerpt_b,
                    "speaker": f"{speaker}",
                    "text": f"{max_beg_sentence}",
                   "meta": {"start": start_time_b, "end": end_time_b, 
                            "episode": episode, "mkv_path": mkv, "aligned":"no aligned"}
                  }
            
        # load forced alignment        
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)

        # choose first and last sentences based on time length            
        begining_sentences  = {i : i._.end_time-i._.start_time for i in sentences[10:20] if i._.end_time-i._.start_time !=0}
        ending_sentences = {i : i._.end_time-i._.start_time for i in sentences[-30:] if i._.end_time-i._.start_time !=0}
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
                    "meta": {"moment": "begining sentence", "start": start_time_b, "end": end_time_b, 
                             "episode": episode, "mkv_path": mkv, "aligned":aligned},
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
                    "meta": {"moment": "ending sentence", "start": start_time, "end": end_time, 
                             "episode": episode, "mkv_path": mkv, "aligned":aligned},
                }
        
def stream_char():

    forced_alignment = ForcedAlignment()

    # gather all episodes of all shows together
    all_episodes_series = ""
    # path to shows directories
    path = "/vol/work/lerner/pyannote-db-plumcot/Plumcot/data"

    # shows' names
    with open(os.path.join(path, "series.txt")) as series_file :
        series = series_file.read()
    all_series = [serie.split(",")[0] for serie in series.split('\n') if serie != '']
    
    # shows' paths
    all_series_paths = [os.path.join(path, name) for name in all_series]
    
    # read episode.txt of each show
    for serie_name in all_series_paths:
        with open(os.path.join(serie_name,"episodes.txt")) as file:  
            episodes_file = file.read() 
            all_episodes_series += episodes_file
    
    # final list of all episodes (season x)
    episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n') if 'Season01.' in episode]
    
    for episode in episodes_list:
        print("Current episode", episode)

        series, _, _ = episode.split('.')

        # path to mkv
        if os.path.isfile(f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv") : 
            mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"
        elif os.path.isfile(f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv") :
            mkv = f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv"
        else:
            print("No mkv file for", episode)
            yield {"No mkv file for :" : episode}

        # path to forced alignment
        if os.path.isfile(os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")):
            aligned = os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")
        else:
            print("No aligned file for", episode)
            yield {"No aligned file for :" : episode}    
            
        # path to credits
        with open(os.path.join(path, f"{series}/credits.txt")) as f_c:
            credits = f_c.read()
                  
        # path to characters
        with open(os.path.join(path,f"{series}/characters.txt")) as f_ch:
            characters = f_ch.read()                  
        characters_list = [char.split(',')[0] for char in characters.split('\n') if char != '']
        
        # credits per episodes
        credits_dict = {episode.split(',')[0] : episode.split(',')[1:] for episode in credits.split('\n')}
        final_dict = {}
        for ep, credit in credits_dict.items():
            final_dict[ep] = [ch for ch, cr in zip(characters_list, credit) if cr == "1"]   
        
        # credits for the current episode
        episode_characters = final_dict[episode]
        
        # load pictures and characters without one of the current episode
        pictures, no_pictures = choose_char(episode_characters, series, path)
        
        # options to load in the choice box
        options = []
        for el in pictures.items():
            options.append({"id":el[0], "image":el[1]})
        # display character's name when no picture
        for el in no_pictures:
            options.append({"id":el, "text": el})
            
        # load forced alignment        
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)

        # select sentences with non available characters
        sentences_choice = [sentence for sentence in sentences if sentence._.speaker == "not_available" if sentence._.text != '']
        
        sentence = random.choice(sentences_choice)
        
        speaker = sentence._.speaker
        start_time = sentence._.start_time
        end_time= sentence._.end_time

        # extract corresponding video excerpt
        video_excerpt = mkv_to_base64(mkv, start_time, end_time)

        yield {
                            "video": video_excerpt,
                           "speaker": f"{speaker}",
                            "text": f"{sentence}",
                            "pictures" : pictures,
                            "no_pictures" : no_pictures,
                            "options" : options,
                           "meta": {"start": start_time, "end": end_time, "episode": episode, "mkv_path": mkv},
                       }      

def stream_text():

    forced_alignment = ForcedAlignment()

    # gather all episodes of all shows together
    all_episodes_series = ""
    # path to shows directories
    path = "/vol/work/lerner/pyannote-db-plumcot/Plumcot/data"

    # shows' names
    with open(os.path.join(path, "series.txt")) as series_file :
        series = series_file.read()
    all_series = [serie.split(",")[0] for serie in series.split('\n') if serie != '']
    
    # shows' paths
    all_series_paths = [os.path.join(path, name) for name in all_series]
    
    # read episode.txt of each show
    for serie_name in all_series_paths:
        with open(os.path.join(serie_name,"episodes.txt")) as file:  
            episodes_file = file.read() 
            all_episodes_series += episodes_file
    
    # final list of all episodes (season x)
    episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n') if 'Season01.' in episode]
    
    for episode in episodes_list:
        print("Current episode", episode)

        series, _, _ = episode.split('.')

        # path to mkv
        if os.path.isfile(f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv") : 
            mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"
        elif os.path.isfile(f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv") :
            mkv = f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv"
        else:
            print("No mkv file for", episode)
            yield {"No mkv file for :" : episode}

        # path to forced alignment
        if os.path.isfile(os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")):
            aligned = os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")
        else:
            print("No aligned file for", episode)
            yield {"No aligned file for :" : episode}    
            
        # load forced alignment        
        transcript = forced_alignment(aligned)      
        sentences = list(transcript.sents)

        # sort sentences by confidence, add unique identifier to sentences
        confidence_per_sentence = {(sentence, sentences.index(sentence)) : sentence._.confidence for sentence in sentences}
        sorted_confidence_per_sentence = {k: v for k, v in sorted(confidence_per_sentence.items(), key=lambda item: item[1])} 

        # select sentences with a confidence lower than x
        sentences_choice = [sentence[0] for sentence, confidence in sorted_confidence_per_sentence.items() if confidence < 0.3]
        
        ponct = "\'\"-.,!?"
        #print(ponct.split())
        
        for sentence in sentences_choice :
            
            if str(sentence) not in ponct and sentence._.end_time-sentence._.start_time != 0.0:
               
                #context of the sentences
                left = sentences[sentences.index(sentence)-1]
                right = sentences[sentences.index(sentence)+1]

                speaker = sentence._.speaker
                start_time = sentence._.start_time
                end_time= sentence._.end_time
                confidence = sentence._.confidence
                print(sentence, confidence)

                # extract corresponding video excerpt
                video_excerpt = mkv_to_base64(mkv, start_time, end_time)

                yield {
                                    "video": video_excerpt,
                                   "speaker": f"{speaker}",
                                    "text": f"{sentence}",
                                   "meta": {"confidence": confidence, "left context":str(left), "right context":str(right),
                                            "start": start_time, "end": end_time, "episode": episode, "mkv_path": mkv},
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
            "blocks": [                
                {"view_id": "audio"},
               
                {"view_id": "choice"}, # use the choice interface
            ],
            "audio_loop": True,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
        },
        
    }
@prodigy.recipe(
    "text_classification",
    dataset=("The dataset to save to", "positional", None, str),
    #file_path=("Path to texts", "positional", None, str),
)
def select_text(dataset, lang="en"):
    nlp = spacy.blank(lang)    
    stream = stream_text()
    stream = add_tokens(nlp, stream)

    return {
        "dataset": dataset,   # save annotations in this dataset
        "stream": stream,
        "before_db": remove_video_before_db,
        
        "view_id": "blocks",  
        "config": {
            "labels": ["DELETE", "CORRECT", "DO NOTHING"],
            "blocks": [                
                {"view_id": "audio"},
                {"view_id": "ner_manual"},
                {"view_id": "text_input"}, # use the choice interface
            ],
            "audio_loop": True,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
        },
        
    }

 

