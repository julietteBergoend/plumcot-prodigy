#!/usr/bin/env python
# coding: utf-8

"""Usage:
add_entity_linking.py <episode>
"""

### Adding Entity Linking annotations after addressee annotations (1st & 2nd persons & names)

    # Use addresses annotations to add entity linking for 2nd pronouns : you, your, yours, yourself...
    # Use speaker of the current sentence to annotate 1st pronouns : my, me myself, mine, I...
    # Use knowledge to annotate names

from forced_alignment import ForcedAlignment
from docopt import docopt
from pathlib import Path

# path to Plumcot data
DATA_PLUMCOT = Path(__file__).absolute().parent.parent.parent / "pyannote-db-plumcot/Plumcot/data/"

if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    # episode name & json file
    episode = args["<episode>"]

    serie = episode.split('.')[0]
   
    # load forced alignment
    episode_path = f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.aligned'
    forced_alignment = ForcedAlignment()
    episode_sentences = forced_alignment(episode_path)
    sentences = list(episode_sentences.sents)


    # #### pronouns to annotate
    firt_prn = ["my", "me", "myself", "mine", "i"]
    second_prn = ["you", "your", "yours", "yourself"]

    # add knowledge based on characters 1st name (manually using print + copy + past in knowledge dictionary)
    supp = {sentence._.speaker.split("_")[0] : sentence._.speaker for sentence in sentences if sentence._.speaker.split("_")[0].lower() != "lord" and sentence._.speaker.split("_")[0].lower() != "the" }
    #print(supp)

    k= {}
    with open(f"{DATA_PLUMCOT}/{serie}/characters.txt", "r") as f:

        for i in f:
            char = i.split(',')[0]
            k[char.split('_')[0]] = char

    #print("\n",k)

    knowledge = {

        # GOT
        "GameOfThrones" : {"ned" : "eddard_stark", "khaleesi" : "daenerys_targaryen", "dani" : "daenerys_targaryen",
                          "littlefinger": "petyr_baelish", "sam" : "samwell_tarly", "tommen" : "tommen_baratheon",
                          'tywin': 'tywin_lannister', 'petyr': 'petyr_baelish', 'cersei': 'cersei_lannister',
                          'jaime': 'jaime_lannister', 'theon': 'theon_greyjoy', 'barristan': 'barristan_selmy',
                          'jorah': 'jorah_mormont', 'joffrey': 'joffrey_baratheon', 'jeor': 'jeor_mormont', 'varly': 'varly', 'janos': 'janos_slynt',
                          'renly': 'renly_baratheon', 'robert': 'robert_baratheon', 'eddard': 'eddard_stark',
                          'waymar': 'waymar_royce', 'gared': 'gared', 'jon': 'jon_snow', 'sansa': 'sansa_stark',
                          'sandor': 'sandor_clegane','arya': 'arya_stark', 'tyrion': 'tyrion_lannister', 'catelyn': 'catelyn_stark',
                          'robin': 'robin_arryn', 'rodrik': 'rodrik_cassel', 'bronn': 'bronn', 'lancel': 'lancel_lannister',
                          'lysa': 'lysa_arryn', 'robb': 'robb_stark', 'irri': 'irri','vardis': 'vardis_egen', 'kevan': 'kevan_lannister',
                          'rickon': 'rickon_stark'},

        # Lost
        "Lost" : { 'gina': 'gina', 'jeff': 'jeff', 'lily': 'lily',
            'arzt': 'dr_leslie_arzt', 'ana': 'ana_lucia_cortez','lucia': 'ana_lucia_cortez','cortez': 'ana_lucia_cortez',
            'sanjay': 'sanjay','diane': 'diane_janssen','steve': 'steve_jenkins','leslie': 'dr_leslie_arzt',
            'marc': 'marc_silverman','essam': 'essam_tasir', 'yusef': 'yusef', 'haddad': 'haddad',
            'frainey': 'frainey', 'eddie': 'eddie', 'anthony': 'anthony_cooper', 'cooper': 'anthony_cooper',
                  'emily': 'emily_locke','michael': 'michael_dawson', 'jack':'dr_jack_shephard', 'hurley': 'hugo_reyes',
                    'claire': 'claire_littleton', 'john': 'john_locke', 'gary': 'gary_troup', 
                     'hugo': 'hugo_reyes', 'boone': 'boone_carlyle', 'kate': 'kate_austen', 
                     'sayid': 'sayid_jarrah', 'charlie': 'charlie_pace', 'shannon': 'shannon_rutherford', 
                     'walt': 'walt_lloyd', 'cindy': 'cindy_chandler', 'rose': 'rose_nadler', 
                     'james': 'james_ford', 'sawyer': 'james_ford', 'seth': 'seth_norris', 'liam': 'liam_pace',
                  'ray': 'ray_mullen',  'warren': 'warren', 'randy': 'randy','helen': 'helen_norwood', 'margo': 'margo_shephard',
                  'sunhwa': 'sunhwa_kwon', 'kilo': 'kilo', 'nadia': 'noor_abed_jaseem', 'noor': 'noor_abed_jaseem',
                  'danielle': 'danielle_rousseau', 'omar': 'omar', 'sullivan': 'sullivan', 'ethan': 'dr_ethan_rom', 
                  'thomas': 'thomas','richard': 'richard_malkin', 'david': 'david', 'jessica':'jessica',
                  'locke': 'john_locke', 'rousseau': 'danielle_rousseau','vincent': 'vincent_the_dog',
                  'brian': 'brian_porter', 'tommy': 'tommy', 'lucy': 'lucy_heatherton', 'francis': 'francis_heatherton',
                  'laurence': 'laurence', 'diego': 'diego', 'tito': 'grandpa_tito', 'ken': 'ken_halperin',
                  'leonard': 'leonard', 'lenny': 'leonard','carmen': 'carmen_reyes',


                          },

         # TWD
        "TheWalkingDead" : { 'rick': 'rick_grimes', 'shane': 'shane_walsh', 'leon': 'leon_basset', 'duane': 'duane', 
                            'morgan': 'morgan_jones', 'amy': 'amy_harrison', 'dale': 'dale_horvath', 'lori': 'lori_grimes',
                            'carl': 'carl_grimes', 'glenn': 'glenn_rhee','daryl': 'daryl_dixon', 'carol': 'carol_peletier', 
                            'michonne': 'michonne', 'maggie': 'maggie_greene', 'theodore': 'theodore_douglas',
                            't-dog': 'theodore_douglas', 'andrea': 'andrea_harrison', 'morales': 'morales', 'jacqui': 'jacqui', 
                            'merle': 'merle_dixon', 'jim': 'jim', 'sophia': 'sophia', 'dale': 'dale_horvath', 'guillermo': 'guillermo', 
                            'abuela': 'abuela', 'felipe': 'felipe', 'edwin': 'edwin_jenner', "vi":"vi",
                            'jenner': 'edwin_jenner', "dr": 'edwin_jenner'

                          },

        # TheOffice
        "TheOffice" : { 'michael': 'michael_scott', 'jim': 'jim_halpert', 'pam': 'pam_beesly', 
                       'dwight': 'dwight_schrute', 'jan': 'jan_levinson', 'todd': 'todd_packer', 
                       'phyllis': 'phyllis_vance', 'stanley': 'stanley_hudson', 'oscar': 'oscar_martinez', 
                       'angela': 'angela_martin', 'kevin': 'kevin_malone', 'ryan': 'ryan_howard', 
                       'roy': 'roy_anderson', 'meredith': 'meredith_palmer', 'toby': 'toby_flend', 'madge': 'madge',
                       'katy': 'katy', 'kelly': 'kelly_kapoor', 'creed': 'creed_bratton'

                          },

        # TBBT
        "TheBigBangTheory" : { 'sheldon': 'sheldon_cooper', 'leonard': 'leonard_hofstadter', 'althea': 'althea', 
                              'penny': 'penny', 'howard': 'howard_wolowitz', 'raj': 'raj_koothrappali', 
                              'kurt': 'kurt',  'doug': 'doug', 'leslie': 'leslie_winkle','mary': 'mary_cooper',
                              'roberta': 'roberta', 'patty': 'patty', 'cheryl': 'cheryl', 'vicki': 'vicki',
                              'christy': 'christy_vanderbilt', 'chen': 'chen', 'debbie': 'debbie_wolowitz',
                              'lalita': 'lalita_gupta',  'toby': 'toby_loobenfeld', 'dennis': 'dennis_kim',
                              'eric': 'dr_eric_gablehauser', 'gablehauser': 'dr_eric_gablehauser', 'dmitri': 'dmitri',
                              'mike': 'mike', 'missy': 'missy_cooper',  'dan': 'dan', 'althea': 'althea',

                          },

        # BuffyTheVampireSlayer
        "BuffyTheVampireSlayer" : { 'darla': 'darla', 'joyce': 'joyce_summers', 'buffy': 'buffy_summers', 
                                'xander': 'xander_harris', 'willow': 'willow_rosenberg', 'jesse': 'jesse',
                              'cordelia': 'cordelia_chase', 'rupert': 'rupert_giles', 'aphrodesia': 'aphrodesia', 
                                'aura': 'aura', 'luke': 'luke', 'angel': 'angel', 'thomas': 'thomas', 'darla': 'darla',
                              'colin': 'colin',  'lishanne': 'lishanne',  'catherine': 'catherine_madison',
                            'madison': 'catherine_madison', 'blayne': 'blayne_moll', 'collin': 'collin', 'andrew': 'andrew_wells',
                            'kyle': 'kyle_dufours', 'tor': 'tor_hauer', 'rhonda': 'rhonda_kelley', 'weirick': 'dr_weirick', 
                            'zookeeper': 'dr_weirick', 'dave': 'dave', 'jenny': 'jenny_calendar', 'fritz': 'fritz',
                            'marc': 'marc', 'lisa': 'lisa', 'elliot': 'elliot', 'snyder': 'principal_snyder', 
                            'morgan': 'morgan_shay', 'sid': 'sid', 'emily': 'emily_', 'laura': 'laura',  'billy': 'billy_palmer',
                            'hank': 'hank_summers', 'aldo': 'aldo_gianfranco', 'tishler': 'ms_tishler',  'wendell': 'wendell',
                            'miller': 'ms_miller', 'kevin': 'kevin'

                          },

        # StarWars
        "StarWars": {'anakin': 'anakin_skywalker', 'obiwan': 'obiwan_kenobi', 'obiwan-kenobi': 'obiwan_kenobi',
                     'kenobi': 'obiwan_kenobi', 'qui-gon': 'quigon_jinn', 'ani': 'anakin_skywalker',
                   'grievous':'general_grievous#unknown#StarWars.Episode03', "chancellor":"the_emperor",
                   'ani': 'anakin_skywalker', 'padme': 'padme', 'yoda': 'yoda', 'kiadimundi': 'kiadimundi', 
                    'boba': 'boba_fett', 'tion': 'tion_medon', 'nute': 'nute_gunray#unknown#StarWars.Episode03', 
                   'gunray': 'nute_gunray#unknown#StarWars.Episode03', 'mace': 'mace_windu',
                   'organa': 'senator_bail_organa', 'darth': 'darth_vader', 'vader':  'darth_vader',
                     "3po": "c3po", "r2" : "r2d2", "lando":'lando_calrissian', 'greedo': 'greedo', 
                     'jabba': 'jabba_the_hutt', 'chewbacca': 'chewbacca', 'chewie': 'chewbacca', 'aunt': 'aunt_beru', 
                     'luke': 'luke_skywalker', 'uncle': 'uncle_owen', 'owen': 'uncle_owen', 'beru': 'aunt_beru',
                     'leia': 'princess_leia', 'wedge': 'wedge', 'daine': 'daine_jir', 'dodonna': 'general_dodonna', 
                     'tarkin': 'grand_moff_tarkin', 'wuher': 'wuher', "biggs": "red_three_", "BB-8": "bb8_performed_by",
                     "artoo" : "r2d2", "r2-d2" : "r2d2", "rey":"rey", "finn": "finn", 'kylo': 'kylo_ren', 
                     'fn2187': 'fn2187', 'poe': 'poe_dameron', 'dameron': 'poe_dameron', 'hux':'general_hux',
                     'han': 'han_solo', 'solo': 'han_solo', 'annie': 'anakin_skywalker'
                    },

        #HarryPotter
        "HarryPotter": { 'albus': 'albus_dumbledore','dumbledore': 'albus_dumbledore', 'quirrell': 'professor_quirinus_quirrell', 
                        'rubeus': 'rubeus_hagrid','hagrid': 'rubeus_hagrid', 'petunia': 'petunia_dursley', 
                        'dudley': 'dudley_dursley', 'vernon': 'vernon_dursley', 'harry': 'harry_potter',
                        'molly': 'molly_weasley', 'george': 'george_weasley', 'fred': 'fred_weasley', 
                        'ginny': 'ginny_weasley', 'ron': 'ron_weasley', 'neville': 'neville_longbottom', 'draco': 'draco_malfoy', 
                        'seamus': 'seamus_finnigan', 'argus': 'argus_filch', 'marcus': 'marcus_flint',
                        'snape':'professor_severus_snape', 'severus':'professor_severus_snape',

                    },
        #BB
        "BreakingBad": { 'hank': 'hank_schrader', 'steven': 'steven_gomez', 'gomie': 'steven_gomez',
                        'marie': 'marie_schrader', 'skyler': 'skyler_white', 'walter': 'walter_white',
                        'jr': 'walter_white_jr', 'jesse': 'jesse_pinkman', 'pete': 'skinny_pete', 'combo': 'combo',
                        'jake': 'jake_pinkman','badger': 'badger', 'elliott': 'elliott_schwartz', 'gretchen': 'gretchen_schwartz', 'farley': 'farley',
                        'soren': 'soren', 'louis': 'louis', 'nodoze': 'nodoze', 'tuco': 'tuco_salamanca',
                        'krazy8': 'krazy8', 'carmen': 'carmen_molina', 'hugo': 'hugo_archuleta', 'jock': 'jock',
                        'ben': 'ben', 'bogdan': 'bogdan_wolynetz', 'chad': 'chad', 'emilio': 'emilio_koyama',
                        'wendy': 'wendy'
                    },
        # Friends
        "Friends": {'monica': 'monica_geller', 'joey': 'joey_tribbiani', 'chandler': 'chandler_bing', 'phoebe': 
                'phoebe_buffay', 'ross': 'dr_ross_geller', 'rachel': 'rachel_green', 'jasmine': 'jasmine', 
                'paul': 'paul','franny': 'franny', 'marsha': 'marsha', 'carol': 'carol_willick',
                'judy': 'judy_geller', 'jack': 'jack_geller', 'susan': 'susan', 'barry': 'barry', 'bobby': 'bobby',
                'paula': 'paula', 'alan': 'alan', 'lizzy': 'lizzy', 'leslie': 'leslie', 'kiki': 'kiki', 'joanne': 'joanne',
                'angela': 'angela', 'janice': 'janice', 'bob': 'bob', 'aurora': 'aurora', 'shelly': 'shelly',
                'terry': 'terry', 'heckles': 'mr_heckles', 'paolo': 'paolo', 'max': 'max', 'david': 'david',
                'sandy': 'sandy', 'bobby': 'fun_bobby', 'dick': 'dick_clark','jay': 'jay_leno', 'nora': 'nora_tyler_bing',
                },
        # BSG
        "BattlestarGalactica" : { 'lee': 'cpt_lee_adama', 'president': 'president_laura_roslin', 'laura': 'president_laura_roslin',
                             'roslin': 'president_laura_roslin', 'gaius': 'dr_gaius_baltar', 'baltar': 'dr_gaius_baltar',
                             'billy': 'billy_keikeya', 'keikeya': 'billy_keikeya', 'socinus': 'crewman_specialist_socinus',
                             'tyrol': 'chief_galen_tyrol', 'sharon': 'lt_sharon_valerii', 'boomer': 'lt_sharon_valerii',
                             'dualla': 'officer_anastasia_dualla', 'william': 'admiral_william_adama', 'saul': 'colonel_saul_tigh',
                             'crashdown': 'crashdown', 'karl': 'captain_karl_agathon', 'crashdown': 'crashdown', 'agathon': 'captain_karl_agathon',
                             'cally': 'crewman_specialist_cally_henderson', 'gaeta': 'lt_felix_gaeta', 'tom': 'tom_zarek',
                             'zarek': 'tom_zarek', 'kara': 'captain_kara_thrace', 'starbuck': 'captain_kara_thrace',
                            'aaron': 'aaron_doral', 'boxey': 'boxey', 'mason': 'mason','hotdog': 'lt_brendan_constanza',
                             'cottle': 'dr_cottle', 'zak': 'zak_adama', 'chuckles': 'chuckles',
                
    },
    
}

    # #### Find entity linking
    for sentence in sentences:

        for word in sentence:

            # find 1st pronoun without EL
            if str(word).lower() in firt_prn and (word._.entity_linking == '_' or word._.entity_linking == '?'):
                print("FIRST PRONOUN FOUND",sentence) 
                word._.entity_linking = word._.speaker
                print("----->", word, word._.entity_linking)

            # find 2nd pronoun without EL
            if str(word).lower()  in second_prn and (word._.entity_linking == '_' or word._.entity_linking == '?'):
                print("SECOND PRONOUN FOUND",sentence)
                word._.entity_linking = word._.addressee
                print("----->", word, word._.entity_linking)

            for el, val in knowledge[serie].items() : 
                if str(word).lower() == el and (word._.entity_linking == '_' or word._.entity_linking == '?'):
                    print("NAME FOUND",sentence)
                    word._.entity_linking = val
                    print("----->", word, word._.entity_linking)

            if word._.entity_linking == "?":
                word._.entity_linking = "_"

    # #### Write temp file
    temp_file = open(f'{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.temp', 'w')
    with open(episode_path, 'r') as f:
        for line in f :
            #print(line)
            line = line.strip('\n')
            # if all colons are here, skip
            if len(line.split()) == 8:
                temp_file.write(f'{line}\n')
            elif len(line.split()) == 7:
                temp_file.write(f'{line} _\n')
    temp_file.close()

    # #### Write new file
    print(f"Writing new alignment file to {DATA_PLUMCOT}/{serie}/forced-alignment")
    new_file = open(f"{DATA_PLUMCOT}/{serie}/forced-alignment/{episode}.aligned", "w")

    for sentence in sentences:
        for word in sentence:
            confidence = "{:.2f}".format(word._.confidence)
            start_time = "{:.2f}".format(word._.start_time)
            end_time = "{:.2f}".format(word._.end_time)
            if word._.entity_linking == "?":
                word._.entity_linking = "_"
            if word._.entity_linking == "" or word._.addressee == " " :
                word._.entity_linking = "_"
            new_file.write(f'{episode} {word._.speaker} {start_time} {end_time} {word} {confidence} {word._.entity_linking} {word._.addressee}\n')

    new_file.close()
