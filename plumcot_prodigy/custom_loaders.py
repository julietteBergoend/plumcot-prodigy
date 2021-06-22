from plumcot_prodigy.forced_alignment import ForcedAlignment
import os
import json

def load_files(series, episode, path):
    """Load mkv and aligned files of the current episode,
       Return mkv path, aligned path and sentences of the current episode
    """
    forced_alignment = ForcedAlignment()

    # path to mkv
    if os.path.isfile(f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv") : 
        mkv = f"/vol/work3/lefevre/dvd_extracted/{series}/{episode}.mkv"
    elif os.path.isfile(f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv") :
        mkv = f"/vol/work1/maurice/dvd_extracted/{series}/{episode}.mkv"
    else:
        print("No mkv file for", episode)
        mkv = ""

    # path to forced alignment
    if os.path.isfile(os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")):
        aligned = os.path.join(path,f"{series}/forced-alignment/{episode}.aligned")
    else:
        print("No aligned file for", episode)
        aligned = ""

    # load forced alignment        
    transcript = forced_alignment(aligned)      
    sentences = list(transcript.sents)

    return mkv, aligned, sentences
    
def load_episodes(path, episode): 
    """Load shows' episodes
    
       Arguments : path : path to Plumcot/data, 
                   show : show name (e.g Lost), 
                   season : season to annotate (e.g Season01), 
                   ep : episode to annotate (e.g Episode01)
       
       Return episode list to annotate
    """
    # if episode name is known, return it in a list
    if episode is not None :
        
        episodes_list = [episode]
        print("Number of episodes to annotate :", len(episodes_list))
        
        return episodes_list
    
    # else, find all the episodes of the current season  
    else :
       
        # process serie or film
        if len(episode.split('.')) == 3:
            series, _, _ = episode.split('.')
        elif len(episode.split('.')) == 2:
            series, _ = episode.split('.')

        series = [series]
        print("\nCurrent show :", series)

        # stack all episodes of the show
        all_episodes_series = ""

        # path to the show
        series_paths = [os.path.join(path, name) for name in series]

        # read episode.txt of each show
        for serie_name in series_paths:
            with open(os.path.join(serie_name,"episodes.txt")) as file:  
                episodes_file = file.read() 
                all_episodes_series += episodes_file

        # final list of all episodes (season x)
        episodes_list = [episode.split(',')[0] for episode in all_episodes_series.split('\n') if season in episode]

        print("Number of episodes to annotate :", len(episodes_list))
        return episodes_list

def load_credits(episode, series, path):
    
    with open(f"{path}/{series}/credits.txt") as f_c:
        credits = f_c.read()

    # path to characters
    with open(f"{path}/{series}/characters.txt") as f_ch:
          characters = f_ch.read()                  
    characters_list = [char.split(',')[0] for char in characters.split('\n') if char != '']

    # credits per episodes
    credits_dict = {ep.split(',')[0] : ep.split(',')[1:] for ep in credits.split('\n')}
    final_dict = {}
    for ep, credit in credits_dict.items():
        final_dict[ep] = [ch for ch, cr in zip(characters_list, credit) if cr == "1"]   

    # credits for the current episode
    episode_characters = final_dict[episode]
    
    return episode_characters
    
def load_photo(characters, serie_uri, path):  
    """Load photos for the show's characters
    """
    # open json file corresponding to the current show
    with open(os.path.join(path, f"{serie_uri}/images/images.json")) as f:
        data = json.load(f)

    # dictionary character : url to the character's picture
    char_pictures = {}
    # dictionaries for characters
    characters_dic = data['characters']

    # find centroid for each character in the current episode
    for character in characters : 
        for name, val in characters_dic.items():

            # characters with a centroid
            if character == name and val['count'] != 0:
                try:
                    if val['centroid'] :
                        char_pictures[name] = val['centroid'] 

                # characters without centroid
                except KeyError:
                    char_pictures[name] = name

            # characters without photo
            elif character == name and val['count'] == 0:
                char_pictures[name] = name
    return char_pictures 
