import streamlit as st
from PIL import Image
import os
import pandas as pd
import altair as alt
import numpy as np
import pydeck as pdk

st.set_page_config(page_title="Crop Yield Impact Through Climate Change and Pesticides", layout="wide")

# read in data
df = pd.read_csv('group_data_new.csv')

# Smaller title using custom HTML and CSS
st.markdown(
    "<h2 style='font-size:2rem; margin-bottom: 1rem;'>Impact of Climate Change and Pesticide Use on Global Crop Yields 🌱</h2>",
    unsafe_allow_html=True,
)

# Set a smaller width for the image (e.g., 400px)
#st.image("crops-growing-in-thailand.jpg", width=600)

# Filters on Sidebar
st.sidebar.header("Filters")  # Move filters to the sidebar

# if st.sidebar.button("🔄 Reset Click Filters"):
#     for key in st.session_state.keys():
#         del st.session_state[key]
#     st.rerun()

# Temperature unit selector
temp_unit = st.sidebar.radio(
    "Temperature Unit",
    options=["Celsius (°C)", "Fahrenheit (°F)"],
    index=0
)

# Ensure 'avg_temp' exists and convert
if "avg_temp" in df.columns:
    if temp_unit == "Fahrenheit (°F)":
        df["avg_temp"] = df["avg_temp"] * 9 / 5 + 32
else:
    st.warning("avg_temp column not found in data.")

# Slider: Filter by Year
df["Year"] = pd.to_datetime(df["Year"], errors='coerce')
min_year = int(df["Year"].dt.year.min())
max_year = int(df["Year"].dt.year.max())
time_range = st.sidebar.slider(
    "Select Years",
    min_year,
    max_year,
    (min_year, max_year)
)

df['Year'] = df['Year'].dt.year

# Selectbox: Filter by Country
country_options = ["All"] + sorted(df["country"].dropna().unique())
country = st.sidebar.selectbox("Filter by Country", options=country_options)

# Selectbox: Select Variable
x_axis_options = ['pesticides_tonnes', 'avg_temp', 'GDP_per_capita_clean', 'food_supply']
# Show temperature with units
x_axis_labels = {
    'pesticides_tonnes': 'Pesticides (tonnes)',
    'avg_temp': f'Avg Temp ({"°F" if temp_unit.startswith("Fahrenheit") else "°C"})',
    'GDP_per_capita_clean': 'GDP per Capita',
    'food_supply': 'Food Supply'
}
x_axis_label_list = [x_axis_labels[key] for key in x_axis_options]
x_axis_choice_label = st.sidebar.selectbox("Select Variable", options=x_axis_label_list)


# Map label back to x_axis_options key
x_axis_choice = [k for k,v in x_axis_labels.items() if v == x_axis_choice_label][0]
x_axis_title = x_axis_labels[x_axis_choice]

# Filter the DataFrame based on selected country and year range
if country == "All":
    filtered_df = df[df["Year"].between(*time_range)]
else:
    filtered_df = df[(df["country"] == country) & (df["Year"].between(*time_range))]

# Only scatter will have selection
country_selection = alt.selection_point(
    fields=['country'],
    empty='all',
    #bind='legend',
    on='click'
)
crop_selection = alt.selection_point(
     fields=['Item'],
     empty='all',
     bind='legend',
     on='click'
 )

# Define a standard width and height for all charts
CHART_WIDTH = 900
CHART_HEIGHT = 400

# Horizontal Bar Chart of Country
bar = alt.Chart(filtered_df).mark_bar(color="#5F4747", height=20).encode(
    x=alt.X('total_yield:Q', title='Yield (hg/ha)'),
    y=alt.Y('country:N', title='Country', sort='-x'),
    opacity=alt.condition(country_selection, alt.value(1), alt.value(0.2)),
).transform_aggregate(
    total_yield='sum(hg/ha_yield)',
    groupby=['country', 'Item']  # Keep crop info for filtering
).transform_filter(
    crop_selection  # Now this works!
).transform_aggregate(
    total_yield='sum(total_yield)',  # Re-aggregate across selected crops
    groupby=['country']
).transform_window(
    rank='rank(total_yield)',
    sort=[alt.SortField('total_yield', order='descending')]
).transform_filter(
    alt.datum.rank <= 10
).add_params(
    country_selection
).properties(
    width=CHART_WIDTH,
    height=alt.Step(30),
    title='Top 10 Countries by Total Yield'
).interactive()

# 1. Scatter plot with legend and selection
scatter = alt.Chart(filtered_df).mark_circle().encode(
    x=alt.X(f'{x_axis_choice}:Q', title=x_axis_title),
    y=alt.Y('hg/ha_yield:Q', title='Yield (hg/ha)'),
    # color=alt.condition(
    #     crop_selection,
    #     alt.Color('Item:N', legend=None),
    #     alt.value('lightgray')),
    color=alt.Color('Item:N', legend=None),
    opacity=alt.condition(crop_selection, alt.value(1), alt.value(0.2)),
    tooltip=['country:N', f'{x_axis_choice}:Q', 'hg/ha_yield:Q', 'Item:N', 'food_supply:Q']
    ).transform_filter(
       country_selection
).add_params(crop_selection).properties(
   # width=CHART_WIDTH/2,
    height=CHART_HEIGHT,
    title='Yield vs. ' + x_axis_title
).interactive()

# 2. Box plot (no selection)
boxplot = alt.Chart(filtered_df).mark_boxplot().encode(
    x=alt.X('Item:N', title='Crop', axis=alt.Axis(labelAngle=-45)),
    y=alt.Y(f'{x_axis_choice}:Q', title=x_axis_title),
    color=alt.Color('Item:N', title='Crop', legend=None),
   # opacity=alt.condition(crop_selection, alt.value(1), alt.value(0.2)),
#   ).transform_filter(
#       country_selection
).properties(
   # width=CHART_WIDTH/2,
    height=CHART_HEIGHT,
    title=f'Box Plot: {x_axis_title} by Crop'
).interactive()

# 3. Line chart (no selection)
line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('sum(hg/ha_yield):Q', title='Total Yield (hg/ha)'),
    color=alt.Color('Item:N', title='Crop', legend=alt.Legend(title='Crop', orient='top', columns=5)),
    opacity=alt.condition(crop_selection, alt.value(1), alt.value(0.2)),
    tooltip=[
        alt.Tooltip('Year:O', title='Year'),
        alt.Tooltip('Item:N', title='Crop'),
        alt.Tooltip('sum(hg/ha_yield):Q', title='Total Yield (hg/ha)')
    ]
).add_params(crop_selection).transform_filter(country_selection).properties(
    height=CHART_HEIGHT,
    title='Crop Yield Over Time'
).interactive()


# #st.altair_chart(bar, use_container_width=True)

# # # Display charts using Streamlit's layout system
# st.altair_chart(bar, use_container_width=True)

# # # Two columns: scatter and boxplot
# col1, col2 = st.columns(2)

# with col1:
#     st.altair_chart(scatter, use_container_width=True)

# with col2:
#      st.altair_chart(boxplot, use_container_width=True)

# # # Line chart at the bottom
# st.altair_chart(line_chart, use_container_width=True)

layout = alt.vconcat(
    bar,
    line_chart,
    scatter
).resolve_scale(
    color='independent'
)

# st.altair_chart(layout, use_container_width=True)
st.altair_chart(layout, use_container_width=True)
