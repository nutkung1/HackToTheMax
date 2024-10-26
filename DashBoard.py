import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import time
import requests

sumperDay = pd.read_csv("Sum Per Day.csv")

import datetime

today = datetime.datetime.now()
next_year = today.year
jan_1 = datetime.date(next_year, 6, 1)
dec_31 = datetime.date(next_year, 7, 31)


def DashBoard():
    # st.title(":green[_DashBoard_] :sunglasses:")
    st.title("📊 DashBoard")
    col1, col2 = st.columns([0.55, 0.5])
    with col1:
        with st.container(
            border=True,
        ):
            sumpertranDf = pd.read_csv("Sumpertran (1).csv")
            sumpertranDf1 = sumpertranDf.copy()
            c = (
                alt.Chart(sumpertranDf1.iloc[0:450])
                .mark_area()
                .encode(
                    x="tran_date",
                    color="payment_type_name",
                    y="carbon_emission_per_type",
                )
                .properties(
                    width=500,
                    height=385,
                    title="Overall Carbon Emissions by Payment Type",
                )
            )
            st.altair_chart(c, use_container_width=True)
        import streamlit.components.v1 as components

        with st.container(border=True):
            components.iframe(
                "https://carboncredits.com/live-carbon-prices/index.php", height=384
            )
    with col2:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            col1.metric(
                "Average CO2e footprint reduction per week", "16,473 CO2", "13%+"
            )
            col2.metric(
                "Average increase in weekly transactions", "6,616 person", "10%"
            )
        with st.container(
            border=True,
        ):
            col1, col2 = st.columns([0.32, 0.7])
            with col1:
                d = st.date_input(
                    "Select your range",
                    (jan_1, datetime.date(next_year, 6, 8)),
                    jan_1,
                    dec_31,
                    format="YYYY.MM.DD",
                )
                options = st.multiselect(
                    "Categorize Payment Type",
                    [
                        "All",
                        "ATMs",
                        "Bank_cards",
                        "Bank_notes",
                        "Cheques",
                        "Coins",
                        "POS_machines",
                        "QR_codes",
                    ],
                    ["All"],
                )
            df = pd.read_csv("Sumpertran (1).csv")

            df["tran_date"] = pd.to_datetime(df["tran_date"])

            # Filter data based on selected date range
            mask = (df["tran_date"].dt.date >= d[0]) & (df["tran_date"].dt.date <= d[1])
            filtered_df = df[mask]

            # Group by payment type and sum carbon emissions
            summary_df = (
                filtered_df.groupby("payment_type_name")["carbon_emission_per_type"]
                .sum()
                .reset_index()
            )
            summary_df.columns = [
                "category",
                "value",
            ]  # Rename columns to match your example

            # Create the donut chart
            chart = (
                alt.Chart(summary_df)
                .mark_arc(innerRadius=40)
                .encode(
                    theta=alt.Theta(field="value", type="quantitative"),
                    color=alt.Color(
                        "category:N",
                        scale=alt.Scale(scheme="tableau20"),  # Use a color scheme
                        legend=alt.Legend(title="Payment Type", orient="right"),
                    ),
                    tooltip=[
                        alt.Tooltip("category:N", title="Payment Type"),
                        alt.Tooltip("value:Q", title="Carbon Emission", format=",.2f"),
                    ],
                )
                .properties(
                    width=200, height=244, title="Carbon Emissions by Payment Type"
                )
                .configure_title(
                    fontSize=18, fontWeight="bold", anchor="middle", color="teal"
                )
                .configure_legend(
                    titleFontSize=12,
                    labelFontSize=10,
                    titleColor="gray",
                    labelColor="darkblue",
                    orient="right",
                )
                .configure_view(stroke=None)  # Remove border around the chart
            )
            # Display the chart
            with col2:
                st.altair_chart(chart, use_container_width=True)
        with st.container(border=True):
            st.header("Forecast 30 days")
            st.image("forecast_plot.png", use_column_width=True)
