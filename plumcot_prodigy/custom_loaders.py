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
            
    
def load_episodes(path):
    """Load shows' episodes,
       Return episode list
    """

    # gather all episodes of all shows together
    all_episodes_series = ""
   
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
    
    return episodes_list
    
def load_photo(characters, serie_uri, path):  
    """Load photos for the show's characters
    """
    directory = "/vol/work1/bergoend/pyannote-db-plumcot"
    
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
                    char_pictures[name] = os.path.join(directory, val['paths'][0])
                    
            # characters without photo
            elif character == name and val['count'] == 0:
                char_pictures[name] = name
    return char_pictures 