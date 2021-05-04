import prodigy
from prodigy.components.preprocess import add_tokens, split_sentences
import requests
import spacy

def debug_stream():

    while True:

        yield {
            "text": "sheldon Hello there. sheldon How are you? leonard Fine, thank you.",
            "tokens": [
                {"text": "sheldon", "start": 0, "end": 7, "id": 0, "ws": True},
                {"text": "Hello there.\n", "start": 8, "end": 20, "id": 1, "ws": True},
                {"text": "sheldon", "start": 21, "end": 28, "id": 2, "ws": True},
                {"text": "How are you?", "start": 29, "end": 41, "id": 3, "ws": True},
                {"text": "leonard", "start": 42, "end": 49, "id": 4, "ws": True},
                {
                    "text": "Fine, thank you.",
                    "start": 50,
                    "end": 66,
                    "id": 5,
                    "ws": True,
                },
            ],
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
                }], 
                
             "relations": [            
                 {
                     'head': 1, 
                     'label': 'ADDRESSED_TO', 
                     'child': 4
                 },
                {
                     'head': 3, 
                     'label': 'ADDRESSED_TO', 
                     'child': 4
                 },
               {
                     'head': 5, 
                     'label': 'ADDRESSED_TO', 
                     'child': 0
                 }
                 
            ],
            "html": "<iframe width='400' height='225' src='https://www.youtube.com/embed/vKmrxnbjlfY'></iframe>",
                }


@prodigy.recipe("simple_addressee")
def addresse(dataset):

    blocks = [
        {"view_id": "html"},
        {"view_id": "relations"},
    ]

    stream = debug_stream()

    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": stream,
        "config": {
            "blocks": blocks,
            "hide_newlines": True,
            "labels": ["ADDRESSED_TO",],
            # "relations_span_labels": ["sheldon", "leonard"],
        },
    }
