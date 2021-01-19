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
        if "options" in eg:
            del eg["options"]
        if "pictures" in eg:
            del eg["pictures"]

    return examples


def stream():

    # path to shows directories
    path = "/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data"
    
    episodes_list = load_episodes(path)
    
    for episode in episodes_list:
            
        print("\nCurrent Episode :", episode)
        series, _, _ = episode.split('.')         
        mkv, aligned, sentences = load_files(series, episode, path)
        
        if mkv != "" and aligned != "" and sentences != "":

            # choose first and last sentences based on time length            
            begining_sentences  = {i : i._.end_time-i._.start_time for i in sentences[10:20] if i._.end_time-i._.start_time !=0}
            ending_sentences = {i : i._.end_time-i._.start_time for i in sentences[-30:] if i._.end_time-i._.start_time !=0}
            max_beg_sentence = max(begining_sentences, key=begining_sentences.get)
            max_end_sentence = max(ending_sentences, key=ending_sentences.get)

            # load its attributes from forced alignment
            speaker = max_beg_sentence._.speaker
            start_time_b = max_beg_sentence._.start_time
            end_time_b = max_beg_sentence._.end_time +0.2

            # extract corresponding video excerpt
            video_excerpt_b = mkv_to_base64(mkv, start_time_b, end_time_b)
            #print("extract video", len(video_excerpt_b))

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
            yield {
                            "video": video_excerpt_e,
                            "speaker": f"{speaker}",
                            "text": f"{max_end_sentence}",
                            "meta": {"moment": "ending sentence", "start": start_time, "end": end_time, 
                                     "episode": episode, "mkv_path": mkv, "aligned":aligned},
                        }
            
        else:# mkv == "" or aligned == "" or sentences == "":
            
            continue
            

def stream_char():
    # path to shows directories
    path = "/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data"
    
    episodes_list = load_episodes(path)
    
    for episode in episodes_list:
        print("\nCurrent episode", episode)
        
        series, _, _ = episode.split('.')        
        mkv, aligned, sentences = load_files(series, episode, path)
        
        if mkv == "" and aligned == "":
            continue
            
        else:
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
            pictures = load_photo(episode_characters, series, path)
            
            if len(episode_characters) != len(pictures):
                print("ONE OR MORE CHARACTERS W// PICTURE")
                print(len(pictures))
                print(len(episode_characters))

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

            # 1. select one sentence per speaker's name which is not in the credits
            sentences_choice_unkown = {sentence._.speaker : sentence for sentence in sentences if sentence._.speaker not in episode_characters if str(sentence) != ''}
            print(sentences_choice_unkown)
            print('\nCharacters')
            for idx, char in enumerate(episode_characters):
                print(idx, char)
            
            # display video excerpt
            for speaker, sentence in sentences_choice_unkown.items():
                if speaker != "not_available":                    
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
                        end_time= right._.end_time+0.01
                    else:
                        start_time = sentence._.start_time
                        end_time = sentence._.end_time+0.01                

                    speaker = sentence._.speaker
                    print(speaker, ':', sentence)

                    # extract corresponding video excerpt
                    video_excerpt = mkv_to_base64(mkv, start_time, end_time)

                    yield {
                                        "video": video_excerpt,
                                       "speaker": f"{speaker}",
                                        "text": f"{speaker} : {sentence}",
                                    "pictures" : pictures,
                                    "options" : options,
                                    "sentence": f"{sentence}",
                                    "start_time": f"{sentence._.start_time}",
                                    "end_time": f"{sentence._.end_time}",
                                   "meta": {"start_extract": start_time, "end_extract": end_time, 
                                            "episode": episode, "mkv_path": mkv},
                               }      
            
            # 2. select sentences with non available characters
            sentences_choice_not_available = [sentence for sentence in sentences if sentence._.speaker == 'not_available' if str(sentence) != '']
            for sentence in sentences_choice_not_available:              
                
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
                    end_time= right._.end_time
                else:
                    start_time = sentence._.start_time
                    end_time = sentence._.end_time                
                
                speaker = sentence._.speaker
                print(speaker, ':', sentence)

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
                                   "meta": {"start_extract": start_time, "end_extract": end_time, 
                                            "episode": episode, "mkv_path": mkv},
                               }      

def stream_text():
    
    # path to shows directories
    path = "/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data"
    
    episodes_list = load_episodes(path)
    
    for episode in episodes_list:
        print("\nCurrent Episode :", episode)

        series, _, _ = episode.split('.')        
        mkv, aligned, sentences = load_files(series, episode, path)
        
        if mkv == "" and aligned == "":
            continue
            
        else:
            # sort sentences by confidence, add unique identifier to sentences
            confidence_per_sentence = {(sentence, sentences.index(sentence)) : sentence._.confidence for sentence in sentences}
            sorted_confidence_per_sentence = {k: v for k, v in sorted(confidence_per_sentence.items(), key=lambda item: item[1])} 

            # select sentences with a confidence lower than x
            sentences_choice = [sentence[0] for sentence, confidence in sorted_confidence_per_sentence.items() if  confidence <= 0.5 ]

            ponct = "\'\"-.,!?<>/"

            for sentence in sentences_choice :

                if str(sentence) not in ponct and sentence._.end_time-sentence._.start_time != 0.0:
                    
                    # context of the sentences, if exists
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
                        end_time= right._.end_time+0.01
                        #print(sentence._.end_time-sentence._.start_time)
                    else:
                        start_time = sentence._.start_time
                        end_time = sentence._.end_time+0.01
                        #print('here',sentence._.end_time-sentence._.start_time)

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
                                       "meta": {"confidence": confidence, "start": start_time, 
                                                "end": end_time, "episode": episode, "mkv_path": mkv},
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
            "choice_style":"multiple",
        },
        
    }
@prodigy.recipe(
    "text_classification",
    dataset=("The dataset to save to", "positional", None, str),
    #file_path=("Path to texts", "positional", None, str),
)

        
        
def select_text(dataset, lang="en"):      

    def disable_left_right(stream, lang="en"):   
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
                
    stream = stream_text()   
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
                {"view_id": "text_input"}, # use the choice interface
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