"""
Script to make the interactive dashboard for this project.
"""
import os

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

try:
    # When running as a package (e.g., during testing)
    from .data_prep import process_healthcare_data
except ImportError:
    # When running as a top-level script (e.g., via streamlit)
    from data_prep import process_healthcare_data

# pylint: disable=C0103
# we have included the above pylint error disable because pylint was incorrectly
# interpreting streamlit filter selection variables as constants, and flagging them
# for not following the uppercase naming convention
@st.cache_data
def load_data():
    """
    loads in the original data from our data folder,
    processes them into 3 dataframes using our data_prep.py module
    and returns them to be used to generate dashboard figures
    """
    #file_path = "../data/"
    file_path = os.path.join(os.getcwd(), "data/")
    df_WHO, df_IHME, df_met = process_healthcare_data(file_path)

    df_IHME.columns = df_IHME.columns.str.strip().str.replace('"', '')
    ihme_mapping = {
        "location": "location",
        "sex": "sex",
        "cause": "cause",
        "year": "year",
        "Deaths": "deaths",
        "Incidence": "incidence"
    }
    df_IHME = df_IHME.rename(columns=ihme_mapping)

    # Check that all expected IHME columns are present:
    expected_IHME = set(ihme_mapping.values())
    if not expected_IHME.issubset(set(df_IHME.columns)):
        raise ValueError(
            f"final_IHME.csv is missing columns: {expected_IHME - set(df_IHME.columns)}")

    # Load final WHO data
    # df_WHO = pd.read_csv("../data_prep/final_data/final_who.csv")
    df_WHO.columns = df_WHO.columns.str.strip().str.replace('"', '')
    df_WHO = df_WHO.loc[:, ~df_WHO.columns.str.contains("^Unnamed")]
    who_mapping = {
        "Location": "location",
        "Period": "year",
        "Medical Doctors per 10,000": "medical_doctors_per_10000",
        "Nurses and Midwifes per 10,000": "nurses_midwifes_per_10000",
        "Pharmacists per 10,000": "pharmacists_per_10000",
        "Dentists per 10,000": "dentists_per_10000"
    }
    df_WHO = df_WHO.rename(columns=who_mapping)
    expected_WHO = set(who_mapping.values())
    if not expected_WHO.issubset(set(df_WHO.columns)):
        raise ValueError(
            f"final_who.csv is missing columns: {expected_WHO - set(df_WHO.columns)}")

    # Load inner merged data
    # df_met = pd.read_csv("../data_prep/final_data/inner_merged_data.csv")
    df_met.columns = df_met.columns.str.strip().str.replace('"', '')
    df_met = df_met.loc[:, ~
                                df_met.columns.str.contains("^Unnamed")]
    # The inner merged file should have the same workforce columns.
    # It may use either "Period" or "year" for the time column.
    # We want to standardize on "year".
    if "Period" in df_met.columns and "year" not in df_met.columns:
        df_met = df_met.rename(columns={"Period": "year"})
    # In case it already uses "year", we leave it.
    # Now, rename the workforce columns (assuming they match the WHO file):
    metrics_mapping = {
        "Location": "location",
        "medical doctors per 10,000": "medical_doctors_per_10000",
        "nurses and midwifes per 10,000": "nurses_midwifes_per_10000",
        "pharmacists per 10,000": "pharmacists_per_10000",
        "dentists per 10,000": "dentists_per_10000"
    }
    df_met = df_met.rename(columns=metrics_mapping)
    # Ensure the time column is named "year"
    if "year" not in df_met.columns:
        raise ValueError(
            "inner_merged_data.csv must contain a time column named either 'year' or 'Period'.")
    expected_metrics = {"location", "year", "medical_doctors_per_10000",
                        "nurses_midwifes_per_10000", "pharmacists_per_10000", "dentists_per_10000"}
    if not expected_metrics.issubset(set(df_met.columns)):
        raise ValueError(
            f"inner_merged_data.csv missing columns: {expected_metrics - set(df_met.columns)}")
            # removed "is" from above value error message for line length
            # if this affects test passing, replace and split the above line into 2 lines
    return df_IHME, df_WHO, df_met

def plot_compscore_over_time(df, primary_metric="composite_score", selected_location=None):
    """
    Generates a line plot of the composite score over time for the chosen countries
    """
    if selected_location:
        df = df[df["location"].isin(selected_location)]
    fig = go.Figure()
    for loc in df["location"].unique():
        #df_loc = df[df["location"] == loc]
            #.dropna(subset=[primary_metric])
        fig.add_trace(go.Scatter(
            x=df[df['location']==loc]["year"],
            y=df[df['location']==loc][primary_metric],
            mode="lines+markers",
            name=f"{primary_metric.replace('_', ' ').capitalize()} - {loc}"
        ))
    fig.update_layout(
        title=f"{primary_metric.replace('_', ' ').capitalize()} Over Time",
        xaxis_title="Year",
        yaxis_title=primary_metric.replace("_", " ").capitalize(),
        template="plotly_white"
    )
    return fig

def plot_death_vs_docs(df, primary_metric = "deaths",
    secondary_metric = "medical_doctors_per_10000", selected_location = None):
    """
    Generates scatter plot of the number of deaths vs the rate of medical doctors in the
    specified countries, with each point representing a different year
    """
    if selected_location:
        df = df[df["location"].isin(selected_location)]
    fig = px.scatter(
        df,
        x=secondary_metric,
        y=primary_metric,
        color="location",                         # Encode country with color
        hover_data=["year", "location"],          # Show year and country on hover
        title=f"{primary_metric} vs {secondary_metric} by Country (Each Point = Year)",
    )
    fig.update_traces(marker={"size": 10})      # Adjust dot size if needed
    fig.update_layout(template="plotly_white")   # Use a clean layout
    return fig

def plot_ihme_data(df, metric="deaths", select_yr_and_sex=tuple([None], [None]),
    selected_location=None, selected_cause=None):
    """
    Generates a bar plot of the chosen disease metric for the chosen injury causes
    for the selected year and countries
    """
    select_yr = select_yr_and_sex[0].item()
    selected_sex = select_yr_and_sex[1].item()
    # The IHME data now uses 'deaths' and 'incidence'
    if metric not in ["deaths", "incidence"]:
        raise ValueError("Metric must be 'deaths' or 'incidence'")

    required_columns = {"location", "cause", "year", metric}
    if not required_columns.issubset(set(df.columns)):
        missing_cols = required_columns - set(df.columns)
        raise ValueError(
            f"Missing required columns in IHME data: {missing_cols}")

    if select_yr is None:
        select_yr = df["year"].max()
    df_year = df[df["year"] == select_yr].dropna(
        subset=["location", "cause", metric])

    if selected_location:
        df_year = df_year[df_year["location"].isin(selected_location)]
    if selected_cause:
        df_year = df_year[df_year["cause"].isin(selected_cause)]
    if selected_sex:
        df_year = df_year[df_year["sex"].isin(selected_sex)]

    fig = px.bar(
        df_year,
        x="cause",
        y=metric,
        color="location",
        barmode="group",
        title=f"{metric.capitalize()} by Cause in {select_yr}"
    )
    fig.update_layout(xaxis_title="Cause",
                      yaxis_title=metric.capitalize(), template="plotly_white")
    return fig

def plot_who_data(df, select_year=None, selected_location=None, selected_regions=None):
    """
    Generates a bar plot of all 4 workforce metrics from the WHO dataset for the locations
    specified in the year specified
    """
    if select_year is None:
        select_year = df["year"].max()
    df_year = df[df["year"] == select_year]
    if selected_regions and len(selected_regions)>0:
        df_year = df_year[df_year["Region"].isin(selected_regions)]
    if selected_location and len(selected_location)>0:
        df_year = df_year[df_year["location"].isin(selected_location)]

    if df_year.empty:
        st.write("No data available for the selected year,"
            + " region(s), and countries combination, try another combination.")

    categories = [
        ("medical_doctors_per_10000", "Medical Doctors per 10000"),
        ("nurses_midwifes_per_10000", "Nurses & Midwifes per 10000"),
        ("pharmacists_per_10000", "Pharmacists per 10000"),
        ("dentists_per_10000", "Dentists per 10000")
    ]

    fig = go.Figure()
    for col, label in categories:
        if col in df_year.columns:
            fig.add_trace(go.Bar(
                x=df_year["location"],
                y=df_year[col],
                name=label
            ))
    fig.update_layout(
        title=f"Workforce Metrics by Country in {select_year}",
        xaxis_title="Location",
        yaxis_title="Per 10000 Population",
        template="plotly_white",
        barmode="group"
    )
    return fig

def plot_metrics_by_country(df, primary_metric="medical_doctors_per_10000",
    secondary_metric="nurses_midwifes_per_10000",
    selected_yr=None,
    selected_place=(None,None)):
    """
    Generates a bar plot of the primary metric with a line plot of the second metric
    overlayed for the selected year and location(s)
    """
    selected_location = selected_place[0]
    selected_region = selected_place[1]
    if selected_yr is None:
        selected_yr = df["year"].max()
    df_year = df[df["year"] == selected_yr].dropna(
        subset=["location", primary_metric, secondary_metric])
    if selected_region and len(selected_region)>0:
        df_year = df_year[df_year["region"].isin(selected_region)]
    if selected_location:
        df_year = df_year[df_year["location"].isin(selected_location)]
    if df_year.empty:
        st.write("No data available for the selected year and location, try another combination.")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_year["location"],
        y=df_year[primary_metric],
        name=primary_metric.replace("_", " ").capitalize(),
        marker_color="red"
    ))
    fig.add_trace(go.Scatter(
        x=df_year["location"],
        y=df_year[secondary_metric],
        name=secondary_metric.replace("_", " ").capitalize(),
        mode="lines+markers",
        line={"color": 'blue', "dash": 'dash'}
    ))
    fig.update_layout(
        title=f"{primary_metric.replace('_', ' ').capitalize()} & "
            + f"{secondary_metric.replace('_', ' ').capitalize()} by Location in {selected_year}",
        xaxis_title="Location",
        yaxis_title=primary_metric.replace("_", " ").capitalize(),
        template="plotly_white"
    )
    return fig

def plot_metrics_over_time(df, primary_metric="medical_doctors_per_10000",
    secondary_metric="nurses_midwifes_per_10000", selected_location=None):
    """
    Generates a line plot of the 2 selected metrics over all years for the selected location(s)
    """
    if selected_location:
        df = df[df["location"].isin(selected_location)]

    fig = go.Figure()
    for loc in df["location"].unique():
        df_loc = df[df["location"] == loc].dropna(
            subset=["year", primary_metric, secondary_metric])
        fig.add_trace(go.Scatter(
            x=df_loc["year"],
            y=df_loc[primary_metric],
            mode="lines+markers",
            name=f"{primary_metric.replace('_', ' ').capitalize()} - {loc}"
        ))
        fig.add_trace(go.Scatter(
            x=df_loc["year"],
            y=df_loc[secondary_metric],
            mode="lines+markers",
            name=f"{secondary_metric.replace('_', ' ').capitalize()} - {loc}",
            line={"dash": 'dash'}
        ))
    fig.update_layout(
        title=f"{primary_metric.replace('_', ' ').capitalize()} & "
            + f"{secondary_metric.replace('_', ' ').capitalize()} Over Time",
        xaxis_title="Year",
        yaxis_title=primary_metric.replace("_", " ").capitalize(),
        template="plotly_white"
    )
    return fig

def country_spider(df, ctry, year):
    """
    Generates spider plot of healthcare workforce metrics for the specified country
    in the specified year
    """
    # Create a spider plot for the country
    # Get the row for the country
    country_row = df[(df['location'] == ctry) & (df['year'] == year)]
    # Get the metrics
    thetas = ['medical_doctors_per_10000', 'nurses_midwifes_per_10000',
     'pharmacists_per_10000', 'dentists_per_10000']
    rads = country_row[thetas].values.flatten()
    fig_spider = px.line_polar(r=rads, theta=thetas, line_close=True)
    fig_spider.update_layout(title=f"{ctry} Workforce Metrics in {year}")
    fig_spider.update_traces(fill='toself')
    # below line not working for some reason
    fig_spider.update_layout(legend={"font": {"color": 'black'}})
    return fig_spider


# dahsboard layout
st.set_page_config(page_title="Global Healthcare", layout="wide")
st.title("Global Healthcare")

# Load data.
df_ihme, df_who, df_metrics = load_data()


# (Optional) Debug: Uncomment these lines to inspect standardized column names.
# st.write("IHME Data Columns:", df_ihme.columns.tolist())
# st.write("WHO Data Columns:", df_who.columns.tolist())
# st.write("Metrics Data Columns:", df_metrics.columns.tolist())

# Create tabs.
tabs = st.tabs(
    ["Home", "IHME Data", "WHO Data", "Data by Country", "Data Over Time", "Country Overview"])

# --- Home Page ---
with tabs[0]:
    st.header("Ranking and Scores")
    st.write("Welcome! This site provides an interactive overview of healthcare workforce and"
        + " outcome metrics for various countries. On each tab, you can filter to see the "
        + "desired data. Enjoy!")
    # Section 1
    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("Top 5 Healthcare Systems by Year")
        # Dropdown to select the year
        years = sorted(df_metrics["year"].unique())
        selected_year = st.selectbox("Select Year", years, key="home_year")

    with col2:
        # Drop down and ranking list
        top_countries = df_metrics[df_metrics["year"] == selected_year].nsmallest(5, "rank")
        st.subheader(f"Top 5 Countries in {selected_year}:")
        for i, row in top_countries.iterrows():
            st.write(f"**{row['rank']} {row['location']}**")
        st.markdown("---")

    # Section 2
    st.subheader("Composite Score or Ranking Over Time by Country")
    metric_choice = st.selectbox("Select Metric", options=[
                                     "composite_score", "rank"], key="home_metric")
    available_locations = sorted(df_metrics["location"].dropna().unique())
    location_choice = st.multiselect("Select Location(s)", options=available_locations,
                        default="United States of America", key="home_loc")
    fig_scores_ranks = plot_compscore_over_time(df_metrics, primary_metric = metric_choice,
                        selected_location = location_choice)
    st.plotly_chart(fig_scores_ranks, use_container_width=True)
    st.markdown("---")
    # Section 3
    country_list = sorted(df_metrics["location"].dropna().unique())
    country_selection = st.multiselect("Select Location(s)", options=country_list,
                        default="United States of America", key="country1")
    fig_death_vs_docs = plot_death_vs_docs(df_metrics, selected_location = country_selection)
    st.plotly_chart(fig_death_vs_docs, use_container_width=True)
    # Section 4
    st.write("DISCLAIMER: the fields used to generate these rankings are limited, therefore our "
        + "rankings are not to be taken as definitive.")

# -------- IHME Data Tab --------
with tabs[1]:
    st.header("Death or Incidence Rates by Cause")
    col1, col2, col3, col4, col5 = st.columns(5)
    year_choice = None
    with col1:
        measure_choice = st.selectbox("Select Measure", options=[
                                     "deaths", "incidence"], key="ihme_measure")
    with col2:
        years = sorted(df_ihme["year"].unique())
        year_choice = st.selectbox(
            "Select Year", options=years, index=len(years)-1, key="ihme_year")
    with col3:
        locations = sorted(df_ihme[df_ihme["year"]==(year_choice)]["location"].unique())
        default = ["United States of America", "India", "China"]
        location_choice = st.multiselect(
            "Select Location(s)", options=locations, default=default, key="ihme_loc")
    with col4:
        causes = sorted(df_ihme["cause"].unique())
        default = ["Cardiovascular diseases", "Digestive diseases"]
        cause_choice = st.multiselect(
            "Select Cause(s)", options=causes, default=default, key="ihm_cause")
    with col5:
        sexes = sorted(df_ihme["sex"].unique())
        sex_choice = st.multiselect(
            "Select Sex Group(s)", options=sexes, default="Both", key="ihm_sex")

    fig_ihme = plot_ihme_data(df_ihme, metric=measure_choice,
                select_yr_and_sex=tuple(year_choice, sex_choice),
                selected_location=location_choice, selected_cause=cause_choice)
    st.plotly_chart(fig_ihme, use_container_width=True)

# -------- WHO Data Tab --------
with tabs[2]:
    st.header("Medical Workforce by Country")
    col1, col2, col3 = st.columns(3)
    year_choice = None
    region_choice = None
    with col1:
        years_who = sorted(df_who["year"].unique())
        year_choice = st.selectbox(
            "Select Year", options=years_who, index=len(years_who)-1, key="who_year")
    with col2:
        regions = sorted(df_who["Region"].unique())
        region_choice = st.multiselect("Select Region", options=regions, key="who_region")
    with col3:
        hold = df_who[(df_who["year"]==(year_choice))&(df_who["Region"].isin(region_choice))]
        countries_who = sorted(hold["location"].unique())
        default = countries_who[:3]
        country_choice = st.multiselect(
            "Select Location(s)", options=countries_who, default=default, key="who_loc")
    fig_who = plot_who_data(df_who, select_year=year_choice,
        selected_location=country_choice, selected_regions = region_choice)
    st.plotly_chart(fig_who, use_container_width=True)

# -------- Data by Country Tab --------
with tabs[3]:
    st.header("Data by Country")
    col1, col2, col3, col4, col5 = st.columns(5)
    workforce_metrics = [
        "medical_doctors_per_10000",
        "nurses_midwifes_per_10000",
        "pharmacists_per_10000",
        "dentists_per_10000"
    ]
    year_choice = None
    region_choice = None
    with col1:
        primary_metric_choice = st.selectbox(
            "Primary Metric", options=workforce_metrics, index=0, key="country_met_one")
    with col2:
        secondary_metric_choice = st.selectbox(
            "Secondary Metric", options=workforce_metrics, index=1, key="country_met_two")
    with col3:
        years_metrics = sorted(df_metrics["year"].unique())
        year_choice = st.selectbox(
            "Select Year", options=years_metrics, index=len(years_metrics)-1, key="country_year")
    with col4:
        regions = sorted(df_metrics["region"].unique())
        region_choice = st.multiselect("Select Region", options=regions, key="country_region")
    with col5:
        holder = df_metrics[(
            df_metrics["year"]==(year_choice))&(df_metrics["region"].isin(region_choice))]
        countries = sorted(holder["location"].unique())
        end = min(10, len(countries)-1)
        default = countries[:end]
        countries_choice = st.multiselect(
            "Select Location(s)", options=countries, default=default, key="country_loc")
    fig_country = plot_metrics_by_country(
        df_metrics,
        primary_metric=primary_metric_choice,
        secondary_metric=secondary_metric_choice,
        selected_yr=year_choice,
        selected_place=(countries_choice, region_choice)
    )
    st.plotly_chart(fig_country, use_container_width=True)

# -------- Data Over Time Tab --------
with tabs[4]:
    st.header("Metrics Over Time")
    col1, col2, col3, col4 = st.columns(4)
    region_choice = None
    with col1:
        primary_metric_time = st.selectbox(
            "Primary Metric", options=workforce_metrics, index=0, key="over_time_primary")
    with col2:
        secondary_metric_time = st.selectbox(
            "Secondary Metric", options=workforce_metrics, index=1, key="over_time_secondary")
    with col3:
        regions = sorted(df_metrics["region"].unique())
        region_choice = st.multiselect("Select Region",
            options=regions, default = "Africa", key="over_time_region")
    with col4:
        available_locations = sorted(
            df_metrics[df_metrics['region'].isin(region_choice)]["location"].dropna().unique())
        location_time_choice = st.multiselect(
            "Select Location(s)", options=available_locations, 
            default=available_locations[:3], key="over_time_loc")
    fig_time = plot_metrics_over_time(
        df_metrics,
        primary_metric=primary_metric_time,
        secondary_metric=secondary_metric_time,
        selected_location=location_time_choice
    )
    st.plotly_chart(fig_time, use_container_width=True)

# --- Country Overview ---
with tabs[5]:
    st.header("Country Overview")
    countries = sorted(df_metrics["location"].dropna().unique())
    country = st.selectbox("Select Country", options=countries, key="country_country")

    #col1 = st.columns(1)
    #with col1:
    years = sorted(df_who[df_who["location"]==country]["year"].unique())
    year_choice = st.selectbox("Select Year", options=years, key="spider_year")
    hldr = df_metrics[(df_metrics['location']==country)&(df_metrics['year']==year_choice)]
    st.subheader(f"{country} had a composite score of "
        + f"{hldr['composite_score'].values[0]} in {year_choice}")
    st.subheader(f"{country} was ranked "
        + f"{hldr['rank'].values[0]} in {year_choice}")

    fig_country = country_spider(df_who, country, year_choice)
    st.plotly_chart(fig_country, use_container_width=False)
    #add graphs for country page here
    # print large: most recent algo ranking
    # line plot of score over time, can hover to see exact score for any year
