# Seattle Weather Explorer

An interactive Streamlit app for exploring daily Seattle weather observations from 2012 through 2015. [Open the app](https://seattle-weather-explorer-e4mbulpv5yhacgyuwh2qnq.streamlit.app/).

The [Seattle Weather dataset](https://vega.github.io/vega-datasets/datapackage.html) contains 1,461 daily records adapted from NOAA observations for instructional use. It includes dates, weather conditions, precipitation, daily maximum and minimum temperatures, and wind speed. This short record is intended for exploring seasonal weather patterns, not long-term climate change.

Visitors can filter by weather type, maximum temperature, and date range. The app updates summary statistics, a temperature-over-time chart, and an expandable table. A reset button restores all records, and an empty-results message helps users adjust their selections.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, normally `http://localhost:8501`. Press `Ctrl+C` to stop the app. If `.venv` already exists, skip the environment-creation command.

`app.py` contains the interface and analysis; `seattle-weather.csv` contains the data; `styles.css` and `.streamlit/config.toml` define the blue-and-gray appearance.
