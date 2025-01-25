import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import datetime

# Database Connection
server = 'localhost\\REPORTING'  # Your SQL Server instance
database = 'AdventureWorks2022'  # Your database name
username = 'Python'
password = 'python'

# Create SQLAlchemy engine
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)

# Title
st.title("Enhanced Sales Dashboard")

# Sidebar: Date Inputs
st.sidebar.header("Filter by Date")
from_date = st.sidebar.date_input("From Date", datetime.date(2010, 1, 1))
to_date = st.sidebar.date_input("To Date", datetime.date(2014, 12, 31))

# Ensure from_date <= to_date
if from_date > to_date:
    st.error("Error: From Date must be earlier than To Date.")

# Query the Database with Date Filter
@st.cache_data
def load_data(from_date, to_date):
    query = """
    SELECT 
        CAST(SUM(sod.LineTotal) AS DECIMAL(20, 2)) AS LineTotal,
        p.Name AS ProductName,
        ps.Name AS SubcategoryName,
        pc.Name AS CategoryName,
        CAST(soh.OrderDate AS DATE) AS OrderDate
    FROM 
        Sales.SalesOrderHeader soh
    JOIN 
        Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
    JOIN 
        Production.Product p ON sod.ProductID = p.ProductID
    LEFT JOIN 
        Production.ProductSubcategory ps ON p.ProductSubcategoryID = ps.ProductSubcategoryID
    LEFT JOIN 
        Production.ProductCategory pc ON ps.ProductCategoryID = pc.ProductCategoryID
    WHERE 
        soh.OrderDate BETWEEN ? AND ?
    GROUP BY 
        p.Name, ps.Name, pc.Name, CAST(soh.OrderDate AS DATE)
    ORDER BY 
        LineTotal DESC;
    """
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date_str = to_date.strftime('%Y-%m-%d')
    return pd.read_sql(query, con=engine, params=(from_date_str, to_date_str))

# Load Data
df = load_data(from_date, to_date)

# Sidebar: Subcategory Filter
selected_subcategories = st.sidebar.multiselect(
    "Select Subcategories",
    options=df['SubcategoryName'].unique(),
    default=df['SubcategoryName'].unique()
)

# Sidebar: Chart Type Selector
chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    options=["Bar Chart", "Line Chart"]
)

# Filter Data
filtered_df = df[df['SubcategoryName'].isin(selected_subcategories)]

# Display Data
st.subheader("Filtered Sales Data")
st.write(filtered_df)

# Aggregate Data by Category to reduce x-axis labels
df_grouped = filtered_df.groupby("CategoryName").agg({"LineTotal": "sum"}).reset_index()

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

