import streamlit as st
import pandas as pd
import plotly.express as px




st.set_page_config(
     page_title="Netflix Content Insights",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

#css

st.markdown("""
<style>

    /* Main page */
    .main {
        padding-top: 2rem;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 30px;
    }

    /* Section titles */
    .section-title {
        font-size: 24px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    /* KPI cards */
    .kpi-card {
        background-color: #f8f9fb;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e5e7eb;
        min-height: 120px;
    }

    .kpi-label {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 700;
    }

    /* Insight boxes */
    .insight-box {
        background-color: #f8f9fb;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 4px solid #777777;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        padding-top: 2rem;
    }

</style>
""", unsafe_allow_html=True)

#Data load
df = pd.read_csv("Netflix_cleaned.csv")


#Header
st.markdown(
    '<div class="main-title"> Netflix Content Insights</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Explore Netflix\'s catalog, content trends, genres, countries, and audience ratings.'
    '</div>',
    unsafe_allow_html=True
)





# FILTERS
st.sidebar.title(" Filters")

st.sidebar.caption(
    "Use the filters below to explore different parts of the Netflix catalog."
)

content_type = st.sidebar.selectbox(
    "Content type",
    ["All"] + sorted(df["type"].unique())
)

ratings = st.sidebar.multiselect(
    "Audience rating",
    sorted(df["rating"].unique()),
    default=[]
)

min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())

year_range = st.sidebar.slider(
    "Release period",
    min_year,
    max_year,
    (min_year, max_year)
)


filtered_df = df.copy()

if content_type != "All":
    filtered_df = filtered_df[
        filtered_df["type"] == content_type
    ]

if ratings:
    filtered_df = filtered_df[
        filtered_df["rating"].isin(ratings)
    ]

filtered_df = filtered_df[
    filtered_df["release_year"].between(
        year_range[0],
        year_range[1]
    )
]

st.info(
    f"**{len(filtered_df):,} titles** match your current selection."
)


#KPI 
content_counts = filtered_df["type"].value_counts()

total_titles = len(filtered_df)
movies = content_counts.get("Movie", 0)
tv_shows = content_counts.get("TV Show", 0)

most_common_rating = (
    filtered_df["rating"].mode()[0]
    if not filtered_df.empty
    else "N/A"
)



col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Titles", total_titles)
col2.metric("Movies", movies)
col3.metric("TV Shows", tv_shows)
col4.metric("Most Common Rating", most_common_rating)


st.divider()

#Dashboards
st.markdown(
    '<div class="section-title">Content Mix</div>',
    unsafe_allow_html=True
)

content_summary = filtered_df["type"].value_counts().reset_index()
content_summary.columns = ["Type", "Count"]

fig_content = px.bar(
    content_summary,
    x="Type",
    y="Count",
    title="Netflix Content Distribution",
    text="Count",
    labels={
        "Type": "Content Type",
        "Count": "Number of Titles"
    }
)

fig_content.update_traces(textposition="outside")


content_by_year = (
    filtered_df.groupby("release_year")
    .size()
    .reset_index(name="Count")
)

fig_year = px.line(
    content_by_year,
    x="release_year",
    y="Count",
    title="Content by Release Year",
    markers=True,
    labels={
        "release_year": "Release Year",
        "Count": "Number of Titles"
    }
)


col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_content, use_container_width=True)

with col2:
    st.plotly_chart(fig_year, use_container_width=True)


st.divider()

st.markdown(
    '<div class="section-title"> Global Content</div>',
    unsafe_allow_html=True
)

countries = (
    filtered_df["country"]
    .str.split(", ")
    .explode()
    .str.strip()
)

country_counts = countries.value_counts()

top_countries = (
    country_counts
    .head(10)
    .reset_index()
)

top_countries.columns = ["Country", "Count"]

fig_country = px.bar(
    top_countries,
    x="Count",
    y="Country",
    orientation="h",
    title="Top 10 Countries by Number of Titles",
    text="Count",
    labels={
        "Count": "Number of Titles",
        "Country": "Country"
    }
)
fig_country.update_traces(textposition="outside")


genres = (
    filtered_df["listed_in"]
    .str.split(", ")
    .explode()
    .str.strip()
)

genre_counts = genres.value_counts()

top_genres = (
    genre_counts
    .head(10)
    .reset_index()
)

top_genres.columns = ["Genre", "Count"]

fig_genre = px.bar(
    top_genres,
    x="Count",
    y="Genre",
    orientation="h",
    title="Top 10 Netflix Genres",
    text="Count",
    labels={
        "Count": "Number of Titles",
        "Genre": "Genre"
    }
)

fig_genre.update_traces(textposition="outside")


col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_country, use_container_width=True)

with col2:
    st.plotly_chart(fig_genre, use_container_width=True)


st.divider()

st.markdown(
    '<div class="section-title"> Audience & Ratings</div>',
    unsafe_allow_html=True
)

rating_data = (
    filtered_df.groupby("type")["rating"]
    .value_counts()
    .reset_index(name="Count")
)

fig_rating = px.bar(
    rating_data,
    x="rating",
    y="Count",
    color="type",
    barmode="group",
    title="Ratings Distribution by Content Type",
    labels={
        "rating": "Rating",
        "Count": "Number of Titles",
        "type": "Content Type"
    }
)

st.plotly_chart(fig_rating, use_container_width=True)

st.divider()

#Key Insights

st.header(" Key Business Insights")

st.markdown(
    """
- **Movies represent the majority of the catalog**, accounting for roughly 70% of the available titles.
- **TV-MA is the most common content rating**, indicating a strong representation of mature-rated content.
- **International Movies, Dramas, and Comedies** are among the most represented content categories.
- The release-year analysis shows substantial growth in the number of titles from the mid-2010s onward, followed by a decline in more recent release years.
- **Movies contain a stronger representation of R-rated titles**, while TV Shows have a greater representation of TV-PG and other TV-specific ratings.
"""
)

st.divider()




st.header("Executive Summary")

st.markdown("""
### Key Findings

**1. Content Mix**  
Movies represent the majority of the Netflix catalog, while TV Shows account for a smaller share of the available titles.

**2. Content Ratings**  
TV-MA is the most common rating in the dataset, showing a strong representation of mature-rated content.

**3. Genre Distribution**  
International Movies, Dramas, and Comedies are among the most represented categories in the catalog.

**4. Content by Release Year**  
The number of titles varies considerably across release years, with a notable increase in titles associated with more recent years before declining in the latest years represented in the dataset.

**5. Content Type and Ratings**  
Movies have a stronger representation of R-rated content, while TV Shows contain a greater share of TV-specific ratings such as TV-PG and TV-Y7.

### Business Considerations

- Netflix could monitor whether its current content mix aligns with audience demand.
- Highly represented genres can be analyzed further alongside viewing data to determine whether catalog size corresponds to audience engagement.
- Less represented genres could be investigated as potential opportunities for audience expansion.
- Rating distributions can help support content segmentation and audience-targeting decisions.
""")

# KEY INSIGHTS

st.markdown(
    '<div class="section-title"> Key Insights</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="insight-box">
        <strong>Content Mix</strong><br>
        Movies represent the majority of the Netflix catalog, while TV Shows
        account for a smaller share of available titles.
    </div>

    <div class="insight-box">
        <strong>Audience Ratings</strong><br>
        TV-MA is the most common rating in the dataset, showing a strong
        representation of mature-rated content.
    </div>

    <div class="insight-box">
        <strong>Genre Distribution</strong><br>
        International Movies, Dramas, and Comedies are among the most
        represented categories in the catalog.
    </div>

    <div class="insight-box">
        <strong>Content Trends</strong><br>
        The number of titles associated with release years increased substantially during the late 2010s,
          followed by a decline in the latest years represented in the dataset.
    </div>

    <div class="insight-box">
        <strong>Content Type & Ratings</strong><br>
        Movies show a stronger representation of R-rated content, while
        TV Shows contain a greater representation of TV-specific ratings.
    </div>
    """,
    unsafe_allow_html=True
)

# FILTERED DATA

with st.expander("Explore filtered data"):

    st.write(
        f"{len(filtered_df):,} titles currently match your filters."
    )

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
st.divider()

st.caption(
    "Netflix Content Insights • Data Analysis Project • "
    "Python · Pandas · Plotly · Streamlit"
)