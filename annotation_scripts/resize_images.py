#!/usr/bin/env python
# coding: utf-8

# ### Resize images for select_characters ans speaker recipes - Prodigy


"""Usage:
resize_images.py <episode_name> <path_to_corpora>
"""

import os
import json

from custom_loaders import *
from PIL import Image
from pathlib import Path
from docopt import docopt

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # path to Plumcot data
    DATA_PLUMCOT = args["<path_to_corpora>"]
    
    episode = args["<episode_name>"]

    episodes_list = [episode]

    for episode in episodes_list:
        print("\nCurrent episode", episode)
        
        series = episode.split('.')[0]
        
        path = DATA_PLUMCOT

        # path to credits
        with open(os.path.join(path, f"{series}/credits.txt")) as f_c:
            credits = f_c.read()

        # path to characters
        with open(os.path.join(path,f"{series}/characters.txt")) as f_ch:
            characters = f_ch.read()                  
        characters_list = [char.split(',')[0] for char in characters.split('\n') if char != '']
        print(episode)
        # credits per episodes
        credits_dict = {episode.split(',')[0] : episode.split(',')[1:] for episode in credits.split('\n')}
        final_dict = {}
        for ep, credit in credits_dict.items():
            final_dict[ep] = [ch for ch, cr in zip(characters_list, credit) if cr == "1"]   

        # credits for the current episode
        episode_characters = final_dict[episode]

        # open json file corresponding to the current show
        data = [json.loads(line) for line in open(os.path.join(path,f"{series}/images/images.json"), 'r')]

        # find centroid for each character in the current episode
        for character in episode_characters : 
            
            for picture in data:
                
                # add path to picture
                if character == picture[0]:
                    img = Image.open(os.path.join(path,f"{series}/images/{picture[1]}"))
                    img_resize = img.resize((43, 44))
                    img_resize.save(os.path.join(path,f"{series}/images/{picture[1]}"))
                                    
        print("DONE")







