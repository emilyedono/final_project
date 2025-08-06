import streamlit as st
from PIL import Image
import os
import pandas as pd
import altair as alt
import numpy as np
import pydeck as pdk

st.set_page_config(page_title="Crop Yield Impact Through Climate Change and Pesticides", layout="wide")

# read in data
df = pd.read_csv('new_data.csv')
df.rename(columns={"Area": "Country"}, inplace=True)
df2 = pd.read_csv("group_data_new.csv")

# Smaller title using custom HTML and CSS
st.markdown(
    "<h2 style='font-size:2rem; margin-bottom: 1rem;'>🌱 Crops & Countries - A 'Plant Your Own Seeds' Dashboard 🌱</h2>",
    unsafe_allow_html=True,
)

# Set a smaller width for the image (e.g., 400px)
#st.image("crops-growing-in-thailand.jpg", width=600)

# Filters on Sidebar
st.sidebar.header("Use These Filters to Plant Your Dashboard's Seeds!")  # Move filters to the sidebar

# if st.sidebar.button("🔄 Reset Click Filters"):
#     for key in st.session_state.keys():
#         del st.session_state[key]
#     st.rerun()

# Clean merge keys in both DataFrames
df['Country'] = df['Country'].str.strip().str.upper()
df2['Area'] = df2['Area'].str.strip().str.upper()

df['Item'] = df['Item'].str.strip()
df2['Item'] = df2['Item'].str.strip()

df['Year'] = df['Year'].astype(int)
df2['Year'] = pd.to_datetime(df2['Year'], errors='coerce').dt.year


# Slider: Filter by Year
df['Year'] = df['Year'].astype(int)  # Just to be sure
min_year = df['Year'].min()
max_year = df['Year'].max()
time_range = st.sidebar.slider(
    "Select Years",
    min_year,
    max_year,
    (min_year, max_year)
)


df = df[['Country', 'Year', 'Item', 'Country Climate']]
df = pd.merge(df2, df, right_on=['Country', 'Year', 'Item'], left_on=['Area', 'Year', 'Item'], how='left')
# Selectbox: Filter by Country
country_options = ["All"] + sorted(df["Country"].dropna().unique())
country = st.sidebar.selectbox("Filter by Country", options=country_options)

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
# Selectbox: Select Variable
x_axis_options = ['pesticides_tonnes', 'avg_temp', 'GDP_per_capita_clean', 'food_supply']
# Show temperature with units
x_axis_labels = {
    'pesticides_tonnes': 'Pesticides (tonnes)',
    'avg_temp': f'Avg Temp ({"°F" if temp_unit.startswith("Fahrenheit") else "°C"})',
    'GDP_per_capita_clean': 'GDP per Capita',
    'food_supply': 'Food Supply (KCal per person per day)'
}
x_axis_label_list = [x_axis_labels[key] for key in x_axis_options]
x_axis_choice_label = st.sidebar.selectbox("Explore Climate Related Indicators", options=x_axis_label_list)


# Map label back to x_axis_options key
x_axis_choice = [k for k,v in x_axis_labels.items() if v == x_axis_choice_label][0]
x_axis_title = x_axis_labels[x_axis_choice]

# Filter the DataFrame based on selected country and year range
if country == "All":
    filtered_df = df[df["Year"].between(*time_range)]
else:
    filtered_df = df[(df["Country"] == country) & (df["Year"].between(*time_range))]

st.write(f":point_left: See this cool toolbar? Start here to select your desired filters, or 'seeds'! {crop_selection_drop}")


# Dropdown for crop selection
crops_drop = [
    "None Selected",
    "Maize",
    "Potatoes",
    "Rice, paddy",
    "Sorghum",
    "Soybeans",
    "Wheat",
    "Cassava",
    "Sweet potatoes",
    "Plantains and others",
    "Yams"
]

crop_selection_drop = st.selectbox("Curious about a crop? Use this dropdown to learn more!", crops_drop)

if crop_selection_drop == "Maize":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Maize.jpg", width=600)
    st.write("Maize, a member of the grains and grasses category, thrives in both tropical and temperate climates. It is well-suited to regions with low rainfall, typically ranging from 1 to 25 mm per week, and requires moderate light exposure of about 6 to 8 hours daily. The optimal temperature for maize growth is around 22.5°C, which supports healthy development and yield. Maize is a versatile crop with a wide range of uses, including human food, animal feed, and industrial applications, making it a crucial component in global agriculture and food systems.")
elif crop_selection_drop == "Potatoes":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Potatoes.jpg", width=600)
    st.write("Potatoes are temperate-climate tuber crops that grow best under moderate environmental conditions. They require a weekly rainfall of about 25 to 50 mm and benefit from moderate light exposure of 6 to 8 hours per day. The optimal temperature for potato growth is around 17.5°C, which promotes healthy tuber development. Classified as a root crop, potatoes are primarily used for human food and also have significant industrial applications, making them a vital staple in many regions around the world.")
elif crop_selection_drop == "Rice, paddy":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Rice.jpg", width=600)
    st.write("Rice is a staple crop widely grown in tropical regions, where it thrives under high rainfall conditions of 50 to 100 mm per week. It requires moderate sunlight, typically 6 to 8 hours per day, and grows optimally at a temperature of 27.5°C. As a member of the grains and grasses category, rice plays a crucial role in global food security. Its primary use is for human consumption, serving as a dietary cornerstone for billions of people around the world.")
elif crop_selection_drop == "Sorghum":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Sorghum.jpg", width=600)
    st.write("Sorghum is a resilient crop that thrives in tropical and desert climates, making it well-suited for regions with challenging growing conditions. It requires high rainfall levels, typically between 50 to 100 mm per week, and moderate sunlight exposure of 6 to 8 hours daily. The optimal temperature for sorghum growth is around 28.5°C. Belonging to the grains and grasses category, sorghum serves multiple purposes—ranging from human food and animal feed to various industrial uses. Its adaptability and versatility make it a valuable crop in both subsistence and commercial agriculture.")
elif crop_selection_drop == "Soybeans":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Soybeans.jpg", width=600)
    st.write("Soybeans are a versatile legume crop well-suited to temperate climates, where they grow effectively under low rainfall conditions ranging from 1 to 25 mm per week. They require moderate light exposure of 6 to 8 hours per day and perform best at an optimal temperature of 25°C. As members of the legume family, soybeans are rich in protein and serve a wide range of purposes. Their uses include human food products such as tofu and soy milk, animal feed, and various industrial applications, making them a crucial component of both agriculture and the global economy.")
elif crop_selection_drop == "Wheat":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Wheat.jpg", width=600)
    st.write("Wheat is a major crop that thrives in temperate and Mediterranean climates, where it benefits from high rainfall levels ranging from 50 to 100 mm per week. It requires moderate sunlight, about 6 to 8 hours daily, and grows best at an optimal temperature of 20°C. Classified under the grains and grasses category, wheat is one of the most widely cultivated and consumed crops globally. Its primary uses include human food—such as bread, pasta, and flour—animal feed, and a variety of industrial applications, making it a foundational element in global food systems and economies.")
elif crop_selection_drop == "Cassava":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Cassava.jpg", width=600)
    st.write("Cassava is a robust tuber crop ideally suited to tropical climates, where it flourishes under high rainfall conditions of 50 to 100 mm per week. Unlike many other crops, cassava requires high light exposure, typically 10 to 12 hours of sunlight daily, and grows optimally at a temperature of 27°C. Classified among tubers and root crops, cassava is a vital source of carbohydrates and plays a key role in food security for millions of people in tropical regions. Its uses extend beyond human food to include animal feed and industrial applications, highlighting its versatility and economic importance in agriculture.")
elif crop_selection_drop == "Sweet potatoes":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("SweetPotato.jpg", width=600)
    st.write("Sweet potatoes are nutrient-rich tuber crops that grow well in both tropical and temperate climates. They thrive under moderate rainfall conditions, typically receiving 25 to 50 mm of water per week, and require moderate sunlight exposure of 6 to 8 hours daily. The optimal temperature for sweet potato cultivation is around 23.5°C, which supports healthy root development. As members of the tubers and root crops category, sweet potatoes are primarily used for human consumption, valued for their high nutritional content and versatility in a wide range of traditional and modern dishes.")
elif crop_selection_drop == "Plantains and others":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Plantain.jpg", width=600)
    st.write("Plantains are starchy fruits that thrive in tropical climates, where they grow best under moderate rainfall levels of 25 to 50 mm per week. They require moderate sunlight, around 6 to 8 hours daily, and perform optimally at a temperature of 27.5°C. As a key crop in many tropical regions, plantains are classified as starchy fruits and are primarily used for human food. They serve as a staple in many diets, offering a rich source of carbohydrates and playing an important role in food security and culinary traditions around the world.")
elif crop_selection_drop == "Yams":
    st.write(f"You selected: {crop_selection_drop}")
    st.image("Yam.jpg", width=600)
    st.write("Yams are tropical tuber crops primarily cultivated for human consumption. They thrive in warm climates with consistent temperatures around 27.5°C and require high rainfall ranging from 50 to 100 mm per week. Optimal growth occurs with moderate sunlight exposure of about 6 to 8 hours daily. As root crops, yams are a vital food source in many regions, valued for their nutritional content and versatility in cooking.")
elif crop_selection_drop == "None Selected":
    st.image("crops-growing-in-thailand.jpg", width=600)
    

# Only scatter will have selection
country_selection = alt.selection_point(
    fields=['Country'],
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
    y=alt.Y('Country:N', title='Country', sort='-x'),
    opacity=alt.condition(country_selection, alt.value(1), alt.value(0.2)),
).transform_aggregate(
    total_yield='sum(hg/ha_yield)',
    groupby=['Country', 'Item']  # Keep crop info for filtering
).transform_filter(
    crop_selection  # Now this works!
).transform_aggregate(
    total_yield='sum(total_yield)',  # Re-aggregate across selected crops
    groupby=['Country']
).transform_window(
    rank='rank(total_yield)',
    sort=[alt.SortField('total_yield', order='descending')]
).transform_filter(
    alt.datum.rank <= 10
).add_params(
    country_selection
).properties(
    width=CHART_WIDTH//2 - 10,
    height=250,
    title='Top 10 Countries by Total Crop Yield (Sum)'
)

bar2 = alt.Chart(filtered_df).mark_bar(color="#5F4747", height=20).encode(
    x=alt.X(f'mean_choice:Q', title=x_axis_title),
    y=alt.Y('Country:N', title='Country', sort='-x'),
    opacity=alt.condition(country_selection, alt.value(1), alt.value(0.2)),
).transform_aggregate(
    mean_choice=f'mean({x_axis_choice})',
    groupby=['Country']  # Keep crop info for filtering
).transform_window(
    rank='rank(mean_choice)',
    sort=[alt.SortField('mean_choice', order='descending')]
).transform_filter(
    alt.datum.rank <= 10
).add_params(
    country_selection
).properties(
    width=CHART_WIDTH//2 - 10,
    height=250,
    title=f'Top 10 Countries by Average Yearly {x_axis_title}'
)

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
    tooltip=['Country:N', f'{x_axis_choice}:Q', 'hg/ha_yield:Q', 'Item:N', 'food_supply:Q']
    ).transform_filter(
       country_selection
).add_params(crop_selection).properties(
   # width=CHART_WIDTH/2,
    height=CHART_HEIGHT,
    title='Yield vs. ' + x_axis_title
)

scatter2 = alt.Chart(filtered_df).mark_circle().encode(
    x=alt.X(f'{x_axis_choice}:Q', title=x_axis_title),
    y=alt.Y('total_yield:Q', title='Total Yield (hg/ha)'),
    # color=alt.condition(
    #     crop_selection,
    #     alt.Color('Item:N', legend=None),
    #     alt.value('lightgray')),
    color=alt.Color('Country Climate:N', legend=None),
    opacity=alt.condition(crop_selection, alt.value(1), alt.value(0.2)),
    tooltip=['Country:N', 'Year:N', f'{x_axis_choice}:Q', 'total_yield:Q', 'Country Climate:N']
    ).transform_aggregate(
        total_yield='sum(hg/ha_yield)',
        groupby=['Country', 'Year', 'Country Climate']
     ).transform_filter(
        country_selection
).transform_aggregate(
        total_yield='sum(hg/ha_yield)',
        groupby=['Year', 'Country Climate']
).properties(
   # width=CHART_WIDTH/2,
    height=CHART_HEIGHT,
    title='Total Yield (All Crops) vs. ' + x_axis_title
)

agg_df = filtered_df.groupby(['Country', 'Year', 'Country Climate']).agg(
    total_yield=('hg/ha_yield', 'sum'),
    mean_x_axis=(x_axis_choice, 'mean')
).reset_index()

scatter3 = alt.Chart(agg_df).mark_circle().encode(
    x=alt.X('mean_x_axis:Q', title=x_axis_title),
    y=alt.Y('total_yield:Q', title='Total Yield (hg/ha)'),
    color=alt.Color('Country Climate:N', legend=alt.Legend(title='Country Climate', orient='right')),
    tooltip=['Country', 'Year', 'Country Climate', 'total_yield', 'mean_x_axis']
).transform_filter(
    country_selection
    ).properties(
    height=CHART_HEIGHT,
    title='Total Yield (All Crops) vs. ' + x_axis_title
)


# 2. Box plot (no selection)
boxplot = alt.Chart(filtered_df).mark_boxplot().encode(
    x=alt.X('Item:N', title='Crop', axis=alt.Axis(labelAngle=-45)),
    y=alt.Y(f'{x_axis_choice}:Q', title=x_axis_title),
    color=alt.Color('Item:N', title='Crop', legend=None),
    opacity=alt.condition(crop_selection, alt.value(1), alt.value(0.2)),
    tooltip=[
        alt.Tooltip('Item:N', title='Crop'),
        alt.Tooltip('Year:O', title='Year'),
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip(f'{x_axis_choice}:Q', title=f'{x_axis_title}')
    ]
).transform_filter(country_selection).properties(
    height=CHART_HEIGHT,
    title=f'Distribution of {x_axis_title} by Crop'
)

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
)


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
    line_chart,
    alt.hconcat(bar, bar2),
    scatter3
).resolve_scale(
    color='independent'
)

layout = layout.configure_view(stroke=None).configure_concat(spacing=15)
layout = layout.configure_concat(spacing=15)

layout = layout.properties(
    autosize=alt.AutoSizeParams(
        type='pad',
        contains='padding',
        resize=True
    )
)

# st.altair_chart(layout, use_container_width=True)
st.altair_chart(layout, use_container_width=True)

