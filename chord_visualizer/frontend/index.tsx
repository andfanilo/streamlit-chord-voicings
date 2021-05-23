import "./index.css";

import * as React from "react";
import { useEffect } from "react";
import * as ReactDOM from "react-dom";

import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import { Piano, MidiNumbers } from "react-piano";
import "react-piano/dist/styles.css";

import SoundfontProvider from "./SoundfontProvider";

// webkitAudioContext fallback needed to support Safari.
//const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const audioContext = new window.AudioContext();
const soundfontHostname = "https://d1pzp51pvbm36p.cloudfront.net";

const ChordVisualizer = () => {
  const noteRange = {
    first: MidiNumbers.fromNote("c3"),
    last: MidiNumbers.fromNote("c5"),
  };

  useEffect(() => {
    Streamlit.setFrameHeight();
  });

  return (
    <SoundfontProvider
      instrumentName="acoustic_grand_piano"
      audioContext={audioContext}
      hostname={soundfontHostname}
      render={({ isLoading, playNote, stopNote }) => (
        <Piano
          noteRange={noteRange}
          width={1000}
          playNote={playNote}
          stopNote={stopNote}
          disabled={isLoading}
        />
      )}
    />
  );
};

const StreamlitChordVisualizer = withStreamlitConnection(ChordVisualizer);

ReactDOM.render(
  <React.StrictMode>
    <StreamlitChordVisualizer />
  </React.StrictMode>,
  document.getElementById("app")
);
