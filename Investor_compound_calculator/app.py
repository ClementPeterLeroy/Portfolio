import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Investment Calculator", layout="wide")
st.title("Investment Growth Calculator")

with st.sidebar:
    st.header("Investment Parameters")
    start_amount = st.number_input("Starting Amount ($)", value=10_000, step=1_000, min_value=0)
    annual_return = st.slider("Annual Return Rate (%)", 0.0, 30.0, 7.0, 0.1) / 100
    yearly_contribution = st.number_input("Additional Contribution per Year ($)", value=1_200, step=100, min_value=0)
    monthly_contribution = st.number_input("Additional Contribution per Month ($)", value=0, step=50, min_value=0)
    years = st.number_input("Investment Horizon (years)", min_value=1, max_value=50, value=10)


def compute_growth(start, annual_rate, yearly_contrib, monthly_contrib, years):
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
    n_months = years * 12

    principal_track = np.zeros(n_months)
    contribution_track = np.zeros(n_months)
    interest_track = np.zeros(n_months)

    balance = start
    total_contributed = 0.0
    total_interest = 0.0
    cumulative_start_value = start

    for m in range(n_months):
        contrib_this_month = monthly_contrib
        if m % 12 == 0 and m > 0:
            contrib_this_month += yearly_contrib

        balance += contrib_this_month
        total_contributed += contrib_this_month

        interest = balance * monthly_rate
        balance += interest
        total_interest += interest

        cumulative_start_value *= (1 + monthly_rate)

        principal_track[m] = cumulative_start_value
        contribution_track[m] = total_contributed
        interest_track[m] = total_interest

    months = np.arange(1, n_months + 1)
    return balance, months, principal_track, contribution_track, interest_track


final_balance, months, principal_track, contribution_track, interest_track = compute_growth(start_amount, annual_return, yearly_contribution, monthly_contribution, years)

total_invested = start_amount + yearly_contribution * years + monthly_contribution * 12 * years
total_gain = final_balance - total_invested

col1, col2, col3 = st.columns(3)
col1.metric("Final Portfolio Value", f"${final_balance:,.2f}")
col2.metric("Total Contributed", f"${total_invested:,.2f}")
col3.metric(
    "Total Interest Earned",
    f"${total_gain:,.2f}",
    delta=f"{(total_gain / total_invested * 100):.1f}% return" if total_invested > 0 else "N/A"
)

tab1, tab2 = st.tabs(["Chart", "Monthly Table"])

with tab1:
    fig = go.Figure()
    fig.add_bar(x=months, y=principal_track, name="Starting Amount", marker_color="#2196F3")
    fig.add_bar(x=months, y=contribution_track, name="Contributions", marker_color="#4CAF50")
    fig.add_bar(x=months, y=interest_track, name="Interest", marker_color="#FF9800")
    fig.update_layout(
        barmode="stack",
        xaxis_title="Month",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_tickformat="$,.0f"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df = pd.DataFrame({
        "Month": months,
        "Year": ((months - 1) // 12) + 1,
        "Starting Amount ($)": principal_track.round(2),
        "Cumulative Contributions ($)": contribution_track.round(2),
        "Cumulative Interest ($)": interest_track.round(2),
        "Total Portfolio Value ($)": (principal_track + contribution_track + interest_track).round(2)
    })
    st.dataframe(df, use_container_width=True)
