import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from pax_utils import *
import streamlit as st

# retrieve data from pax_utils
MetroData = MetroData()
Eda = EDA()
ForecastModel = ForecastModel()
df_pass = MetroData.df_pass
# retrieve metor line names
lines = Eda.lines
# get passengers in different time resolutions for every line
pax_by_month = Eda.pax_by_month
pax_by_year = Eda.pax_by_year
pax_by_semester = Eda.pax_by_semester
# get data for prediction model and pax income
ticket_hist = ForecastModel.ticket_hist
df_pred = ForecastModel.df_pred

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

st.markdown("## Income by Passenger")
st.markdown("""### Historic Ticket Fees
Ticket prices correspond to a specific type of passenger for certain metro lines, precisely Line A and Line B""")

tf_col1, tf_col2 = st.columns([3,1])
with tf_col2:
    st.table(ticket_hist)
    plot_hist_fees = st.checkbox("Plot historic ticket fees")
    plot_prediction = st.checkbox("Plot Linear Model")

if plot_hist_fees and plot_prediction==False:
    with tf_col1:
        fig1 = px.scatter(ticket_hist, x="Year", y="Price")
        fig1.update_layout(xaxis_type="category")
        st.plotly_chart(fig1, use_container_width=True)
if plot_prediction and plot_hist_fees:
    with tf_col1:
        fig1 = px.scatter(ticket_hist, x="Year", y="Price")
        fig1.update_layout(xaxis_type="category")
        
        fig2 = px.line(df_pred, x="Year", y="Price")
        fig2.update_traces(line_color='rgba(50,50,50,0.2)')

        fig3 = go.Figure(data=fig1.data+fig2.data)
        st.plotly_chart(fig3, use_container_width=True)

if plot_hist_fees and plot_prediction:
    st.markdown("---")
    compute_pax_income = st.button("Compute income from passengers")
    if compute_pax_income:
        # compute income from passengers of Lines A and B
        df_income = pax_by_year[(pax_by_year["Line"]=="LineA") | (pax_by_year["Line"]=="LineB")]
        df_income = pd.merge(df_income, df_pred, how="left", on="Year")
        df_income["TotalIncome"] = np.round(df_income["Price"] * df_income["Passengers"], 2)
        
        st.plotly_chart(px.line(df_income, x="Year", y="TotalIncome", color="Line"), use_container_width=True)
        with st.expander("See tabular data"):    
            st.table(df_income)