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
$ (plumcot-prodigy) pip install -r requirements.txt

# download spaCy english model
$ (plumcot-prodigy) python -m spacy download en_core_web_sm
```
Install libraries for speaker annotation :
- install [pytorch](https://pytorch.org/)
- install develop branch of [pyannote.audio](https://github.com/pyannote/pyannote-audio/tree/develop) :
```bash
pip install https://github.com/pyannote/pyannote-audio/archive/develop.zip
```
- install [faiss](https://github.com/facebookresearch/faiss) :
```bash
conda install -c pytorch faiss-cpu
```
```bash
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

1. Make sure that the show you want to annotate is in the right format : [adapt alignement file](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#before-annotation)
2. Check the alignment of the episodes : [check alignment](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#check-alignment)
3. Check didascalies in your transcipts : [check didascalies](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#check-didascalies)
4. (if needed) Annotate not_available characters : [not available speakers](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#not_available-characters)
5. Annotate addressees : [addressees](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#addressees)
6. Add entity linking (1st & 2nd persons) : [entity linking 1](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#entity-linking---1st-2nd-persons--names)
7. Annotate entity linking (3rd person & names): [entity linking 2](https://github.com/julietteBergoend/plumcot-prodigy/tree/main/plumcot_prodigy#entity-linking---3rd-person--names)

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
