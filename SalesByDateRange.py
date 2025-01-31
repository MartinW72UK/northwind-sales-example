import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Load the data from a CSV file
@st.cache_data
def load_data():
    return pd.read_csv('sales_data.csv')

# Title
st.title("Enhanced Sales Dashboard")

# Load Data
data = load_data()

# Ensure date column is in datetime format
data['OrderDate'] = pd.to_datetime(data['OrderDate'], errors='coerce')

# Get available date range
min_date = data['OrderDate'].min().date()
max_date = data['OrderDate'].max().date()

# Store defaults in session state if not already set
if "from_date" not in st.session_state:
    st.session_state.from_date = min_date
if "to_date" not in st.session_state:
    st.session_state.to_date = max_date

# Sidebar: Date Inputs
from_date = st.sidebar.date_input(
    "From Date", 
    value=st.session_state.from_date if "from_date" in st.session_state else min_date,
    key="from_date"
)

to_date = st.sidebar.date_input(
    "To Date", 
    value=st.session_state.to_date if "to_date" in st.session_state else max_date,
    key="to_date"
)


# Reset Filters Button
if st.sidebar.button("Reset Filters"):
    st.session_state.from_date = min_date
    st.session_state.to_date = max_date
    st.rerun()  # Ensures Streamlit refreshes with reset values

# Ensure from_date <= to_date
if from_date > to_date:
    st.error("Error: From Date must be earlier than To Date.")

# Filter Data by Date Range
filtered_data = data[(data['OrderDate'] >= pd.to_datetime(from_date)) & 
                     (data['OrderDate'] <= pd.to_datetime(to_date))]

# Sidebar: Subcategory Filter
selected_subcategories = st.sidebar.multiselect(
    "Select Subcategories",
    options=filtered_data['SubcategoryName'].dropna().unique(),  
    default=filtered_data['SubcategoryName'].dropna().unique()
)

# Sidebar: Chart Type Selector
chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    options=["Bar Chart", "Line Chart"]
)

# Filter data by selected subcategories
filtered_data = filtered_data[filtered_data['SubcategoryName'].isin(selected_subcategories)]

# Display Available Date Range When No Data Found
if filtered_data.empty:
    st.warning("No sales found for the selected period. Try adjusting the filters.")
    st.info(f"📅 Available data ranges from **{min_date}** to **{max_date}**")

# Display Filtered Data
st.subheader("Filtered Sales Data")
st.write(filtered_data)

# Aggregate Data by Category
if not filtered_data.empty:
    df_grouped = filtered_data.groupby("CategoryName").agg({"LineTotal": "sum"}).reset_index()
    
    # Render Chart
    if not df_grouped.empty:
        fig, ax = plt.subplots()
        if chart_type == "Bar Chart":
            ax.barh(df_grouped['CategoryName'], df_grouped['LineTotal'], color='skyblue')
            ax.set_title("Sales by Category (Bar Chart)")
            ax.set_xlabel("Sales")
            ax.set_ylabel("Category")
        elif chart_type == "Line Chart":
            ax.plot(df_grouped['CategoryName'], df_grouped['LineTotal'], marker='o', color='green')
            ax.set_title("Sales by Category (Line Chart)")
            ax.set_xlabel("Category")
            ax.set_ylabel("Sales")
            plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("No data to display. Please adjust your filters.")
