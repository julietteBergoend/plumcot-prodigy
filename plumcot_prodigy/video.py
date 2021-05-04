from moviepy.editor import *
from tempfile import NamedTemporaryFile
import base64
from typing import Dict, Text
from pathlib import Path

def mkv_to_base64(mkv: Path, start_time: float, end_time: float) -> Text:
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
    
    episode = mkv.split('/')[-1]
    episode = episode.strip('.mkv')
    
    home = Path(__file__).parent.absolute()
    
    audio_path = f"{home}/data/{episode.split('.')[0]}/{episode}.en16kHz.wav"

    background_audio_clip = AudioFileClip(audio_path).subclip(start_time, end_time)
    
    final_clip = video.set_audio(background_audio_clip)
    
    with NamedTemporaryFile(mode="wb", suffix=".mp4", delete=True) as fw:
        final_clip.write_videofile(fw.name, preset="ultrafast", logger=None)
        with open(fw.name, mode="rb") as fr:
            b64 = base64.b64encode(fr.read()).decode()
    return f"data:video/mp4;base64,{b64}"