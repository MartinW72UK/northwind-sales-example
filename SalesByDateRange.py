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

# Sidebar: Date Inputs
st.sidebar.header("Filter by Date")
from_date = st.sidebar.date_input("From Date", datetime.date(2010, 1, 1))
to_date = st.sidebar.date_input("To Date", datetime.date(2014, 12, 31))

# Ensure from_date <= to_date
if from_date > to_date:
    st.error("Error: From Date must be earlier than To Date.")

# Load and Filter Data
data = load_data()

# Ensure date column is in datetime format
data['OrderDate'] = pd.to_datetime(data['OrderDate'])

# Filter data by date range
filtered_data = data[(data['OrderDate'] >= pd.to_datetime(from_date)) & 
                     (data['OrderDate'] <= pd.to_datetime(to_date))]

# Sidebar: Subcategory Filter
selected_subcategories = st.sidebar.multiselect(
    "Select Subcategories",
    options=filtered_data['SubcategoryName'].unique(),  
    default=filtered_data['SubcategoryName'].unique()
)

# Sidebar: Chart Type Selector
chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    options=["Bar Chart", "Line Chart"]
)

# Filter data by selected subcategories
filtered_data = filtered_data[filtered_data['SubcategoryName'].isin(selected_subcategories)]

# Display Filtered Data
st.subheader("Filtered Sales Data")
st.write(filtered_data)

# Aggregate Data by Category to reduce x-axis labels
df_grouped = filtered_data.groupby("CategoryName").agg({"LineTotal": "sum"}).reset_index()

# Render Chart
if not df_grouped.empty:
    fig, ax = plt.subplots()
    if chart_type == "Bar Chart":
        # Use horizontal bar chart for better readability
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
