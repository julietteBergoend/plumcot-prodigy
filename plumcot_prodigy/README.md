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

Usage :
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./adapt_aligned_file.py <episode_name>

e.g : ./adapt_aligned_file.py 24.Season01.Episode01
```

The script will create a temp file with a copy of the previous transcript, and a new aligned file with one or two “?” sign(s) at the end of each line (depending on the length of the lines). 

* _ : this sign means that the episode was already annotated in EL or Addressee, and that no annotation was done on the current word (because not necessary for example).

* ? : this sign means that the episode was never annotated in EL or Addressees

### Check alignment

![check_forced_alignment recipe](../screenshots/alignment.png)

Corresponding script : [check_alignment.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/check_alignment.py)

This part allows you to check double episodes in a show. 
The recipe displays the first and the last sentences of each episode in the season you want to annotate. 
If the text corresponds to audio in both examples, the episode is good. If not, it can be because of a double episode. In the last case, you need to check the transcript of the episode.

#### Usage
1. Make sure that you have created a database before lauching annotation.
Create a data base before first usage only.
Recommended name for your database : data_alignment
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy db-in data_alignment
```
2. Lauch recipe
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy check_forced_alignment <dataset_name> <show_name> <season> -F plumcot_prodigy/check_alignment.py

e.g : prodigy check_forced_alignment data_alignment Lost Season01 -F plumcot_prodigy/check_alignment.py
```
<path_to_corpora> : corpora containing wav, mkv and txt files

Press _a_ (for _accept_) when the audio corresponds to the text.
Press _x_ (for _reject_) if not.

3. Save your annotations
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy db-out data_alignment > <path/to/prodigy_databases/data_base_name.jsonl>
```
4. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./process_alignment.py <id_series> <data_base_name>

e.g : ./process_alignment.py Lost alignment_data.jsonl
```
The script displays the result of your annotations. Based on it, you may need to check some audio and transcript files.
### Check didascalies
![check_didascalies](../screenshots/didascalies.png)

Corresponding script : [check_didascalies.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/check_didascalies.py)

This recipe allows to delete didascalies in transcription files. 
Prodigy displays all the sentences in the current episode with confidence index under _x_, and allows to select parts of the sentence to delete (if so). Left and right contexts are displayed but with forbidden selection.

#### Usage
1. Create a new database.
Recommended name for your database : data_didascalies
2. Lauch the recipe :
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy check_didascalies.py data_didascalies <episode> <confidence_index> <path_to_corpora> -F plumcot_prodigy/check_didascalies.py

e.g : prodigy check_didascalies data_didascalies TheWalkingDead.Season01.Episode01 0.3 /home/toto/corpora/ -F plumcot_prodigy/check_didascalies.py
```
When selection is finished, press _x_ (or _reject_).
If no selection is necessary, press _a_ (or _accept_) or _space_ (or _ignore_).

The top example will display sentences with a confidence index bellow 0.3. 

3. Save your annotations
```bash
e.g : prodigy db-out data_didascalies > seasons1_didascalies.jsonl
```
4. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./process_didascalies.py <episode> <data_base_name>

e.g : ./process_didascalies.py TheWalkingDead.Season01.Episode01 seasons1_didascalies.jsonl
```
Didascalies deletion is applied to trancript files (Plumcot/data/{serie_uri}/transcripts/*.txt), not to aligned files.
Once the new trancript file is created, you must lauch [Forced Alignment](https://github.com/PaulLerner/Forced-Alignment) to create a new aligned file. 

### Not_available characters
This part concerns all shows without available characters.
```bash
(aligned file)
ER.Season01.Episode01 not_available 6.2 6.5600000000000005 Dr 0.1 ? ?
ER.Season01.Episode01 not_available 6.56 6.56 . 0.95 ? ?
ER.Season01.Episode01 not_available 12.76 13.12 Greene 0.1 ? ?
ER.Season01.Episode01 not_available 13.12 13.12 ? 0.95 ? ?
```
Prodigy displays all the sentences in the current episode with not available speaker, and images corresponding to all the characters of the current episodes.

Two scripts are available for this task, including one recipe with active annotation using speaker diarization model.
#### Before annotation
The two recipes are using image selection. Images have to be size 40x40 to allow correct display.

Corresponding script : [resize_images](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/annotation_scripts/resize_images.py)

Usage:
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./resize_images <episode_name>

e.g : ./resize_images 24.Season01.Episode01
```
#### Select_character
![select_characters](../screenshots/select_chars.png)

Corresponding script : [select_characters.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/select_characters.py)

This recipe is a version without speaker diarization.

1. Process images
2. Enter a new database
3. Lauch recipe
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy select_char select_characters <episode_name> -F plumcot_prodigy/select_characters.py

e.g : prodigy select_char select_characters 24.Season01.Episode01 -F plumcot_prodigy/select_characters.py
```
When selection is finished, press _a_ (for _accept_) .
If no selection is done, press _space_ (for _ignore_) or _x_.
You can select multiple images when multiple characters are uttering the same sentence at the same time.

4. Save your annotations
5. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./replace_non_available_chars.py <episode> <data_base_name>

e.g : ./replace_non_available_chars.py 24.Season01.Episode01 characters.jsonl
```
Speaker annotations are applied directly to the alignment file.
A temporary file is created with previous alignment.

#### Speakers
![speakers](../screenshots/speakers.png)

Corresponding script : [speaker.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/speaker.py)

Active learning annotation with speaker recognition model.

1. Before annotation : format the data to annotate
  - create speech turn file :	this file gathers all speech turns without speaker in the alignment file.
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./create_speech_turns.py <episode_name>
```
  - create speakers file : this file is a list of all the speakers of the current show.
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./create_speakers_txt.py <id_series>
```
2. Create a new database
3. Lauch recipe
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy pyannote.speaker <path/to/speechturns.jsonl> 
-speakers=<path/to/speakers.txt> -allow-new-speaker -F plumcot_prodigy/speaker.py

e.g : prodigy pyannote.speaker speakers_data speech_turns.jsonl -speakers=speakers.txt -allow-new-speaker -F plumcot_prodigy/speaker.py
```
The recipe uses the same principle as select_characters : select corresponding locutor thanks to images.
Multiple selections are _not allowed_.

This recipe stores annotations to make predictions on the current speaker.
Predictions start after about 20 annotations. 

4. Save your annotations
5. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./replace_non_available_chars.py <episode> <data_base_name>

e.g : ./replace_non_available_chars.py 24.Season01.Episode01 speakers_data.jsonl
```
Speaker annotations are applied directly to the alignment file.
A temporary file is created with previous alignment.

### Addressees
![addressee](../screenshots/addressee_1.png)

Selecting relations (above)

![addressee](../screenshots/addressee_2.png)

Labelling relations (above)

Corresponding script : [addressees.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/adressee.py)

This recipe allows you to annotate addressees for 5 speech turns per example.
Addressee annotation consists in making relations between sentences and speakers. 

#### Usage
1. Create a database
2. Lauch recipe
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy addressee addressee_data <episode_name> -F plumcot_prodigy/adressee.py
```
The head of the relation is always a speaker whereas the child of the relation is always a sentence (see first illustration).
Relations are pre-selected but you may need to correct it manually.

Sometimes relations are not pre-selected because one speaker is talking during 5 speech turns. In this case, a labelling interface is available to label the sentence with its addressee (see second illustration).
Labelling can also be used when the addressee is addressed to multiple speakers which are not in the 5 speech turns.
Combination of labelling and selection is allowed.

Press _a_ when addressee annotation is done for the current example.
Press _space_ when no annotations are done/needed.

3. Save your annotations
4. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./process_addressee.py <episode> <data_base_name>
```
```bash
(aligned file)
TheWalkingDead.Season01.Episode02 carl_grimes 8.70 9.06 Mom 0.10 ? lori_grimes
TheWalkingDead.Season01.Episode02 carl_grimes 9.06 9.06 ! 0.95 ? lori_grimes
TheWalkingDead.Season01.Episode02 lori_grimes 19.19 19.55 Yes 0.99 ? carl_grimes
TheWalkingDead.Season01.Episode02 lori_grimes 19.60 20.00 Honey 0.99 ? carl_grimes
TheWalkingDead.Season01.Episode02 lori_grimes 21.00 22.00 ? 0.99 ? carl_grimes
```

### Entity linking

This task assigns entity labels to words such as pronouns : me, you, he, mine, her, we... 
Excluded pronouns : they, them.
It also attributes entity labels to names and nicknames :
```bash
(aligned file)
GameOfThrones.Season01.Episode05 renly_baratheon 477.69 478.07 Such 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 478.07 478.16 a 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 478.16 478.51 shame 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 478.51 478.51 , 0.10 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 478.62 479.24 Littlefinger 0.99 petyr_baelish petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 479.24 479.24 . 0.95 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 479.50 479.76 It 0.10 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 479.76 480.02 would 0.10 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.02 480.07 have 0.40 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.08 480.19 been 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.22 480.43 so 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.48 480.67 nice 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.69 480.76 for 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.77 480.82 you 0.99 petyr_baelish petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.84 480.92 to 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 480.94 481.02 have 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 481.02 481.09 a 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 481.09 481.36 friend 0.99 _ petyr_baelish
GameOfThrones.Season01.Episode05 renly_baratheon 481.36 481.36 . 0.95 _ petyr_baelish
```

#### Entity linking - 1st, 2nd persons & names

This first part of entity linking annotation uses addressees to assign EL to 2nd person pronouns, and current speaker for 1st person pronouns.

The [script](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/annotation_scripts/add_entity_linking.py) also uses knowledge given by the user to assign EL to names and nicknames:
```bash
knowledge = {

        # GOT
        "GameOfThrones" : {"ned" : "eddard_stark", "khaleesi" : "daenerys_targaryen", "dani" : "daenerys_targaryen", "littlefinger": "petyr_baelish", 
                          "sam" : "samwell_tarly", "tommen" : "tommen_baratheon", 'tywin': 'tywin_lannister', 'petyr': 'petyr_baelish', 
                          'cersei': 'cersei_lannister', 'jaime': 'jaime_lannister', 'theon': 'theon_greyjoy', 'barristan': 'barristan_selmy',
                          'jorah': 'jorah_mormont', 'joffrey': 'joffrey_baratheon', 'jeor': 'jeor_mormont', 'varly': 'varly', 'janos': 'janos_slynt',
                          'renly': 'renly_baratheon', 'robert': 'robert_baratheon', 'eddard': 'eddard_stark', 'waymar': 'waymar_royce', 'gared': 'gared', 
                          'jon': 'jon_snow', 'sansa': 'sansa_stark', 'sandor': 'sandor_clegane','arya': 'arya_stark', 'tyrion': 'tyrion_lannister', 
                          'catelyn': 'catelyn_stark', 'robin': 'robin_arryn', 'rodrik': 'rodrik_cassel', 'bronn': 'bronn', 'lancel': 'lancel_lannister',
                          'lysa': 'lysa_arryn', 'robb': 'robb_stark', 'irri': 'irri','vardis': 'vardis_egen', 'kevan': 'kevan_lannister',                                                     'rickon': 'rickon_stark'},
...
```
Usage:
1. Make sure that addressee annotation is done
2. Add names to the knowledge dictionary in the script. Add a new show dictionary if you work on a new show. 

Warning : each key in a dictionary corresponds to a firstname/name/nickame, and each value to a character id under the format firstname_name. Those ids must be present in _characters.txt_ file of the show you are annotating (Plumcot/data/{serie_uri}/characters.txt).
4. Lauch script
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$ ./add_entity_linking.py <episode_name>

e.g ./add_entity_linking.py TheWalkingDead.Season01.Episode02
```
The script will add EL to your alignment file.

#### Entity linking - 3rd person & names

![entity_linking](../screenshots/entity_linking.png)

Corresponding script : [entity.py](https://github.com/julietteBergoend/plumcot-prodigy/blob/main/plumcot_prodigy/entity.py)

This second step allows to assign EL to the rest of the nouns and pronouns in the aligned file.

Usage:
1. Create a new database
2. Lauch recipe
```bash
(plumcot-prodigy) plumcot-prodigy$ prodigy entity_linking entity_data <episode_name> -F plumcot_prodigy/entity.py
```
The recipe displays sentences one by one, and pre-selects nouns and pronouns.
If preselections are not nouns or pronouns, skip the example (_space_).
If preselections are nouns or pronouns, corresponding to one character, enter his name in the first input. The input will propose characters based on what you are writing. Select the right character and Press _a_.
If preselections are nouns or pronouns, corresponding to multiple characters, enter their names in separate inputs, and use the labelling tool to assign right labels to right nouns/pronouns (see the illustration). Press _a_.

3. Save your annotations
4. Process your annotations
```bash
(plumcot-prodigy) plumcot-prodigy/annotation_scripts$./process_entities.py <episode_name> <database_name>

e.g : ./process_entities.py TheWalkingDead.Season01.Episode02 test.jsonl
```
```bash
(aligned file)
TheWalkingDead.Season01.Episode02 carl_grimes 8.70 9.06 Mom 0.10 lori_grimes lori_grimes
TheWalkingDead.Season01.Episode02 carl_grimes 9.06 9.06 ! 0.95 _ lori_grimes
TheWalkingDead.Season01.Episode02 lori_grimes 19.19 19.55 Yes 0.99 _ carl_grimes
TheWalkingDead.Season01.Episode02 lori_grimes 19.60 20.00 Honey 0.99 _ carl_grimes
TheWalkingDead.Season01.Episode02 lori_grimes 21.00 22.00 ? 0.99 _ carl_grimes
```
