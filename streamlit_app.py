import numbers
from dataclasses import dataclass
from typing import Dict
from typing import List

import sexpdata
import streamlit as st
from music21.interval import Interval
from music21.pitch import Pitch
from music21.scale import ConcreteScale
from sexpdata import car
from sexpdata import cdr
from sexpdata import Symbol

from chord_visualizer import st_visualize_chord


def _sexpdata_to_dict(d: List[Symbol]) -> Dict:
    """Build a Dict from a parsed S-expression, as
    cat -> key, cdr -> value
    """
    return {car(v).value(): cdr(v) for v in d}


def _cdr_to_str(l: List[Symbol]) -> str:
    """A CDR is a list of children Symbols. 
    Extract the value of every children and join them into a string.
    """
    return " ".join([str(w) if isinstance(w, numbers.Number) else w.value() for w in l])


def _list_notes_to_str(l: List[Pitch]) -> str:
    return " ".join([str(note) for note in l])


def _format_pitch(n: str) -> Pitch:
    """c8 represents an eight-note middle C.
    c-/c+ transposes to one octave lower/higher

    We don't need the duration info and need to build octave from the -/+ info 
    (music21 would consider those as accidentals instead of octave transposition).

    So _format_pitch(c8) --> Pitch('C')
    So _format_pitch(g+8) --> Pitch('G5')
    """
    return Pitch(
        (
            n.capitalize()
            .replace("8", "")
            .replace("---", "1")
            .replace("--", "2")
            .replace("-", "3")
            .replace("+", "5")
            .replace("++", "6")
            .replace("+++", "7")
        )
    )


def _transpose_list_notes(
    from_note: Pitch, to_note: Pitch, list_to_transpose: List[Pitch]
) -> List[Pitch]:
    interval = Interval(from_note, to_note)
    return [note.transpose(interval) for note in list_to_transpose]


@dataclass
class Voicing:
    name: str
    type: str
    notes: List[Pitch]
    extension: List[Pitch]


@dataclass
class ParsedChord:
    name: str
    pronounce: str
    key: Pitch
    family: str
    spell: List[Pitch]
    color: List[Pitch]
    priority: List[Pitch]
    approach: List[List[Pitch]]
    voicings: List[Voicing]
    extensions: List[str]  # should be chord names
    scales: List[str]
    avoid: List[Pitch]
    substitute: List[str]  # should be chord names
    same: List[str]


@st.cache(allow_output_mutation=True, hash_funcs={Symbol: lambda s: s.value()})
def load_vocabulary(fn: str) -> List[Symbol]:
    with open(fn, "r+") as f:
        contents = "\n".join(f.readlines())
        return sexpdata.loads("({})".format(contents.replace("'", "")))


def extract_scales(dictionary: List[Symbol]) -> Dict[str, ConcreteScale]:
    raw_scales: List[Dict] = [
        _sexpdata_to_dict(cdr(w)) for w in dictionary if car(w).value() == "scale"
    ]
    parsed_scales: Dict[str, ConcreteScale] = {}
    for scale in raw_scales:
        name: str = _cdr_to_str(scale["name"])
        if "spell" in scale:
            spell: List[str] = [
                f"{w.value().capitalize()}4" for w in scale["spell"][:-1]
            ]
            spell: ConcreteScale = ConcreteScale(pitches=spell)
        else:
            # given the file, any scales without spells have been already defined by their "same" scale attribute
            spell = parsed_scales[_cdr_to_str(scale["same"])]
        parsed_scales[name] = spell
    return parsed_scales


def extract_chords(dictionary: List[Symbol]) -> Dict[str, ParsedChord]:
    raw_chords: List[Dict] = [
        _sexpdata_to_dict(cdr(w)) for w in dictionary if car(w).value() == "chord"
    ]

    parsed_chords: Dict[str, ParsedChord] = {}  # holds the final list of chords
    same_chord_mapping: Dict[
        str, List[str]
    ] = {}  # holds chords with a "same" attribute to push to 'parsed_chords' when all chords have been extracted

    def _parse_voicings(raw_voicings: List[Symbol]) -> List[Voicing]:
        parsed_voicings = []
        for v in raw_voicings:
            name = car(v).value()
            voicing = _sexpdata_to_dict(cdr(v))
            typing = _cdr_to_str(voicing["type"])
            notes = [_format_pitch(n.value()) for n in voicing["notes"]]
            extension = [_format_pitch(n.value()) for n in voicing["extension"]]
            parsed_voicings.append(
                Voicing(name=name, type=typing, notes=notes, extension=extension,)
            )
        return parsed_voicings

    for chord in raw_chords:
        name = _cdr_to_str(chord["name"])
        if "same" in chord:
            same = _cdr_to_str(chord["same"])
            same_chord_mapping[name] = same
        else:
            pronounce = _cdr_to_str(chord["pronounce"])
            key = _format_pitch(_cdr_to_str(chord["key"]))
            family = _cdr_to_str(chord["family"])
            spell = [_format_pitch(note.value()) for note in chord["spell"]]
            color = [_format_pitch(note.value()) for note in chord["color"]]
            priority = [_format_pitch(note.value()) for note in chord["priority"]]
            approach = [
                [_format_pitch(note.value()) for note in list_of_notes]
                for list_of_notes in chord["approach"]
            ]
            voicings = _parse_voicings(chord["voicings"])
            extensions = [ch.value() for ch in chord["extensions"]]
            scales = [" ".join([name.value() for name in sc]) for sc in chord["scales"]]
            avoid = [_format_pitch(av.value()) for av in chord["avoid"]]
            substitute = [sub.value() for sub in chord["substitute"]]
            parsed_chords[name] = ParsedChord(
                name=name,
                pronounce=pronounce,
                key=key,
                family=family,
                spell=spell,
                color=color,
                priority=priority,
                approach=approach,
                voicings=voicings,
                extensions=extensions,
                scales=scales,
                avoid=avoid,
                substitute=substitute,
                same=[],
            )

    for chord, similar_chord in same_chord_mapping.items():
        if similar_chord in parsed_chords:
            parsed_chords[similar_chord].same.append(chord)
        else:
            # probably a nested "same"
            parsed_chords[same_chord_mapping[similar_chord]].same.append(chord)
    return parsed_chords


def main():
    st.title("Piano Chord Voicings")
    st.caption(
        "Exploring all piano voicings defined in [Impro-Visor's dictionary](https://github.com/Impro-Visor/Impro-Visor/blob/master/vocab/My.voc)."
    )
    vocabulary = load_vocabulary("./data/My.voc")
    chords = extract_chords(vocabulary)

    with st.sidebar:
        st.header("Configuration")
        selected_chord = chords[
            st.selectbox("Select a chord type:", list(chords.keys()))
        ]

        all_voicings = selected_chord.voicings

        def format_voicing(v: Voicing):
            return f"{v.name} - {v.type}"

        selected_voicing = st.selectbox(
            "Select voicing:", all_voicings, format_func=format_voicing
        )

    st_visualize_chord(chord=selected_voicing.notes)

    st.markdown(
        f"""
**Pronounce**: {selected_chord.pronounce}  
**Family**: {selected_chord.family}  
**Spell**: {_list_notes_to_str(selected_chord.spell)}  
**Color**: {_list_notes_to_str(selected_chord.color)}  
**Priority**: {_list_notes_to_str(selected_chord.priority)}  
**Approaches**: { " _or_ ".join([_list_notes_to_str(list_notes) for list_notes in selected_chord.approach])}  
**Extensions**: { " _or_ ".join(selected_chord.extensions)}  
**Scales**: { " _or_ ".join(selected_chord.scales)}  
**Avoid**: {_list_notes_to_str(selected_chord.avoid)}    
**Substitute**: { " _or_ ".join(selected_chord.substitute)}  
**Selected voicing**: {_list_notes_to_str(selected_voicing.notes)}  
"""
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Visualizing Impro-Visor Chord voicings",
        page_icon="musical_keyboard",
        layout="wide",
    )
    main()
