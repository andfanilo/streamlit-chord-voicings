# Visualizing Impro-Visor Chord voicings

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/andfanilo/streamlit-chord-voicings/main)

## Development

### Install

- JS side

```shell script
cd chord_visualizer/frontend
npm install
```

- Python side

```shell script
conda create -n streamlit-custom python=3.7
conda activate streamlit-custom
pip install -e .
```

### Run

Both Parcel dev server and Streamlit should run at the same time.

- JS side

```shell script
npm run dev
```

- Python side

```shell script
streamlit run streamlit_app.py
```

### Build frontend

```shell script
npm run build
```

## Resources

Huge credits to the Impro-Visor team for creating this awesome musicology tool and consolidating all of this data!

- [Impro-Visor official website](https://www.cs.hmc.edu/~keller/jazz/improvisor/)
- [Impro-Visor Leadsheet Notation](https://www.cs.hmc.edu/~keller/jazz/improvisor/LeadsheetNotation.pdf)
