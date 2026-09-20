from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Seattle Weather Explorer", layout="wide")

# Keep presentation separate from the filtering and calculations below.
styles = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

st.title("Seattle Weather Explorer")
st.write(
    "Explore Seattle's daily weather from 2012 through 2015. "
    "Compare weather conditions, temperatures, and precipitation "
    "to learn about seasonal patterns."
)
st.write(
    "Each record represents one day. Temperature is measured in °C "
    "and precipitation in mm."
)
with st.expander("About the dataset"):
    st.write(
        "This historical dataset covers 2012–2015. Use it to explore seasonal "
        "weather patterns, not to forecast weather or draw conclusions about "
        "long-term climate change. Weather categories were derived from NOAA "
        "observations for instructional use."
    )


@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "seattle-weather.csv"
    # Parse dates so the date-range control can filter them.
    return pd.read_csv(csv_path, parse_dates=["date"]).sort_values("date")


data = load_data()
minimum_temperature = float(data["temp_max"].min())
maximum_temperature = float(data["temp_max"].max())
first_date = data["date"].min().date()
last_date = data["date"].max().date()


def reset_filters():
    # A button callback runs before Streamlit redraws the controls.
    st.session_state["weather_type"] = "All"
    st.session_state["temperature_range"] = (minimum_temperature, maximum_temperature)
    st.session_state["date_range"] = (first_date, last_date)

st.session_state.setdefault("weather_type", "All")
st.session_state.setdefault("temperature_range", (minimum_temperature, maximum_temperature))
st.session_state.setdefault("date_range", (first_date, last_date))

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
st.subheader("Choose your filters")
st.caption(
    f"{len(data):,} daily records, from {data['date'].min():%B %d, %Y} "
    f"to {data['date'].max():%B %d, %Y}. "
    f"Weather types: {', '.join(sorted(data['weather'].dropna().unique()))}."
)
st.write("Choose a weather type, temperature range, and date range. All three filters apply together.")

weather_column, temperature_column, date_column = st.columns(3)

with weather_column:
    weather_type = st.selectbox(
        "Weather type",
        options=["All", *sorted(data["weather"].dropna().unique())],
        format_func=str.title,
        key="weather_type",
        help="Choose one weather condition, or All to include every condition.",
    )

with temperature_column:
    temperature_range = st.slider(
        "Daily maximum temperature (°C)",
        min_value=minimum_temperature,
        max_value=maximum_temperature,
        step=0.1,
        format="%.1f",
        key="temperature_range",
        help="Move both handles to select a range for each day's highest temperature.",
    )

with date_column:
    date_range = st.date_input(
        "Date range",
        min_value=first_date,
        max_value=last_date,
        key="date_range",
        help="Select a start date and an end date. Both dates are included.",
    )

st.button("Reset filters", on_click=reset_filters, help="Show all days again.")

# A date range is temporarily incomplete while the user selects its end date.
if len(date_range) != 2:
    st.info("Select both a start date and an end date to view matching days.")
    st.stop()

start_date, end_date = date_range
filtered_data = data[
    data["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    & data["temp_max"].between(*temperature_range)
]
if weather_type != "All":
    filtered_data = filtered_data[filtered_data["weather"] == weather_type]

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
st.subheader("Summary of matching days")
st.write("All weather types" if weather_type == "All" else f"Weather type: {weather_type.title()}")
st.caption(
    f"{start_date:%b %d, %Y} to {end_date:%b %d, %Y} · "
    f"Daily maximum temperature: {temperature_range[0]:.1f}–{temperature_range[1]:.1f} °C. "
    "All results below describe only days matching these filters."
)
count_column, average_temperature_column, precipitation_column = st.columns(3)
count_column.metric("Matching days", f"{len(filtered_data):,}", help=f"Out of {len(data):,} days in the full dataset.")
average_temperature_column.metric(
    "Average daily maximum temperature",
    f"{filtered_data['temp_max'].mean():.1f} °C" if not filtered_data.empty else "—",
    help="The mean of daily high temperatures for matching days, not an all-day average temperature.",
)
precipitation_column.metric(
    "Average daily precipitation",
    f"{filtered_data['precipitation'].mean():.1f} mm" if not filtered_data.empty else "—",
    help="The mean precipitation across matching days, including days with zero precipitation.",
)

if filtered_data.empty:
    st.info("No days match these filters. Widen a range, choose All weather types, or use Reset filters.")
else:
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.subheader("Daily maximum temperature over time")
    st.write(
        "Each point represents one matching day. Hover over a point for its details. "
        "Gaps may contain days excluded by your filters."
    )
    if len(filtered_data) == 1:
        st.caption("Only one day matches. Broaden your filters to compare days over time.")

    # Points keep a filtered-out interval from looking like a continuous trend.
    temperature_chart = (
        alt.Chart(filtered_data)
        .mark_circle(size=45, color="#2F6FA7", opacity=0.75)
        .encode(
            x=alt.X(
                "date:T",
                title="Date",
                axis=alt.Axis(
                    format="%b %d, %Y",
                    tickCount=8,
                    labelOverlap=True,
                    labelAngle=0,
                ),
            ),
            y=alt.Y("temp_max:Q", title="Daily maximum temperature (°C)", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%b %d, %Y"),
                alt.Tooltip("temp_max:Q", title="Daily maximum (°C)", format=".1f"),
                alt.Tooltip("precipitation:Q", title="Precipitation (mm)", format=".1f"),
                alt.Tooltip("weather:N", title="Weather type"),
            ],
        )
        .properties(height=320, background="#FFFFFF")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#5B6B7A",
            titleColor="#263746",
            labelFontSize=13,
            titleFontSize=14,
            titleFontWeight="normal",
            labelPadding=8,
            titlePadding=14,
            domain=False,
            tickColor="#D7E0E8",
            gridColor="#E6EBF0",
            gridWidth=0.7,
        )
        .configure_axisX(grid=False)
    )
    st.altair_chart(temperature_chart, width="stretch", theme=None)

display_data = filtered_data.rename(
    columns={
        "date": "Date",
        "weather": "Weather type",
        "temp_max": "Maximum temperature (°C)",
        "temp_min": "Minimum temperature (°C)",
        "precipitation": "Precipitation (mm)",
        "wind": "Wind speed",
    }
)

with st.expander("View matching records", expanded=False):
    st.dataframe(
        display_data,
        hide_index=True,
        column_config={"Date": st.column_config.DateColumn(format="YYYY-MM-DD")},
    )
st.caption(
    "Source: [Vega Seattle Weather dataset]"
    "(https://vega.github.io/vega-datasets/datapackage.html), "
    "adapted from NOAA records for instructional use. "
    "Weather categories were derived from the original observations."
)
