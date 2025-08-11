import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Multi-Page Dashboard",
    page_icon="📊",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox("Choose a page:", ["Hello", "Goodbye", "Data Dashboard"])

# Page 1: Hello
if page == "Hello":
    # Get welcome message from environment variable
    welcome_message = os.getenv('WELCOME_MESSAGE', 'Hello')  # Default to 'Hello' if not found
    st.title(welcome_message)
    
    # Optional: Display additional info about the environment variable
    st.caption("💡 This message is loaded from the .env file")

# Page 2: Goodbye  
elif page == "Goodbye":
    st.title("Goodbye")

# Page 3: Original Data Dashboard
elif page == "Data Dashboard":
    # Main title
    st.title("📊 Sample Table Data Dashboard")
    st.write("This is a simple Streamlit application displaying various types of sample data.")

    # Sidebar
    st.sidebar.header("Data Options")
    table_type = st.sidebar.selectbox(
        "Select table type:",
        ["Sales Data", "Employee Data", "Product Inventory", "Financial Data"]
    )

    # Generate sample data based on selection
    if table_type == "Sales Data":
        st.header("🛒 Sales Data")
        
        # Create sample sales data
        np.random.seed(42)
        data = {
            'Date': pd.date_range('2024-01-01', periods=50, freq='D'),
            'Product': np.random.choice(['Product A', 'Product B', 'Product C', 'Product D'], 50),
            'Sales Amount': np.random.randint(100, 1000, 50),
            'Quantity': np.random.randint(1, 20, 50),
            'Sales Rep': np.random.choice(['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'], 50)
        }
        
    elif table_type == "Employee Data":
        st.header("👥 Employee Data")
        
        # Create sample employee data
        np.random.seed(42)
        data = {
            'Employee ID': [f'EMP{str(i).zfill(3)}' for i in range(1, 26)],
            'Name': [f'Employee {i}' for i in range(1, 26)],
            'Department': np.random.choice(['HR', 'Engineering', 'Sales', 'Marketing', 'Finance'], 25),
            'Salary': np.random.randint(40000, 120000, 25),
            'Years of Experience': np.random.randint(1, 15, 25),
            'Performance Rating': np.random.choice(['Excellent', 'Good', 'Average', 'Needs Improvement'], 25)
        }
        
    elif table_type == "Product Inventory":
        st.header("📦 Product Inventory")
        
        # Create sample inventory data
        np.random.seed(42)
        data = {
            'Product Code': [f'PRD{str(i).zfill(3)}' for i in range(1, 31)],
            'Product Name': [f'Product {i}' for i in range(1, 31)],
            'Category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports'], 30),
            'Stock Quantity': np.random.randint(0, 500, 30),
            'Unit Price': np.round(np.random.uniform(10, 200, 30), 2),
            'Supplier': np.random.choice(['Supplier A', 'Supplier B', 'Supplier C'], 30)
        }
        
    else:  # Financial Data
        st.header("💰 Financial Data")
        
        # Create sample financial data
        np.random.seed(42)
        data = {
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Account': np.random.choice(['Revenue', 'Expenses', 'Assets', 'Liabilities'], 30),
            'Amount': np.round(np.random.uniform(1000, 50000, 30), 2),
            'Category': np.random.choice(['Operations', 'Marketing', 'R&D', 'Administration'], 30),
            'Status': np.random.choice(['Approved', 'Pending', 'Rejected'], 30)
        }

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Display the table
    st.subheader("Data Table")
    st.dataframe(df, use_container_width=True)

    # Display some basic statistics
    st.subheader("📈 Basic Statistics")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Rows", len(df))
        st.metric("Total Columns", len(df.columns))

    with col2:
        # Show numeric column statistics if available
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            first_numeric_col = numeric_cols[0]
            st.metric(f"Average {first_numeric_col}", f"{df[first_numeric_col].mean():.2f}")
            st.metric(f"Max {first_numeric_col}", f"{df[first_numeric_col].max():.2f}")

    # Download button
    st.subheader("💾 Download Data")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"{table_type.lower().replace(' ', '_')}_data.csv",
        mime="text/csv"
    )

    # Additional features
    st.subheader("🔍 Data Exploration")

    # Search functionality
    search_term = st.text_input("Search in data:")
    if search_term:
        # Search across all string columns
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        filtered_df = df[mask]
        st.write(f"Found {len(filtered_df)} matching rows:")
        st.dataframe(filtered_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit* 🚀")