# Annotation guide

## Process

### Before annotation

Make sure that all your alignment files contain lines of length 8, as follow
```bash
<episode_name_field> <speaker_field> <start_time_field> <end_time_field> <word_field> <confidence_field> <entity_linking_field> <addressee_field>

e.g : TheWalkingDead.Season01.Episode02 carl_grimes 8.70 9.06 Mom 0.10 _ _
```
Each line must contain : the episode reference, speaker name, start time of the word, end time of the word, one word, confidence score, entity linking (EL) (represented by “_”, “?”, or “character_name”), addressee (represented by “_”*, “?”*, or “character_name”).

Corresponding script : [adapt_aligned_file.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/annotation_scripts/adapt_aligned_file.py)
Usage : PATH TO GUIDE

The script will create a temp file with a copy of the previous transcript, and a new aligned file with one or two “?” sign(s) at the end of each line (depending on the length of the lines). 

* _ : this sign means that the episode was already annotated in EL or Addressee, and that no annotation was done on the current word (because not necessary for example).

* ? : this sign means that the episode was never annotated in EL or Addressees

### Check alignment

![check_forced_alignment recipe](screenshots/alignment.jpg)

Corresponding script : [check_alignment.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/check_alignment.py)

This part allows you to check double episodes in a show. 
The recipe displays the first and the last sentences of each episode in the season you want to annotate. 
If the text corresponds to audio in both examples, the episode is good. If not, it can be because of a double episode. In the last case, you need to check the transcript of the episode.

#### Usage
1. Make sure that you have created a DB before lauching annotation
Recommended name for your database : data_alignment
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy db-in data_alignment
```
2. Lauch recipe
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy check_forced_alignment <dataset_name> <show_name> <season> -F plumcot_prodigy/check_alignment.py

e.g : prodigy check_forced_alignment data_alignment Lost Season01 -F plumcot_prodigy/check_alignment.py
```
3. Save you annotations
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy db-out data_alignment > <path/to/prodigy_databases/data_base_name.jsonl>
```
4. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./process_alignment.py <id_series> <data_base_name>

e.g : ./process_alignment.py Lost alignment_data.jsonl
```
### Check didascalies

### Not_available characters

#### Before annotation

#### Select_character

#### Speakers

### Addressees

### Entity linking

#### Entity linking - 1st, 2nd persons & names

#### Entity linking - 3rd person & names

## Notes

### video.py

### custom_loaders.py

### forced_alignment.py
