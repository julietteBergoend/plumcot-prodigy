#!/usr/bin/env python
# coding: utf-8

# ### Resize images for select_characters ans speaker recipes - Prodigy

# warning : for the moment all images are available in /vol/work1/bergoend/pyannote-db...

"""Usage:
process_alignment.py <episode_name>
"""

import os
import json

from custom_loaders import *
from PIL import Image


# path to Plumcot data
DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    episode = args["<episode_name>"]

    episodes_list = [episode]

    for episode in episodes_list:
        print("\nCurrent episode", episode)
        
        series = episode.split('.')[0]
        
        path = DATA_PLUMCOT
        
        # load aligned sentence
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
            print(episode)
            # credits per episodes
            credits_dict = {episode.split(',')[0] : episode.split(',')[1:] for episode in credits.split('\n')}
            final_dict = {}
            for ep, credit in credits_dict.items():
                final_dict[ep] = [ch for ch, cr in zip(characters_list, credit) if cr == "1"]   

            # credits for the current episode
            episode_characters = final_dict[episode]

            # open json file corresponding to the current show
            with open(os.path.join(path, f"{series}/images/images.json")) as f:
                data = json.load(f)

            # dictionary character : url to the character's picture
            char_pictures = {}
            # dictionaries for characters
            characters_dic = data['characters']

                    # open json file corresponding to the current show
            with open(os.path.join(path, f"{series}/images/images.json")) as f:
                data = json.load(f)

            # dictionary character : url to the character's picture
            char_pictures = {}
            # dictionaries for characters
            characters_dic = data['characters']
            i=0
            # find centroid for each character in the current episode
            for character in episode_characters : 
                #print(character)
                for name, val in characters_dic.items():

                    # characters with a centroid
                    if character == name and val['count'] != 0:
                        try:
                            if val['centroid'] :
                                i+=1
                                char_pictures[name] = val['centroid']
                                print('centroid ',character)
                                print(val['centroid'])
                                img = Image.open(val['centroid'])
                                img_resize = img.resize((43, 44))
                                img_resize.save(val['centroid'])

                        # characters without centroid
                        except KeyError:
                            i+=1
                            char_pictures[name] = os.path.join(directory, val['paths'][0])
                            print('photo ',character)
                            print(os.path.join(directory, val['paths'][0]))
                            img = Image.open(os.path.join(directory, val['paths'][0]))
                            img_resize = img.resize((43, 44))
                            img_resize.save(os.path.join(directory, val['paths'][0]))
                    # characters without photo
                    elif character == name and val['count'] == 0:
                        char_pictures[name] = name
                        print('Character without photo :',character)
            print("DONE.")







