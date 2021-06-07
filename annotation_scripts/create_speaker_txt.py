#!/usr/bin/env python
# coding: utf-8

### Create speakers.txt file for speaker.py recipe
### Output : list of speakers in a txt file
"""Usage:
process_alignment.py <id_series>
"""

import os
from docopt import docopt
from pathlib import Path


# path to plumcot-prodigy
PATH = Path(__file__).absolute().parent.parent

# path to shows directories
DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    id_series = args["<id_series>"]
    
    # file to write
    file = open(os.path.join(PATH, "speakers.txt"), 'w')
    
    # characters of the current show
    characters = open(f'{DATA_PLUMCOT}/{id_series}/characters.txt', 'r')

    # write file
    print(f"Write json file to {PATH}")
    for line in characters:
        loc = line.split(',')[0]
        file.write(loc +'\n')
        
    file.close()
    characters.close()


    print("DONE.")




