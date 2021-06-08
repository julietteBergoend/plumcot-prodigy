# plumcot-prodigy

Prodigy recipes for PLUMCOT dataset

## Installation


```bash
# clone this repository
$ git clone https://github.com/hbredin/plumcot-prodigy.git
$ cd plumcot-prodigy

# create and activate conda environment
$ conda env create -f environment.yml
$ conda activate plumcot-prodigy

# install prodigy 
$ (plumcot-prodigy) pip install prodigy.*.whl

# download spaCy english model
$ (plumcot-prodigy) python -m spacy download en_core_web_sm

# launch prodigy annotation server
$ (plumcot-prodigy) prodigy check_forced_alignment my_dataset -F plumcot_prodigy/recipes.py

Added dataset my_dataset to database SQLite.

✨  Starting the web server at http://localhost:8080 ...
Open the app in your browser and start annotating!

```

![check_forced_alignment recipe](screenshots/check_forced_alignment.jpg)


To access the server from anywhere, one can use [`ngrok`](https://ngrok.com/).
Once `ngrok` is copied and [running](https://dashboard.ngrok.com/get-started/setup) with `./ngrok http 8080`, you can access the web interface in your browser using the printed `http://xxxxx.ngrok.io` URL.

## Starting new annotations for [Plumcot](https://github.com/julietteBergoend/pyannote-db-plumcot) dataset

When starting new annotations, you need to follow this process : 

1. Make sure that the show you want to annotate is in the right format :
2. Check the alignment of the episodes : lien check alignment
3. Check didascalies in your transcipts :
4. (if needed) Annotate not_available characters :
5. Annotate addressees :
6. Add entity linking (1st & 2nd persons) :
7. Annotate entity linking (3rd person & names): 

## Notes

Annotation scripts
```bash
(plumcot-prodigy) cd plumcot-prodigy
```

Pre-process and post-process annotation scripts
```bash
(plumcot-prodigy) cd plumcot-prodigy/annotation_scripts
```

Place to save your annotations
```bash
(plumcot-prodigy) cd plumcot-prodigy/prodigy_databases
```
