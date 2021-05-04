import prodigy
from pathlib import Path
from typing import Dict, List, Text, Union
from typing_extensions import Literal
from pyannote.audio import Audio, Inference, Model
from pyannote.core import Segment
import torch
import io
import scipy.io.wavfile
import base64
import numpy as np
import faiss
from collections import Counter
from moviepy.editor import *
from tempfile import NamedTemporaryFile
from prodigy.util import file_to_b64
from plumcot_prodigy.custom_loaders import *

class SpeakerStream:
    def to_base64(self, waveform: np.ndarray, sample_rate: int) -> Text:
        """Convert waveform to base64 data"""

        waveform /= np.max(np.abs(waveform)) + 1e-8

        with io.BytesIO() as content:
            scipy.io.wavfile.write(content, sample_rate, waveform)
            content.seek(0)
            b64 = base64.b64encode(content.read()).decode()
            b64 = f"data:audio/x-wav;base64,{b64}"
        return b64
    
    def mkv_to_base64(self, mkv: Path, start_time: float, end_time: float) -> Text:
        """Extract video excerpt for use with prodigy
        Parameters
        ----------
        mkv : Path
            Path to mkv video file
        start_time : float
            Excerpt start time in seconds.
        end_time : float
            Excerpt end time in seconds.
        """

        video = VideoFileClip(mkv).subclip(start_time, end_time)
        with NamedTemporaryFile(mode="wb", suffix=".mp4", delete=True) as fw:
            video.write_videofile(fw.name, preset="ultrafast", logger=None)
            with open(fw.name, mode="rb") as fr:
                b64 = base64.b64encode(fr.read()).decode()
        return f"data:video/mp4;base64,{b64}"

    def __init__(
        self,
        source,
        speakers: List[Text] = None,
        allow_new_speaker: bool = False,
        context: float = 0.5,
    ):
        super().__init__()

        self.source = source
        self.speakers = set() if speakers is None else set(speakers)
        self.allow_new_speaker = allow_new_speaker

        # how many seconds to play before and after the speech turn
        self.context = context

        # initialize audio reader
        self.audio = Audio(sample_rate=16000, mono=True)

        # initialize voice activity detection and speaker embedding models
        # use GPUs when available
        if torch.cuda.is_available():
            vad_device = torch.device("cuda", index=0)
            emb_device = torch.device(
                "cuda", index=1 if torch.cuda.device_count() > 1 else 0
            )
        else:
            vad_device = torch.device("cpu")
            emb_device = torch.device("cpu")

        self.embedding = Model.from_pretrained(
            "hbredin/SpeakerEmbedding-XVectorMFCC-VoxCeleb",
            map_location=emb_device,
            strict=False,
        )
        self.voice_activity_detection = Inference(
            "hbredin/VoiceActivityDetection-PyanNet-DIHARD", device=vad_device
        )

        # index meant to store embeddings (and corresponding speaker ids)
        self.index = faiss.IndexFlatIP(self.embedding.introspection.dimension)
        self.speaker_ids = list()

    def compute_embedding(self, example) -> np.ndarray:

        audio_file = example["audio"]
        
        meta = example["meta"]
        start = meta["start"]
        end = meta["end"]

        chunk = Segment(start=start, end=end)

        # extract audio from current speech turn
        waveform, sample_rate = self.audio.crop(audio_file, chunk)

        with torch.no_grad():

            # run voice activity detection
            weights = self.voice_activity_detection(
                {"waveform": waveform, "sample_rate": sample_rate}
            ).data[:, 0]

            # extract speaker embedding from current speech turn
            weights = torch.tensor(weights).unsqueeze(0)

            # TODO: catch shape mismatch warning
            embedding = (
                self.embedding(waveform.unsqueeze(0), weights=weights).cpu().numpy()
            )

            # L2-normalize embedding
            embedding /= np.linalg.norm(embedding, ord=2, axis=1, keepdims=True)

        return embedding
    
    def on_load(self):
        # TODO: load index from disk
        pass

    def on_exit(self, controller):
        # TODO: save index to disk
        pass

    def validate_answer(self, eg):

        # no need to validate examples which were not accepted
        if eg["answer"] != "accept":
            return

        # neither checkbox nor text field is used
        if not (eg["accept"] or eg.get("other_speaker", False)):
            raise ValueError("Looks like you forgot to annotate this example.")

        # trying to create a new speaker but it is not allowed
        other_speaker = eg.get("other_speaker", False)
        if (
            (other_speaker)
            and (other_speaker not in self.speakers)
            and (not self.allow_new_speaker)
        ):
            raise ValueError(
                "Looks like you are trying to create a new speaker but this is not allowed."
            )

        # checkbox and text field disagree
        if eg["accept"] and eg.get("other_speaker", eg["accept"][0]) != eg["accept"][0]:
            raise ValueError(f"Is it {eg['accept'][0]} or {eg['other_speaker']}?")

    def update(self, answers):

        for eg in answers:

            # skip answers that are not "accept"
            if eg["answer"] != "accept":
                continue

            # add embedding to index
            self.index.add(np.array(eg["embedding"], dtype=np.float32))

            # add corresponding speaker_id
            if "other_speaker" in eg:
                speaker_id = eg["other_speaker"]
            else:
                speaker_id = eg["accept"][0]

            self.speakers.add(speaker_id)
            self.speaker_ids.append(speaker_id)

    def before_db(self, examples):

        for eg in examples:
            del eg["audio"]
            del eg["embedding"]
            del eg["video"]
            del eg["options"]
            del eg["field_suggestions"]
            del eg["field_id"]
            del eg["field_label"]

        return examples

    def __call__(self):
        
        print("Loading embeddings...")
        for speech_turn in prodigy.get_stream(self.source):
            embedding = self.compute_embedding(speech_turn)

            # if locutor is known:
            # add his name and embedding to index
            if speech_turn["answer"] == "accept":
                speaker_id = speech_turn["accept"][0]
                self.speakers.add(speaker_id)
                self.speaker_ids.append(speaker_id)
                # add embedding to index
                self.index.add(np.array(embedding, dtype=np.float32))
            
            # else, find most probable locutor
            elif speech_turn["answer"] != "accept": 
                print('\n', speech_turn['sentence'])                
                # if index contains at least one embedding, look for 100 nearest neighbors
                # and sort speakers from most common to least common neighbor
                if self.index.ntotal > 0:
                    _, I = self.index.search(embedding, min(5, self.index.ntotal))
                    nearest_neighbors = Counter([self.speaker_ids[i] for i in I[0]])

                    # diviser nb de voisins par nb annotations
                    annotations_count = Counter(self.speaker_ids)
                    scores = {speaker:nearest_neighbors[speaker]/annotations_count[speaker] for speaker in nearest_neighbors}
                    #print('Nearest neighbors :', nearest_neighbors)                
                    #print('Compteur d annotations :',Counter(self.speaker_ids))
                    #print('Scores :', scores)
                    #print('Max Scores :', max(scores, key=scores.get))
                    
            
                # if it does not, use "Bootstraping" placeholder to let user know
                # they should be patient and annotate a few more speech turns
                # before they can benefit from speaker recognition
                else:
                    nearest_neighbors = Counter(["Bootstraping..."] * 1)
                    scores = Counter(["Bootstraping..."] * 1)

                # prepare audio chunk for display in prodigy
                duration = self.audio.get_duration(speech_turn["audio"])
                metas = speech_turn["meta"]
                chunk = Segment(start=metas["start"], end=metas["end"])
                chunk_with_context = Segment(
                    start=max(0, metas["start"] - self.context),
                    end=min(duration, metas["end"] + self.context),
                )
                waveform_with_context, sample_rate = self.audio.crop(
                    speech_turn["audio"], chunk_with_context
                )
                audio_spans = [
                    {
                        "start": chunk.start - chunk_with_context.start,
                        "end": chunk.end - chunk_with_context.start,
                        "label": "WHO IS THIS SPEAKER?",
                    }
                ]
                # episode name
                episode = metas["episode"]
                serie = episode.split('.')[0]
                # images for choice view
                path =  Path(__file__).parent.absolute()
                im_path =  f"{path}/data/images"
                
                credits = load_credits(episode, serie, path)
                # load pictures and characters without one of the current episode
                pictures = load_photo(credits, serie, path)
                # options to display            
                options = []
                already_in_options = []

                # show speaker with highest score first
                for speaker_id, count in reversed(sorted(scores.items(), key=lambda item: item[1])):            
                    # find if current locutor has a picture
                    for name, val in pictures.items():                    
                        if speaker_id == name:
                            # if there is a photo, choose the centroïd
                            if name != val:
                                options.append({"id":speaker_id, "image":file_to_b64(val)})
                                already_in_options.append(str(speaker_id))

                            # else, display its name  
                            elif name == val and name not in already_in_options: 
                                options.append({"id":speaker_id, "text":f"{speaker_id}"})
                                already_in_options.append(str(speaker_id))

                    # display bootstraping
                    if speaker_id not in already_in_options:
                        options.append({"id":speaker_id, "text": f"{speaker_id}"})
                        already_in_options.append(str(speaker_id))

                # display speakers who hasn't score for the moment at the end of the options
                for name, val in pictures.items():
                    # display photo in options
                    # do not display locutor if he already has embeddings, it will be displayed thanks to embeddings
                    if name != val and name not in already_in_options:
                        options.append({"id":name, "image":file_to_b64(val)})                    
                    elif name == val and name not in already_in_options :                    
                        # display character's name when no picture
                        options.append({"id":name, "text": name})

                yield {
                "video": self.mkv_to_base64(speech_turn["mkv"], chunk.start, chunk.end),
                "audio": self.to_base64(
                    waveform_with_context.squeeze(0).numpy(), sample_rate
                ),
                "audio_spans": audio_spans,
                "options": options,
                "text": f"{speech_turn['sentence']}",
                "field_id": "other_speaker",
                "field_label": "None of the above? Choose from the list below (or add a new speaker) by typing its name:",
                "field_placeholder": "firstname_lastname",
                "field_rows": 1,
                "field_autofocus": False,
                "field_suggestions": sorted(self.speakers),
                "meta": {"start_extract": chunk.start, "end_extract": chunk.end, "episode": episode},
                "embedding": embedding.tolist(),
            }


@prodigy.recipe(
    "pyannote.speaker",
    dataset=("Name of dataset to save answers to", "positional", None, str),
    source=("Source", "positional", None, str),
    speakers=(
        "Path to file containing list of speakers (one speaker per line)",
        "option",
        None,
        Path,
    ),
    allow_new_speaker=("Allow adding more speakers", "flag", None, bool),
)
def speaker(
    dataset: Text,
    source: Union[Path, Literal["-"]],
    speakers: Path = None,
    allow_new_speaker: bool = False,
) -> Dict:

    # if -speakers is not used, we force-allow new speaker
    if speakers is None:
        allow_new_speaker = True

    # read list of speakers from file
    else:
        with open(speakers, "r") as f:
            speakers = [line.strip() for line in f.readlines()]

    stream = SpeakerStream(
        source, speakers=speakers, allow_new_speaker=allow_new_speaker,
    )

    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": stream(),
        # "on_load": stream.on_load,
        "validate_answer": stream.validate_answer,
        "update": stream.update,
        "before_db": stream.before_db,
        # "on_exit": stream.on_exit,
        "config": {
            "buttons": ["accept", "ignore"],
            "choice_auto_accept": True,
            "custom_theme": {
                "cardMaxWidth": 1500,
                "cardMinWidth": 1500,                
                            },
            "batch_size": 5,
            "blocks": [
                        {"view_id": "text"},
                        {"view_id": "choice"}, 
                        {"view_id": "text_input"}
                      ],
            "audio_autoplay": True,
            "audio_loop": False,
            "show_audio_minimap": False,
            "audio_bar_width": 3,
            "audio_bar_height": 1,
            "audio_rate": 1.0,
            # css : video, grid disposition, 
            "global_css": ".c01143 {width:auto;} .c01150 {flex-wrap:auto;} .c01187 {width:auto;} .c01170 {width:60% ; height:60%;}",
            #"global_css": ".c0158 {cursor:pointer; width:60%; height:60%;} .c0175 {width: 100px;} .c0131 {width:auto; font-size:15px; word-wrap: break-word; overflow-wrap: break-word; white-space: pre-wrap; } .c0138 {grid-template-columns: repeat(10,auto); grid-gap:1px; padding: 1px;} .c0175 {max-width :100px;} .c0177 {margin-right :auto;}",
        },
    }