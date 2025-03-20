"""
Script to make the interactive dashboard for this project.
"""
import os
import streamlit as st

try:
    # When running as a package (e.g., during testing)
    from .data_prep import process_healthcare_data
except ImportError:
    # When running as a top-level script (e.g., via streamlit)
    from data_prep import process_healthcare_data


@st.cache_data
def load_data():
    """Loads and processes healthcare data from different sources."""
    file_path = os.path.join(os.getcwd(), "data/")
    df_who_data, df_ihme_data, df_metrics_data = process_healthcare_data(
        file_path)

    df_ihme_data.columns = df_ihme_data.columns.str.strip().str.replace('"', '')
    ihme_mapping = {
        "location": "location",
        "sex": "sex",
        "cause": "cause",
        "year": "year",
        "Deaths": "deaths",
        "Incidence": "incidence"
    }
    df_ihme_data = df_ihme_data.rename(columns=ihme_mapping)

    expected_ihme = set(ihme_mapping.values())
    if not expected_ihme.issubset(set(df_ihme_data.columns)):
        raise ValueError(
            f"final_IHME.csv is missing columns: {expected_ihme - set(df_ihme_data.columns)}"
        )

    df_who_data.columns = df_who_data.columns.str.strip().str.replace('"', '')
    df_who_data = df_who_data.loc[:, ~
                                  df_who_data.columns.str.contains("^Unnamed")]
    who_mapping = {
        "Location": "location",
        "Period": "year",
        "Medical Doctors per 10,000": "medical_doctors_per_10000",
        "Nurses and Midwifes per 10,000": "nurses_midwifes_per_10000",
        "Pharmacists per 10,000": "pharmacists_per_10000",
        "Dentists per 10,000": "dentists_per_10000"
    }
    df_who_data = df_who_data.rename(columns=who_mapping)
    expected_who = set(who_mapping.values())
    if not expected_who.issubset(set(df_who_data.columns)):
        raise ValueError(
            f"final_who.csv is missing columns: {expected_who - set(df_who_data.columns)}"
        )

    df_metrics_data.columns = df_metrics_data.columns.str.strip().str.replace('"', '')
    df_metrics_data = df_metrics_data.loc[:, ~
                                          df_metrics_data.columns.str.contains("^Unnamed")]

    if "Period" in df_metrics_data.columns and "year" not in df_metrics_data.columns:
        df_metrics_data = df_metrics_data.rename(columns={"Period": "year"})

    metrics_mapping = {
        "Location": "location",
        "medical doctors per 10,000": "medical_doctors_per_10000",
        "nurses and midwifes per 10,000": "nurses_midwifes_per_10000",
        "pharmacists per 10,000": "pharmacists_per_10000",
        "dentists per 10,000": "dentists_per_10000"
    }
    df_metrics_data = df_metrics_data.rename(columns=metrics_mapping)

    expected_metrics = {
        "location", "year", "medical_doctors_per_10000",
        "nurses_midwifes_per_10000", "pharmacists_per_10000", "dentists_per_10000"
    }
    if not expected_metrics.issubset(set(df_metrics_data.columns)):
        raise ValueError(
            f"inner_merged_data has missing cols: {expected_metrics - set(df_metrics_data.columns)}"
        )

    return df_ihme_data, df_who_data, df_metrics_data


# Dashboard layout
st.set_page_config(page_title="Global Healthcare", layout="wide")
st.title("Global Healthcare")

# Load data.
df_ihme, df_who, df_metrics = load_data()

# Create tabs.
tabs = st.tabs([
    "Home", "IHME Data", "WHO Data", "Data by Country", "Data Over Time", "Country Overview"
])

with tabs[0]:
    st.header("Ranking and Scores")
    st.write(
        "Welcome! This site provides an interactive overview of healthcare workforce and"
        " outcome metrics for various countries. Filter data in the available tabs. Enjoy!"
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Healthcare Systems by Year")
        years = sorted(df_metrics["year"].unique())
        selected_year = st.selectbox("Select Year", years, key="home_year")
    with col2:
        top_countries = df_metrics[df_metrics["year"]
                                   == selected_year].nsmallest(5, "rank")
        st.subheader(f"Top 5 Countries in {selected_year}:")
        for _, row in top_countries.iterrows():
            st.write(f"**{row['rank']} {row['location']}**")

    st.markdown("---")
    st.subheader("Composite Score or Ranking Over Time by Country")
    metric_choice = st.selectbox(
        "Select Metric", ["composite_score", "rank"], key="home_metric")
    location_choice = st.multiselect(
        "Select Location(s)", sorted(df_metrics["location"].dropna().unique()),
        default=["United States of America"], key="home_loc"
    )
    st.markdown("---")

    country_list = sorted(df_metrics["location"].dropna().unique())
    country_selection = st.multiselect(
        "Select Location(s)", country_list, default=["United States of America"], key="country1"
    )

st.write("DISCLAIMER: The rankings presented are limited by available data.")
