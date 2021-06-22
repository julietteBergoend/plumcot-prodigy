import prodigy
from prodigy.components.preprocess import add_tokens, split_sentences
from plumcot_prodigy.custom_loaders import *
import requests
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text, Union
from typing_extensions import Literal
import spacy
from pathlib import Path

""" Annotate entity linking (3rd person & names)
        
        Displays sentences with tokens to annotate
        If the token is an entity linking, write the name of the corresponding character in the text input of Prodigy
        
        Arguments : ep : episode to annotate (e.g TheWalkingDead.Season01.Episode01),
            
    Start prodigy : prodigy entity_linking entity_data <episode_name> <path_to_corpora> -F plumcot_prodigy/entity.py     

"""
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
        if 'field_suggestions' in eg:
            del eg['field_suggestions']

    return examples

def entity_linking(episode, user_path):
    
    DATA_PLUMCOT = user_path
    
    show = episode.split('.')[0]
    season = episode.split('.')[1]
    ep= episode.split('.')[2]
    
    # load episode
    episodes_list = [episode]
    
    for episode in episodes_list:
        print("\nCurrent Episode :", episode)
        
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')
            
        # load mkv, aligned file & aligned sentences
        mkv, aligned, sentences = load_files(series, episode, DATA_PLUMCOT)

        # criteria : nouns or pronouns to display automaticaly
        pronouns = ["he", "she", "his", "her", "himself", "herself", "him"]
        nouns = ["mother", "son", "daughter", "wife", "husband", "father", "uncle", "cousin", "aunt", "brother", "sister"]

        # store sentence id with criteria position(s) (PROPN or criteria list)
        store_ids = {}

        # labels to feed in Prodigy
        labels = []

        # for each sentence with criteria, store idx and positions
        for idx, sentence in enumerate(sentences) :

            # store word position with criteria
            store_position = []

            for token in sentence:
                # check if it is a PRON or DET
                if str(token).lower() in pronouns :
                        
                    # check if entity_linking field is empty
                    if token._.entity_linking == "_" or token._.entity_linking == "?":
                        store_position.append(str(sentence).split().index(str(token)))

                # check if it is a name    
                if token.pos_ == "PROPN":                     
                    if str(token) != "ve" and str(token) != "m" and str(token)[0].isupper():
                    
                        # check if entity_linking field is empty
                        if token._.entity_linking == "_" or token._.entity_linking == "?":
                            store_position.append(str(sentence).split().index(str(token)))
               
                # check if it is in nouns
                if str(token).lower() in nouns :
                    # check if entity_linking field is empty
                    if token._.entity_linking == "_" or token._.entity_linking == "?":
                        store_position.append(str(sentence).split().index(str(token)))

            # keep sentence id, tokens positions, sentence id
            store_ids[idx] = (store_position, sentence)

        # process sentences for prodigy
        for i,j in store_ids.items():

            to_return = {"text":''}

            # tokens displayed in Prodigy
            tokens = []

            # spans for EL
            spans = []

            # character counter in the text
            start = 0

            # word id
            ids = 0
  
            #if previous != None and nexts != None:
            if j[0]:
                #print(sentences[i])
                to_return['text'] += str(sentences[i])
                print(i, to_return['text'])

                # get tokens
                for word in str(sentences[i]).split(' '):
                    # do no add +1 to start counter for last word
                    if "\n" in word : 
                        tokens.append({"text": str(word), "start": start , "end": len(str(word))+start-1, "id": ids, "ws": True})

                    else : 
                        tokens.append({"text": str(word), "start": start , "end": len(str(word))+start, "id": ids, "ws": True})
                        start+= len(str(word))+1
                    # change start token for next word
                    ids+=1

                to_return["tokens"] = tokens

                # get spans
                for position in j[0]:
                    for dic in tokens:
                        if position == dic["id"]:
                            #print("FIND TOKEN",dic["text"])
                            #print(dic["start"], dic["end"])
                            corresponding_token = to_return["text"][dic["start"]:dic["end"]].lower()
                            spans.append({"start" : dic["start"], "end" : dic["end"], "token_start": position, "token_end":position, "label": "EL1"})

                to_return["spans"] = spans  

                # get characters of the show
                with open(f"{DATA_PLUMCOT}/{series}/characters.txt", "r") as f:
                    speakers = [line.split(",")[0] for line in f.readlines()]
                    
                # get video (add context)
                try :
                    if i not in range(0,2):
                        start_left = sentences[i-2]
                        end_left = sentences[i]
                        # beug : left index = last sentence index in the list when current sentence is 0
                    else:
                        start_left = None
                        end_left = sentences[i]

                except IndexError:
                    start_left = None
                    end_left = None  

                # video
                if start_left != None and end_left != None:
                    start_time = start_left._.start_time
                    end_time= end_left._.end_time +0.1 
                else:
                    start_time = j[1]._.start_time
                    end_time = j[1]._.end_time +0.1 

                # corresponding video excerpt
                video_excerpt = mkv_to_base64(mkv, start_time, end_time+0.01)

                to_return["field_id"] = "entity",
                to_return["field_placeholder"] = "firstname_lastname",
                to_return["field_rows"] =  1,
                to_return["field_suggestions"] = speakers
                to_return["sentence"] = str(j[1])
                to_return["start_time"] = j[1]._.start_time
                to_return["end_time"] = j[1]._.end_time
                to_return["meta"] = {"episode": episode, "sentence_id": f"{i}", "processing":f"{i}/{len(sentences)}"}
                to_return["video"] = video_excerpt
                yield to_return
    

@prodigy.recipe("entity_linking",
               dataset=("The dataset to save to", "positional", None, str),
               episode=("Episode to annotate (e.g : TheWalkingDead.Season01.Episode01", "positional", None, str),
               user_path=("Path to Plumcot corpora", "positional", None, str),
               )
def addresse(dataset: Text, episode: Text, user_path: Text) -> Dict:
    
    blocks = [
        {"view_id": "audio"}, {"view_id": "relations"},{"view_id": "text_input", "field_id": "input_1", "field_placeholder":"Type here for EL1..."},{"view_id": "text_input", "field_id": "input_2", "field_placeholder":"Type here for EL2..."}, {"view_id": "text_input", "field_id": "input_3", "field_placeholder":"Type here for EL3..."},
    ]
    stream = entity_linking(episode, user_path)
    
    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": stream,  
        "before_db": remove_video_before_db,
        "config": {
            "blocks": blocks,
            "wrap_relations" : True, # apply line breaks
            "hide_newlines": True,
            "audio_loop": False,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
            "relations_span_labels" : ["EL1", "EL2", "EL3"],
            "field_autofocus" : False,            
        },
    }


    

