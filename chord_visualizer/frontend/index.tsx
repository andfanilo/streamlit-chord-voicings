import "./index.css";

import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

import * as React from "react";
import { useEffect } from "react";
import * as ReactDOM from "react-dom";

const ChordVisualizer = () => {
  useEffect(() => {
    Streamlit.setFrameHeight();
  });

  return <>Hello world</>;
};

const StreamlitChordVisualizer = withStreamlitConnection(ChordVisualizer);

ReactDOM.render(
  <React.StrictMode>
    <StreamlitChordVisualizer />
  </React.StrictMode>,
  document.getElementById("app")
);
