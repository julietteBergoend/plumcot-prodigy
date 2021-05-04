import prodigy
from prodigy.components.preprocess import add_tokens, split_sentences
from plumcot_prodigy.custom_loaders import *
import requests
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text
from pathlib import Path

# path to shows directories
#PATH = "/vol/work1/bergoend/pyannote-db-plumcot/Plumcot/data"
#PATH = "/vol/work1/bergoend/point_prodigy/plumcot-prodigy"
PATH = Path(__file__).parent.absolute()

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

def relations(liste):
    """
    Create relations list to pre-select relations
    """
    locutors = [el[0] for el in liste]
    #print(set(locutors))

    relations_list = []
    
    for idx, i in enumerate(liste):
        locutor = i[0]
        sentence = i[1]

        # if there is more than one locutor
        if liste and len(set(locutors)) > 1:
            
            # 1st element
            if idx == 0 :                
                # if next element locutor != current locutor, auto select this addressee
                if liste[idx+1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+1][0]))) 
                # if 3rd element != current 1st element
                elif liste[idx+2][0] != liste[idx][0]:                        
                    relations_list.append((locutor, (sentence, liste[idx+2][0])))
                elif liste[idx+3][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+3][0])))
                elif liste[idx+4][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+4][0])))                     

            # 2nd element
            if idx == 1:
                # if 1st element != 2nd element
                if liste[idx-1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx-1][0])))                
                elif liste[idx+1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+1][0])))
                elif liste[idx+2][0] != liste[idx][0]:                        
                    relations_list.append((locutor, (sentence, liste[idx+2][0])))
                elif liste[idx+3][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+3][0])))
            
            if idx == 2:
                if liste[idx-1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx-1][0])))                
                elif liste[idx-2][0] != liste[idx][0]:  
                    relations_list.append((locutor, (sentence, liste[idx-2][0])))
                elif liste[idx+1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+1][0])))
                elif liste[idx+2][0] != liste[idx][0]:                        
                    relations_list.append((locutor, (sentence, liste[idx+2][0])))
                        
            if idx == 3:
                if liste[idx-1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx-1][0])))
                elif liste[idx-2][0] != liste[idx][0]:  
                    relations_list.append((locutor, (sentence, liste[idx-2][0])))
                elif liste[idx-3][0] != liste[idx][0]:  
                    relations_list.append((locutor, (sentence, liste[idx-3][0])))
                elif liste[idx+1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+1][0])))
                        
            if idx == 4:
                if liste[idx-1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx-1][0])))
                elif liste[idx-2][0] != liste[idx][0]:  
                    relations_list.append((locutor, (sentence, liste[idx-2][0])))
                elif liste[idx-3][0] != liste[idx][0]:  
                    relations_list.append((locutor, (sentence, liste[idx-3][0])))
                elif liste[idx-4][0] != liste[idx][0]:  
                    relations_list.append((locutor, (sentence, liste[idx-4][0])))

    # [(locutor, (sentence with addressee, addressee), ...]    
    return relations_list

def speech_turns():
    
    # load episode
    #episodes_list = load_episodes(PATH)
    episodes_list = ["TheOffice.Season01.Episode02"]
    
    # speakers labels when speaker is not in displayed sentences
    episode_speakers = []

    for episode in episodes_list:
        print("\nCurrent Episode :", episode)
        
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')
         
        # load mkv, aligned file & aligned sentences
        mkv, aligned, sentences = load_files(series, episode, PATH)
        
        # ignore empty files
        if mkv == "" and aligned == "":
            continue
            
        else:
            # credits of the episode 
            speech_turns = list()

            # create speaker / sentence groups
            for idx, sentence in enumerate(sentences):
                
                # keep track of the sentence's id in alignment file
                speech_turns.append( ( (idx, sentence), (sentence._.speaker, str(sentence)) ) )
                episode_speakers.append(sentence._.speaker)   

            # process sentences 3 by 3
            for slices in range(0, len(speech_turns), 5):
                #print("\n", speech_turns[slices:slices+5])
                
                # sentence & speaker container for relations
                s = []
                
                # append text and speaker data to s
                for idx_sent, speaker_sent in speech_turns[slices:slices+5]:

                    if len(speech_turns[slices:slices+5]) ==5:
                        
                        first = {"sentence": str(speech_turns[slices:slices+5][0][0][1]), "speaker": str(speech_turns[slices:slices+5][0][1][0]), "id": str(speech_turns[slices:slices+5][0][0][0])}
                        
                        second = {"sentence": str(speech_turns[slices:slices+5][1][0][1]), "speaker": str(speech_turns[slices:slices+5][1][1][0]), "id": str(speech_turns[slices:slices+5][1][0][0])}
                        
                        third = {"sentence": str(speech_turns[slices:slices+5][2][0][1]), "speaker": str(speech_turns[slices:slices+5][2][1][0]), "id": str(speech_turns[slices:slices+5][2][0][0])}
                        
                        fourth = {"sentence": str(speech_turns[slices:slices+5][3][0][1]), "speaker": str(speech_turns[slices:slices+5][3][1][0]), "id": str(speech_turns[slices:slices+5][3][0][0])}
                        
                        fifth = {"sentence": str(speech_turns[slices:slices+5][4][0][1]), "speaker": str(speech_turns[slices:slices+5][4][1][0]), "id": str(speech_turns[slices:slices+5][4][0][0])}

                        s.append({"text": speaker_sent[1], "meta": {"speaker": speaker_sent[0], "aligned": idx_sent[1]} })
                    else:
                        print("DONE.")
                                
                # text data to return to Prodigy
                to_return = {'text': ''}

                # for each speech turn, create an interpretable dictionary for Prodigy
                # in order to display it in the interface
                for idx, el in enumerate(s) :
                    speaker = el["meta"]["speaker"]
                    sentence = el["text"]

                    # full text to return
                    to_return["text"] += f"{speaker} {sentence}\n"
                    #to_return["text"] += f"{el["meta"]["speaker"]} {el["text"]}\n"
                
                # tokens displayed in Prodigy
                tokens = []
                # spans for speakers
                spans = []
                # character counter in the text
                start = 0
                
                # append tokens for : speaker, sentence & line break
                if len(s) == 5:
                    
                    # 1ST SENTENCE
                    sentence = s[0]["text"]
                    speaker = s[0]["meta"]["speaker"]
                    tokens.append({"text": speaker, "start": 0, "end": len(speaker), "id": 0, "ws": True})
                    tokens.append({"text": sentence, "start": len(speaker) +1 , "end": len(speaker) + len(sentence), "id": 1, "ws": True})
                    tokens.append({"text": "\n", "start": len(speaker) + len(sentence)+1 , "end": len(speaker) + len(sentence)+1, "id": 2, "ws": False})                            

                    # speaker's span
                    spans.append({"start": 0, "end": len(speaker), "token_start": 0, "token_end": 0, "label": "speaker",})
                    # start for the next sentence
                    start = len(speaker) + len(sentence)+2
                    
                    # 2ND SENTENCE
                    sentence = s[1]["text"]
                    speaker = s[1]["meta"]["speaker"]                   
                    tokens.append({"text": speaker, "start": start, "end": start + len(speaker), "id": 3, "ws": True})
                    tokens.append({"text": sentence, "start": start + len(speaker)+1 , "end": start + len(speaker) + len(sentence), "id": 4, "ws": True, "style" : {"background": "#ff6666"}})
                    tokens.append({"text": "\n", "start": start + len(speaker) + len(sentence)+1 , "end": start + len(speaker) + len(sentence)+1, "id": 5, "ws": False})

                    # speaker's span
                    spans.append({"start": start, "end": start + len(speaker), "token_start": 3, "token_end": 3, "label": "speaker",})
                    # start for the next sentence
                    start = start + len(speaker) + len(sentence) + 2
                    
                    # 3RD CONTEXT
                    sentence = s[2]["text"]
                    speaker = s[2]["meta"]["speaker"]
                    tokens.append({"text": speaker, "start": start, "end": start + len(speaker), "id": 6, "ws": True})
                    tokens.append({"text": sentence, "start": start + len(speaker)+1, "end": start + len(speaker) + len(sentence), "id": 7, "ws": True})
                    tokens.append({"text": "\n", "start": start + len(speaker) + len(sentence)+1 , "end": start + len(speaker) + len(sentence)+1, "id": 8, "ws": False})

                    # speaker's span
                    spans.append({"start": start, "end": start + len(speaker), "token_start": 6, "token_end": 6, "label": "speaker",})
                    start = start + len(speaker) + len(sentence) + 2
                    
                    # 4TH CONTEXT
                    sentence = s[3]["text"]
                    speaker = s[3]["meta"]["speaker"]
                    tokens.append({"text": speaker, "start": start, "end": start + len(speaker), "id": 9, "ws": True})
                    tokens.append({"text": sentence, "start": start + len(speaker)+1, "end": start + len(speaker) + len(sentence), "id": 10, "ws": True})
                    tokens.append({"text": "\n", "start": start + len(speaker) + len(sentence)+1 , "end": start + len(speaker) + len(sentence)+1, "id": 11, "ws": False})

                    # speaker's span
                    spans.append({"start": start, "end": start + len(speaker), "token_start": 9, "token_end": 9, "label": "speaker",})
                    start = start + len(speaker) + len(sentence) + 2
                    
                    # 5TH CONTEXT
                    sentence = s[4]["text"]
                    speaker = s[4]["meta"]["speaker"]
                    tokens.append({"text": speaker, "start": start, "end": start + len(speaker), "id": 12, "ws": True})
                    tokens.append({"text": sentence, "start": start + len(speaker)+1, "end": start + len(speaker) + len(sentence)+1, "id": 13, "ws": True})

                    # speaker's span
                    spans.append({"start": start, "end": start + len(speaker), "token_start": 12, "token_end": 12, "label": "speaker",})
                    
                    
                else:
                    print("len(s) < 5" , s)

                # find relations
                rel = relations([(el["meta"]["speaker"], el["text"]) for el in s])
                
                # pre-selected relations
                rel_list = []
                
                # create preselected relation displayed in Prodigy 
                # relation : {"child": 4, "head": 3, "label": "ADDRESSED_TO"}
                if rel:
                    for i in rel :
                        r = {}
                        id_char = []
                        for e in tokens:                           
                            # si l"addressee correspond à un des locuteurs   
                            if i[1][1] in e["text"]:
                                #print(i[1][1], e["text"], e["id"])
                                id_char.append(e["id"])
                                r["child"] = min(id_char)
                                #relations.append()
                            if i[1][0] == e["text"]:
                                #print(e["text"])
                                r["head"] = e["id"]
                                r["label"] = "ADDRESSED_TO"
                        rel_list.append(r)

                # start and end times
                if len(s) == 5 :
                    start_time = s[0]["meta"]["aligned"]._.start_time
                    end_time = s[4]["meta"]["aligned"]._.end_time + 0.5
                    #load mkv for corresponding video extract
                    video_excerpt = mkv_to_base64(mkv, start_time, end_time)
                
                else:
                    video_excerpt = mkv_to_base64(mkv, 1.0, 2.0)
                
                if len(s) == 5:
                    # append tokens to dictionary
                    to_return["video"] = video_excerpt
                    to_return["tokens"] = tokens 
                    to_return["spans"] = spans
                    to_return["relations"] = rel_list
                    to_return["meta"] = {'first':first, 'second': second , 'third': third, 'fourth': fourth, 'fifth':fifth}
                    to_return["episode"] = episode
                    
                    #to_return["relations_span_labels"] = episode_characters

                    yield to_return



@prodigy.recipe("addressee")
def addresse(dataset):

    blocks = [
        {"view_id": "audio"},
        {"view_id": "relations"},
    ]

    # call stream
    stream = speech_turns()    
    
    # create labels list
    episode = None    
    for i in stream:
        episode = i["episode"]
        break
    series = episode.split('.')[0]
    labels = load_credits(episode, series, PATH)
    labels = labels + ["multiple_persons"]
    
    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": stream,
        "before_db": remove_video_before_db,
        "config": {
            "relations_span_labels" : list(set(labels)),            
            "blocks": blocks,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
            "wrap_relations" : True, # apply line breaks
            "hide_newlines": True,
            "labels": ["ADDRESSED_TO",], # relations names
            # c0168 : video & annotation interface container / c0182 : space between play buttons & video / .c0188 : play & loop buttons space / c01110 : allowed space for spans selection (if too narrow, a scroll bar appears)/ c01117 : options space (relations selection or labels assignment) / .c01103 video & annotation boxes space 
            "global_css": ".c0168 {display:flex; flex-direction:row; width:auto; max-width:100%;} .c0182 {width:2%;} .c0188 {width:10%; padding:auto;} .c01110 {width:500px;} .c01117 {width:20%;} .c01103 {width:30%;}",
        },
    }

