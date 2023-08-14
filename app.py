# core Python modules
import calendar
from datetime import datetime

# https://www.youtube.com/watch?v=3egaMfE9388
import streamlit as st # pip install streamlit
from streamlit_option_menu import option_menu # pip install streamlit-option-menu
import plotly.graph_objects as go # pip install plotly

# database
import database as db # local import

# ------------- SETTINGS --------------------
incomes = ["Salary", "Blog", "Other Income"]
expenses = ["Rent", "Food", "Saving", "Other Expenses"]
currency = "USD"
page_title = "Cashflow Tracker"
page_icon = ":money_with_wings:" # emojis: https://www.webfx.com/tools/emoji-cheat-sheet
layout = "centered"

# -------------------------------------------
st.set_page_config(page_title=page_title, page_icon = page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# ----- DROP DPWN VALUES FOR SELECTIONS ----
years = [datetime.today().year, datetime.today().year+1]
months = list(calendar.month_name[1:]) # grab all months in a year

# ----- DATABASE FUNCTIONALITY -------------
def get_all_records():
    items = db.fetch_all()
    periods = [item["key"] for item in items]
    return periods

# ----- CUSTOM STYLING ----------------------
hide_st_style = """
                <style>
                #MainMenu {visibility: hdden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ----- NAVIGATION MENUE --------------------
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-char-fill"],  #https://icons.getbootstrap.com
    orientation="horizontal",
)

# -------- INPUT FORM -----------------------
if selected == "Data Entry":
    st.header(f"Data Entry in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        # set up 2 columns
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")
        # add divider for visual separation
        "---"

        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment")
        
        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            # send information to database
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.create(period, incomes, expenses, comment)
            st.success("Data Saved!")

# --------- PLOT DATA ---------------------
if selected == "Data Visualization":
    st.header("Data Visualization")
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_records())
        submitted = st.form_submit_button("Plot Period")
        # get data from database
        if submitted:
            data = db.get(period)
            comment = data.get("comment")
            expenses = data.get("expenses")
            incomes = data.get("incomes")

            # compute metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense

            # display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col2.metric("Total Expense", f"{total_expense} {currency}")
            col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
            st.text(f"Comment: {comment}")

            # Create Sankey chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

            # data to dict, dict to Sankey 
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            data = go.Sankey(link=link, node=node)

            # plot figure
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)
