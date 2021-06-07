import prodigy
from prodigy.components.preprocess import add_tokens, split_sentences
from plumcot_prodigy.custom_loaders import *
import requests
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text, Union
from typing_extensions import Literal
import spacy
from pathlib import Path

# path to shows directories
PATH = "/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data"

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

def entity_linking():
    
    # load episode
    episodes_list = load_episodes(PATH)
    #episodes_list = ["BuffyTheVampireSlayer.Season01.Episode12"]
    
    for episode in episodes_list:
        print("\nCurrent Episode :", episode)
        
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')
            
        # load mkv, aligned file & aligned sentences
        mkv, aligned, sentences = load_files(series, episode, PATH)

        #######sentences = ["In the name of The King Robert Baratheon", "My name is Juliet\n", "The cat is eating", "My cat is my best friend, he is kind\n", "The frog is eating", "Her name is Kristie\n", "The wolf is eating"]

        #######name_dict = {"juliet": ["juliet_berg"], "robert":["robert_baratheon"], 
                     #"baratheon" : ["robert_baratheon", "joffrey_baratheon"], "kristie": ["kristie"]}

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
                #print(token, token.pos_)
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
                            spans.append({"start" : dic["start"], "end" : dic["end"], "token_start": position, "token_end":position, "label": "EL"})

                to_return["spans"] = spans  

                # get characters of the show
                with open(f"/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data/{series}/characters.txt", "r") as f:
                    speakers = [line.split(",")[0] for line in f.readlines()]
                    
                # get video
                try :
                    if i not in range(0,1):
                        start_left = sentences[i-1]
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

                # extract corresponding video excerpt
                video_excerpt = mkv_to_base64(mkv, start_time, end_time+0.01)

                to_return["field_id"] = "entity",
                to_return["field_placeholder"] = "firstname_lastname",
                to_return["field_rows"] =  1,
                #to_return["field_autofocus"] = False,
                to_return["field_suggestions"] = speakers
                to_return["sentence"] = str(j[1])
                to_return["start_time"] = j[1]._.start_time
                to_return["end_time"] = j[1]._.end_time
                to_return["meta"] = {"episode": episode, "sentence_id": f"{i}", "processing":f"{i}/{len(sentences)}"}
                to_return["video"] = video_excerpt
                yield to_return
    

@prodigy.recipe("entity_linking")
def addresse(dataset):
    
    blocks = [
        {"view_id": "audio"}, {"view_id": "relations"},{"view_id": "text_input"},
    ]
    stream = entity_linking()
    
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
            "relations_span_labels" : ["EL", "EL2", "EL3"],
            "field_autofocus" : False,            
        },
    }


    

