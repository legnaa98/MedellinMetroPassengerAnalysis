import plotly.express as px
import streamlit as st
from pax_utils import *

# retrieve data from pax_utils
MetroData = MetroData()
Eda = EDA()
df_pass = MetroData.df_pass
# retrieve metor line names
lines = Eda.lines
# get passengers in different time resolutions for every line
pax_by_month = Eda.pax_by_month
pax_by_year = Eda.pax_by_year
pax_by_semester = Eda.pax_by_semester
# streamlit layout config
st.set_page_config(layout="wide")

st.markdown("# Medellin Metro Passenger Analysis")
st.markdown("---")

col1, col2 = st.columns([5, 1])

with col2:
    sampling = st.selectbox(
        "Select time resolution",
        [
            "Yearly",
            "Semestral",
            "Monthly",
        ],
        index=0,
    )
    plot_type = st.radio("Data type", ["All passengers", "Passengers by line"], index=0)
    # define resolution data
    if sampling == "Yearly":
        pax_chart_df = pax_by_year
    elif sampling == "Monthly":
        pax_chart_df = pax_by_month
    elif sampling == "Semestral":
        pax_chart_df = pax_by_semester
        x_axis_type = "category"
    # define plot type
    time_res_col = pax_chart_df.columns[0]
    if plot_type == "All passengers":
        pax_chart_df = pax_chart_df.groupby(time_res_col, as_index=False)[
            "Passengers"
        ].sum()
        if sampling != "Semestral":
            pax_chart = px.line(pax_chart_df, x=time_res_col, y="Passengers")
        else:
            pax_chart = px.line(pax_chart_df, x=time_res_col, y="Passengers")
            pax_chart.update_layout(xaxis_type="category")
    elif plot_type == "Passengers by line":
        if sampling != "Semestral":
            pax_chart = px.line(
                pax_chart_df, x=time_res_col, y="Passengers", color="Line"
            )
        else:
            pax_chart = px.line(
                pax_chart_df, x=time_res_col, y="Passengers", color="Line"
            )
            pax_chart.update_layout(xaxis_type="category")

    # exceptions

with col1:
    st.plotly_chart(pax_chart, use_container_width=True)


with st.expander("See tabular data"):
    # exceptionto not ddisplay hours in monthly sampling case
    if sampling == "Monthly":
        pax_chart_df["YearMonth"] = pax_chart_df["YearMonth"].dt.date
    # show tabular data
    st.table(pax_chart_df)
