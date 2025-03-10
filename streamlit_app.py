import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -------------------------
# Data Loading Function with Standardized Column Names
# -------------------------


@st.cache_data
def load_data():
    # -------------------
    # Load final IHME data
    # -------------------
    df_IHME = pd.read_csv("data_prep/final_data/final_IHME.csv")
    # Clean column names: strip spaces and remove quotes
    df_IHME.columns = df_IHME.columns.str.strip().str.replace('"', '')
    # Expected original columns in final_IHME.csv:
    # location, sex, cause, year, Deaths, Incidence
    # Standardize them:
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

    # -------------------
    # Load final WHO data
    # -------------------
    df_WHO = pd.read_csv("data_prep/final_data/final_who.csv")
    df_WHO.columns = df_WHO.columns.str.strip().str.replace('"', '')
    # Drop extra unnamed column if present
    df_WHO = df_WHO.loc[:, ~df_WHO.columns.str.contains("^Unnamed")]
    # Expected original WHO columns:
    # Location, Period, Medical Doctors per 10,000, Nurses and Midwifes per 10,000, Pharmacists per 10,000, Dentists per 10,000
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

    # -------------------
    # Load inner merged metrics data
    # -------------------
    df_metrics = pd.read_csv("data_prep/final_data/inner_merged_data.csv")
    df_metrics.columns = df_metrics.columns.str.strip().str.replace('"', '')
    df_metrics = df_metrics.loc[:, ~
                                df_metrics.columns.str.contains("^Unnamed")]
    # The inner merged file should have the same workforce columns.
    # It may use either "Period" or "year" for the time column.
    # We want to standardize on "year".
    if "Period" in df_metrics.columns and "year" not in df_metrics.columns:
        df_metrics = df_metrics.rename(columns={"Period": "year"})
    # In case it already uses "year", we leave it.
    # Now, rename the workforce columns (assuming they match the WHO file):
    metrics_mapping = {
        "Location": "location",
        "Medical Doctors per 10,000": "medical_doctors_per_10000",
        "Nurses and Midwifes per 10,000": "nurses_midwifes_per_10000",
        "Pharmacists per 10,000": "pharmacists_per_10000",
        "Dentists per 10,000": "dentists_per_10000"
    }
    df_metrics = df_metrics.rename(columns=metrics_mapping)
    # Ensure the time column is named "year"
    if "year" not in df_metrics.columns:
        raise ValueError(
            "inner_merged_data.csv must contain a time column named either 'year' or 'Period'.")
    expected_metrics = {"location", "year", "medical_doctors_per_10000",
                        "nurses_midwifes_per_10000", "pharmacists_per_10000", "dentists_per_10000"}
    if not expected_metrics.issubset(set(df_metrics.columns)):
        raise ValueError(
            f"inner_merged_data.csv is missing columns: {expected_metrics - set(df_metrics.columns)}")

    return df_IHME, df_WHO, df_metrics

# -------------------------
# Plotting Functions (using standardized column names)
# -------------------------


def plot_ihme_data(df, metric="deaths", selected_year=None, selected_location=None):
    # The IHME data now uses 'deaths' and 'incidence'
    if metric not in ["deaths", "incidence"]:
        raise ValueError("Metric must be 'deaths' or 'incidence'")

    required_columns = {"location", "cause", "year", metric}
    if not required_columns.issubset(set(df.columns)):
        missing_cols = required_columns - set(df.columns)
        raise ValueError(
            f"Missing required columns in IHME data: {missing_cols}")

    if selected_year is None:
        selected_year = df["year"].max()
    df_year = df[df["year"] == selected_year].dropna(
        subset=["location", "cause", metric])

    if selected_location:
        df_year = df_year[df_year["location"].isin(selected_location)]

    fig = px.bar(
        df_year,
        x="cause",
        y=metric,
        color="location",
        barmode="group",
        title=f"{metric.capitalize()} by Cause in {selected_year}"
    )
    fig.update_layout(xaxis_title="Cause",
                      yaxis_title=metric.capitalize(), template="plotly_white")
    return fig


def plot_who_data(df, selected_year=None):
    if selected_year is None:
        selected_year = df["year"].max()
    df_year = df[df["year"] == selected_year]

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
        title=f"Workforce Metrics by Location in {selected_year}",
        xaxis_title="Location",
        yaxis_title="Per 10000 Population",
        template="plotly_white",
        barmode="group"
    )
    return fig


def plot_metrics_by_country(df, primary_metric="medical_doctors_per_10000", secondary_metric="nurses_midwifes_per_10000", selected_year=None):
    if selected_year is None:
        selected_year = df["year"].max()
    df_year = df[df["year"] == selected_year].dropna(
        subset=["location", primary_metric, secondary_metric])

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
        line=dict(color="blue", dash="dash")
    ))
    fig.update_layout(
        title=f"{primary_metric.replace('_', ' ').capitalize()} & {secondary_metric.replace('_', ' ').capitalize()} by Location in {selected_year}",
        xaxis_title="Location",
        yaxis_title=primary_metric.replace("_", " ").capitalize(),
        template="plotly_white"
    )
    return fig


def plot_metrics_over_time(df, primary_metric="medical_doctors_per_10000", secondary_metric="nurses_midwifes_per_10000", selected_location=None):
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
            line=dict(dash="dash")
        ))
    fig.update_layout(
        title=f"{primary_metric.replace('_', ' ').capitalize()} & {secondary_metric.replace('_', ' ').capitalize()} Over Time",
        xaxis_title="Year",
        yaxis_title=primary_metric.replace("_", " ").capitalize(),
        template="plotly_white"
    )
    return fig


# -------------------------
# Main Dashboard Layout
# -------------------------
st.set_page_config(page_title="Health Data Dashboard", layout="wide")
st.title("Health Data Dashboard")

# Load data.
df_IHME, df_WHO, df_metrics = load_data()

# (Optional) Debug: Uncomment these lines to inspect standardized column names.
# st.write("IHME Data Columns:", df_IHME.columns.tolist())
# st.write("WHO Data Columns:", df_WHO.columns.tolist())
# st.write("Metrics Data Columns:", df_metrics.columns.tolist())

# Create tabs.
tabs = st.tabs(
    ["IHME Data", "WHO Data", "Metrics by Country", "Metrics Over Time"])

# -------- IHME Data Tab --------
with tabs[0]:
    st.header("IHME Data Visualization")
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_choice = st.selectbox("Select Metric", options=[
                                     "deaths", "incidence"])
    with col2:
        years = sorted(df_IHME["year"].unique())
        year_choice = st.selectbox(
            "Select Year", options=years, index=len(years)-1)
    with col3:
        locations = sorted(df_IHME["location"].unique())
        location_choice = st.multiselect(
            "Select Location(s)", options=locations, default=locations)
    fig_ihme = plot_ihme_data(df_IHME, metric=metric_choice,
                              selected_year=year_choice, selected_location=location_choice)
    st.plotly_chart(fig_ihme, use_container_width=True)

# -------- WHO Data Tab --------
with tabs[1]:
    st.header("WHO Data Visualization")
    col1 = st.columns(1)[0]
    with col1:
        years_who = sorted(df_WHO["year"].unique())
        year_choice_who = st.selectbox(
            "Select Year", options=years_who, index=len(years_who)-1)
    fig_who = plot_who_data(df_WHO, selected_year=year_choice_who)
    st.plotly_chart(fig_who, use_container_width=True)

# -------- Metrics by Country Tab --------
with tabs[2]:
    st.header("Metrics by Country")
    col1, col2, col3 = st.columns(3)
    workforce_metrics = [
        "medical_doctors_per_10000",
        "nurses_midwifes_per_10000",
        "pharmacists_per_10000",
        "dentists_per_10000"
    ]
    with col1:
        primary_metric_choice = st.selectbox(
            "Primary Metric", options=workforce_metrics, index=0)
    with col2:
        secondary_metric_choice = st.selectbox(
            "Secondary Metric", options=workforce_metrics, index=1)
    with col3:
        years_metrics = sorted(df_metrics["year"].unique())
        year_choice_metrics = st.selectbox(
            "Select Year", options=years_metrics, index=len(years_metrics)-1)
    fig_country = plot_metrics_by_country(
        df_metrics,
        primary_metric=primary_metric_choice,
        secondary_metric=secondary_metric_choice,
        selected_year=year_choice_metrics
    )
    st.plotly_chart(fig_country, use_container_width=True)

# -------- Metrics Over Time Tab --------
with tabs[3]:
    st.header("Metrics Over Time")
    col1, col2, col3 = st.columns(3)
    with col1:
        primary_metric_time = st.selectbox(
            "Primary Metric", options=workforce_metrics, index=0, key="over_time_primary")
    with col2:
        secondary_metric_time = st.selectbox(
            "Secondary Metric", options=workforce_metrics, index=1, key="over_time_secondary")
    with col3:
        available_locations = sorted(df_metrics["location"].dropna().unique())
        location_time_choice = st.multiselect(
            "Select Location(s)", options=available_locations, default=available_locations[:3])
    fig_time = plot_metrics_over_time(
        df_metrics,
        primary_metric=primary_metric_time,
        secondary_metric=secondary_metric_time,
        selected_location=location_time_choice
    )
    st.plotly_chart(fig_time, use_container_width=True)
