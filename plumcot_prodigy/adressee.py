import prodigy
from prodigy.components.preprocess import add_tokens, split_sentences
from plumcot_prodigy.custom_loaders import *
import requests
from plumcot_prodigy.video import mkv_to_base64
from typing import Dict, List, Text

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
            
    return examples

def speakers(speech_turns):
    """
    List of speakers of the current episode to display in labels interface
    """
    liste = None
    for i in speech_turns:
        liste = list(i["episode_speakers"])
        break
    return liste

def relations(liste):
    """
    Create relations list to pre-select relations
    Output : [(locutor, (sentence with addressee, addressee), ...] 
    """
    locutors = [el[0] for el in liste]

    relations_list = []
    
    for idx, i in enumerate(liste):
        locutor = i[0]
        sentence = i[1]

        if liste:
            if idx == 0 :                
                if liste[idx+1][0] == liste[idx][0]:
                    if liste[idx+2][0] != liste[idx][0]:                        
                        #print("Addressed to :", liste[idx-1][0], "()", liste[idx-1][1:])
                        relations_list.append((locutor, (sentence, liste[idx+2][0])))
                    else:
                        continue
                if liste[idx+1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx+1][0])))
            
            if idx == 1:
                if liste[idx-1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx-1][0])))
                else:
                    relations_list.append((locutor, (sentence, liste[idx+1][0])))
            
            if idx == 2:
                if liste[idx-1][0] != liste[idx][0]:
                    relations_list.append((locutor, (sentence, liste[idx-1][0])))
                else:
                    relations_list.append((locutor, (sentence, liste[idx-2][0])))

    return relations_list

def speech_turns():
    
    # load episode
    episodes_list = ["TheBigBangTheory.Season01.Episode01"]
    
    # speakers labels when speaker is not in displayed sentences
    episode_speakers = []

    for episode in episodes_list:
        print("\nCurrent Episode :", episode)
        
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')
            
        mkv, aligned, sentences = load_files(series, episode, PATH)
        
        # ignore empty files
        if mkv == "" and aligned == "":
            continue
            
        else:
            speech_turns = list()

            # create speaker / sentence groups
            for idx, sentence in enumerate(sentences):
                
                # keep track of the sentence's id in alignment file
                speech_turns.append( ( (idx, sentence), (sentence._.speaker, str(sentence)) ) )
                episode_speakers.append(sentence._.speaker)   

            # process sentences 3 by 3
            for slices in range(0, len(speech_turns), 3):
                print("\n", speech_turns[slices:slices+3])
                
                # sentence & speaker container for relations
                s = []
                
                # append text and speaker data to s
                for idx_sent, speaker_sent in speech_turns[slices:slices+3]:

                    if len(speech_turns[slices:slices+3]) ==3:
                        
                        left = {"sentence": str(speech_turns[slices:slices+3][0][0][1]), "speaker": str(speech_turns[slices:slices+3][0][1][0]), "id": str(speech_turns[slices:slices+3][0][0][0])}
                        middle = {"sentence": str(speech_turns[slices:slices+3][1][0][1]), "speaker": str(speech_turns[slices:slices+3][1][1][0]), "id": str(speech_turns[slices:slices+3][1][0][0])}
                        right = {"sentence": str(speech_turns[slices:slices+3][2][0][1]), "speaker": str(speech_turns[slices:slices+3][2][1][0]), "id": str(speech_turns[slices:slices+3][2][0][0])}

                        s.append({"text": speaker_sent[1], "meta": {"speaker": speaker_sent[0], "aligned": idx_sent[1]} })
                    else:
                        print("!!! Not enough sentences!!!", speech_turns[slices:slices+3])
                
                print("\n",s)
                print("\nLEFT", left)
                print("\nMID", middle)
                print("\nRIGHT", right)
                
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
                if len(s) == 3:
                    
                    # LEFT CONTEXT
                    sentence = s[0]["text"]
                    speaker = s[0]["meta"]["speaker"]
                    tokens.append({"text": speaker, "start": 0, "end": len(speaker), "id": 0, "ws": True})
                    tokens.append({"text": sentence, "start": len(speaker) +1 , "end": len(speaker) + len(sentence), "id": 1, "ws": True})
                    tokens.append({"text": "\n", "start": len(speaker) + len(sentence)+1 , "end": len(speaker) + len(sentence)+1, "id": 2, "ws": False})                            

                    # speaker's span
                    spans.append({"start": 0, "end": len(speaker), "token_start": 0, "token_end": 0, "label": "speaker",})
                    # start for the next sentence
                    start = len(speaker) + len(sentence)+2
                    
                    # MIDDLE SENTENCE
                    sentence = s[1]["text"]
                    speaker = s[1]["meta"]["speaker"]                   
                    tokens.append({"text": speaker, "start": start, "end": start + len(speaker), "id": 3, "ws": True})
                    tokens.append({"text": sentence, "start": start + len(speaker)+1 , "end": start + len(speaker) + len(sentence), "id": 4, "ws": True, "style" : {"background": "#ff6666"}})
                    tokens.append({"text": "\n", "start": start + len(speaker) + len(sentence)+1 , "end": start + len(speaker) + len(sentence)+1, "id": 5, "ws": False})

                    # speaker's span
                    spans.append({"start": start, "end": start + len(speaker), "token_start": 3, "token_end": 3, "label": "speaker",})
                    # start for the next sentence
                    start = start + len(speaker) + len(sentence) + 2
                    
                    # RIGHT CONTEXT
                    sentence = s[2]["text"]
                    speaker = s[2]["meta"]["speaker"]
                    tokens.append({"text": speaker, "start": start, "end": start + len(speaker), "id": 6, "ws": True})
                    tokens.append({"text": sentence, "start": start + len(speaker)+1, "end": start + len(speaker) + len(sentence)+1, "id": 7, "ws": True})

                    # speaker's span
                    spans.append({"start": start, "end": start + len(speaker), "token_start": 6, "token_end": 6, "label": "speaker",})

                else:
                    print("len(s) < 3" , s)
                
                print('\nTOKENS', tokens )
                print("\n TEXT TO RETURN",to_return["text"])
                
                # find relations
                rel = relations([(el["meta"]["speaker"], el["text"]) for el in s])
                
                # pre-selected relations
                rel_list = []
                
                print("\nRELATIONS", rel)
                # create preselected relation displayed in Prodigy 
                # relation : {"child": 4, "head": 3, "label": "ADDRESSED_TO"}
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
                print("PRESELECT RELATIONS", rel_list)
                
                # start and end times
                if len(s) == 3 :
                    start_time = s[0]["meta"]["aligned"]._.start_time
                    end_time = s[2]["meta"]["aligned"]._.end_time
                    print("\nTIMES",start_time, end_time)
                    #load mkv for corresponding video extract
                    video_excerpt = mkv_to_base64(mkv, start_time, end_time)
                
                else:
                    video_excerpt = mkv_to_base64(mkv, 1.0, 2.0)
                    
                # append tokens to dictionary
                to_return["video"] = video_excerpt
                to_return["tokens"] = tokens 
                to_return["spans"] = spans
                to_return["relations"] = rel_list
                to_return["meta"] = {'left':left, 'middle': middle , 'right': right}
                to_return["episode"] = episode
                to_return["episode_speakers"] = set(episode_speakers)
                
                yield to_return

def debug_stream():

    while True:

        yield {
            'text': "sheldon_cooper So if a photon is directed through a plane with two slits in it and either slit is observed it will not go through both slits. If it's unobserved it will, however, if it's observed after it's left the plane but before it hits its target, it will not have gone through both slits.\nleonard_hofstadter Agreed, what's your point?\nsheldon_cooper There's no point, I just think it's a good idea for a tee-shirt.\n",
            "tokens": [
                {'text': 'sheldon_cooper', 'start': 0, 'end': 14, 'id': 0, 'ws': True},
                {'text': "So if a photon is directed through a plane with two slits in it and either slit is observed it will not go through both slits. If it's unobserved it will, however, if it's observed after it's left the plane but before it hits its target, it will not have gone through both slits.", 'start': 15, 'end': 293, 'id': 1, 'ws': True},
                {'text': '\n', 'start': 294, 'end': 294, 'id': 2, 'ws': False},
                {'text': 'leonard_hofstadter', 'start': 295, 'end': 313, 'id': 3, 'ws': True},
                {'text': "Agreed, what's your point?", 'start': 314, 'end': 339, 'id': 4, 'ws': True},

            ],
            
            # spans for speakers
            "spans": [
                {
                    "start": 0,
                    "end": 7,
                    "token_start": 0,
                    "token_end": 0,
                    "label": "speaker",
                },
                {
                    "start": 21,
                    "end": 28,
                    "token_start": 2,
                    "token_end": 2,
                    "label": "speaker",
                },
                {
                    "start": 42,
                    "end": 49,
                    "token_start": 4,
                    "token_end": 4,
                    "label": "speaker",
                },
            ],
            
            "relations":[
                {"child": 4, "head": 3, "label": "ADDRESSED_TO"},
                {"child": 2, "head": 5, "label": "ADDRESSED_TO"},
            ],
            
            "html": "<iframe width='400' height='225' src='https://www.youtube.com/embed/vKmrxnbjlfY'></iframe>",
        }


@prodigy.recipe("addressee")
def addresse(dataset):

    blocks = [
        {"view_id": "audio"},
        {"view_id": "relations"},
    ]

    stream = speech_turns()
    
    speakers_labels = speakers(stream)
    print("SPEAKERS", speakers_labels)
    
    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": stream,
        "before_db": remove_video_before_db,
        "config": {
            "relations_span_labels" : speakers_labels,            
            "blocks": blocks,
            "audio_autoplay": True,
            "show_audio_minimap": False,
            "show_audio_timeline": False,
            "show_audio_cursor": False,
            "wrap_relations" : True,
            "hide_newlines": True,
            "labels": ["ADDRESSED_TO",],
            # # c0168 : video & annotation interface container / c0182 : space between play buttons & video / .c0188 : play & loop buttons space / c01110 : allowed space for spans selection (if too narrow, a scroll bar appears)/ c01117 : options space (relations selection or labels assignment) / .c01103 video & annotation boxes space 
            "global_css": ".c0168 {display:flex; flex-direction:row; width:auto; max-width:100%;} .c0182 {width:2%;} .c0188 {width:10%; padding:auto;} .c01110 {width:500px;} .c01117 {width:20%;} .c01103 {width:30%;}",
        },
    }

