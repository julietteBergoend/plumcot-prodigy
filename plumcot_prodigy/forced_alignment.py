import functools
from pathlib import Path
import spacy
from typing import Dict, List, Text
from spacy.tokens import Doc, Span


class ForcedAlignment:
    """Forced alignment (.aligned) loader

    Usage
    -----
    >>> forced_alignment = ForceAlignment()
    >>> transcript = forced_alignment("/path/to/file.aligned")

    >>> for sentence in transcript.sents:
    ...     speaker = sentence._.speaker
    ...     start_time = sentence._.start_time
    ...     end_time = sentence._.end_time
    ...     transcription = sentence.text

    >>> for token in sentence:
    ...     speaker = token._.speaker
    ...     start_time = token._.start_time
    ...     end_time = token._.end_time
    ...     confidence = token._.confidence
    ...     word = token.text
    """

    @staticmethod
    def placeholder(doc: Doc) -> Doc:
        """A spaCy pipeline component that does nothing"""
        return doc

    @staticmethod
    def add_forced_alignment_attrs(attributes: List[Dict], doc: Doc) -> Doc:
        """A spaCy pipeline component that adds token attributes"""

        for attr, token in zip(attributes, doc):
            for attr_name, attr_value in attr.items():
                setattr(token._, attr_name, attr_value)
        return doc

    @staticmethod
    def start_sentence_at_speaker_change(doc: Doc) -> Doc:
        """A spaCy pipeline component that ensures that a new sentence starts at each speaker change"""
        for token in doc[1:]:
            if token._.speaker != doc[token.i - 1]._.speaker:
                token.is_sent_start = True
        return doc

    @staticmethod
    def span_speaker(span: Span) -> Text:
        """Get sentence speaker"""
        speakers = set(token._.speaker for token in span)
        if len(speakers) != 1:
            raise ValueError(f"Span '{span}' contains multiple speakers: {speakers}")
        return speakers.pop()

    @staticmethod
    def span_start_time(span: Span) -> Text:
        """Compute sentence start time as the minimum of its words start times"""
        return min(token._.start_time for token in span)

    @staticmethod
    def span_end_time(span: Span) -> Text:
        """Compute sentence end time as the maximum of its words end times"""
        return max(token._.end_time for token in span)
 
    @staticmethod
    def span_average_confidence(span: Span) -> Text:
        """Compute sentence average confidence"""
        return sum(token._.confidence for token in span) / len(span)

    def __init__(self):

        # register Token attributes if they are not registered already
        from spacy.tokens import Token

        for attr_name in ["speaker", "start_time", "end_time", "confidence"]:
            if not Token.has_extension(attr_name):
                Token.set_extension(attr_name, default=None)

        # register Span attributes if they are not registered already
        from spacy.tokens import Span

        if not Span.has_extension("speaker"):
            Span.set_extension("speaker", getter=self.span_speaker)

        if not Span.has_extension("start_time"):
            Span.set_extension("start_time", getter=self.span_start_time)

        if not Span.has_extension("end_time"):
            Span.set_extension("end_time", getter=self.span_end_time)
            
        if not Span.has_extension("confidence"):
            Span.set_extension("confidence", getter=self.span_average_confidence)

        # minimalist spaCy pipeline (used only for its tokenizer)
        self.tokenizer = spacy.load(
            "en_core_web_sm", disable=["tagger", "parser", "ner"]
        )

        # custom spaCy pipeline (that adds forced alignment attributes and ensures
        # that a new sentence starts at every speaker change)
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.add_pipe(self.placeholder, name="forced_alignment", first=True)
        self.nlp.add_pipe(
            self.start_sentence_at_speaker_change, after="forced_alignment"
        )

    def __call__(self, trs: Path) -> Doc:

        # load the whole file
        with open(trs, "r") as fp:
            lines = fp.readlines()

        # for each word, load its attributes (speaker, start_time, end_time, confidence)
        source_tokens, source_attrs = [], []
        for line in lines:
            (
                episode,
                speaker,
                start_time,
                end_time,
                word,
                confidence,
            ) = line.strip().split()
            source_tokens.append(word)
            source_attrs.append(
                {
                    "speaker": speaker,
                    "start_time": float(start_time),
                    "end_time": float(end_time),
                    "confidence": float(confidence),
                }
            )

        # tokenize with spaCy's default tokenizer
        source_content = " ".join(source_tokens)
        target = self.tokenizer(source_content)

        # align forced alignment (source) own tokenization with spaCy's tokenization (target)
        cost, s2t, t2s, s2t_multi, t2s_multi = spacy.gold.align(
            source_tokens, [token.text for token in target]
        )

        # ... and propagate attributes from source to target
        target_attrs = []

        revert_s2t_multi = dict()
        for s, t in s2t_multi.items():
            if t not in revert_s2t_multi:
                revert_s2t_multi[t] = list()
            revert_s2t_multi[t].append(s)

        for t, target_token in enumerate(target):

            if t in revert_s2t_multi:
                aligned_s = revert_s2t_multi[t]
            elif t in t2s_multi:
                aligned_s = [
                    t2s_multi[t],
                ]
            else:
                aligned_s = [
                    t2s[t],
                ]

            speakers = set(source_attrs[s]["speaker"] for s in aligned_s)
            if len(speakers) > 2:
                raise ValueError(
                    f"Token '{target_token}' is mapped with multiple speakers: {speakers}"
                )
            speaker = speakers.pop()
            start_time = min(source_attrs[s]["start_time"] for s in aligned_s)
            end_time = max(source_attrs[s]["end_time"] for s in aligned_s)
            confidence = min(source_attrs[s]["confidence"] for s in aligned_s)
            target_attrs.append(
                {
                    "speaker": speaker,
                    "start_time": start_time,
                    "end_time": end_time,
                    "confidence": confidence,
                }
            )

        # inject aligned attributes into the pipeline
        self.nlp.replace_pipe(
            "forced_alignment",
            functools.partial(self.add_forced_alignment_attrs, target_attrs),
        )

        # run the whole spaCy pipeline
        return self.nlp(source_content)
