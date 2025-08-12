import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import time
import yfinance as yf

# Load environment variables
load_dotenv()

# Function to fetch stock price data
def get_stock_prices(ticker, months_count, period="1y", fallback_data=None):
    """
    Fetch stock prices for a given ticker symbol with fallback support
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'MSFT', 'AAPL') or forex pair (e.g., 'USDAUD=X')
        months_count (int): Number of months of data needed
        period (str): Period for data fetch (default: '1y')
        fallback_data (dict): Optional fallback data with 'base_value' and 'variation_range'
    
    Returns:
        tuple: (data_list, is_real_data, status_message)
    """
    try:
        # Download stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval="1mo")
        
        if not hist.empty:
            # Get monthly closing prices
            prices_real = hist['Close'].values
            # Ensure we have the right number of data points
            if len(prices_real) >= months_count:
                data = list(prices_real[-months_count:])
                return data, True, f"✅ Real {ticker} data loaded successfully!"
            else:
                # If we don't have enough data, pad with the last known price
                data = list(prices_real) + [prices_real[-1]] * (months_count - len(prices_real))
                return data, True, f"✅ Real {ticker} data loaded successfully! (padded)"
        else:
            raise Exception("No data received from API")
            
    except Exception as e:
        # Generate fallback data if real data fetch fails
        if fallback_data:
            np.random.seed(42)  # For consistent fallback data
            base_value = fallback_data['base_value']
            variation_range = fallback_data['variation_range']
            
            if ticker.endswith('=X'):  # Forex data
                data = [base_value + np.random.uniform(-variation_range, variation_range) for _ in range(months_count)]
            else:  # Stock data
                data = [base_value + np.random.uniform(-variation_range, variation_range) + i * 2 for i in range(months_count)]
            
            return data, False, f"⚠️ Could not fetch real {ticker} data ({str(e)}). Using simulated data."
        else:
            # No fallback provided, raise exception
            raise Exception(f"Failed to fetch {ticker} data: {str(e)}")

# Set page configuration
st.set_page_config(
    page_title="Multi-Page Dashboard",
    page_icon="📊",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Choose a page:", ["Finance", "Daily", "Data Dashboard"])

# Page 1: Finance
if page == "Finance":
    # Get welcome message from environment variable
    welcome_message = os.getenv('WELCOME_MESSAGE', 'Hello')  # Default to 'Hello' if not found
    st.title(welcome_message)
    
    # Optional: Display additional info about the environment variable
    st.caption("💡 This message is loaded from the .env file")
    
    # Add combo chart section
    st.markdown("---")
    st.header("📊 Financial Performance Dashboard")
    st.write("Past 12 months overview with Net Worth, USD/AUD Exchange Rate, and MSFT Stock Price")
    
    # Set random seed for consistent data
    np.random.seed(42)
    
    # Read net worth data from CSV file
    try:
        # Try to read net worth data from CSV
        net_worth_df = pd.read_csv('net_worth_data.csv')
        net_worth_df['Date'] = pd.to_datetime(net_worth_df['Date'])
        
        # Sort by date
        net_worth_df = net_worth_df.sort_values('Date')
        
        # Create month labels from the CSV dates instead of generated dates
        months = [date.strftime('%b %Y') for date in net_worth_df['Date']]
        net_worth = net_worth_df['Net_Worth'].tolist()
        
        # Ensure we only show the last 12 months if we have more data
        if len(net_worth) > 12:
            months = months[-12:]
            net_worth = net_worth[-12:]
        
        st.success("✅ Net worth data loaded from CSV file!")
        
    except FileNotFoundError:
        st.warning("⚠️ net_worth_data.csv not found. Using simulated data.")
        # Fallback to generated data with original date logic
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        dates = pd.date_range(start=start_date, end=end_date, freq='ME')
        months = [date.strftime('%b %Y') for date in dates]
        base_net_worth = 500000
        net_worth = [base_net_worth + np.random.randint(-50000, 100000) + i * 5000 for i in range(len(months))]
    except Exception as e:
        st.warning(f"⚠️ Error reading CSV file ({str(e)}). Using simulated data.")
        # Fallback to generated data with original date logic
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        dates = pd.date_range(start=start_date, end=end_date, freq='ME')
        months = [date.strftime('%b %Y') for date in dates]
        base_net_worth = 500000
        net_worth = [base_net_worth + np.random.randint(-50000, 100000) + i * 5000 for i in range(len(months))]
    
    # Fetch USD/AUD exchange rate using yfinance
    with st.spinner('Fetching USD/AUD exchange rate...'):
        usd_aud_rate, is_real_usd_aud, usd_aud_message = get_stock_prices(
            "USDAUD=X", 
            len(months),
            fallback_data={'base_value': 1.45, 'variation_range': 0.15}
        )
        if is_real_usd_aud:
            st.success(usd_aud_message)
        else:
            st.warning(usd_aud_message)
    
    # Fetch real MSFT stock prices using yfinance
    with st.spinner('Fetching real MSFT stock data...'):
        msft_price, is_real_msft, msft_message = get_stock_prices(
            "MSFT", 
            len(months),
            fallback_data={'base_value': 350, 'variation_range': 50}
        )
        if is_real_msft:
            st.success(msft_message)
        else:
            st.warning(msft_message)
    

    # Create the combo chart using Plotly (Net Worth + MSFT Stock)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart for Net Worth
    fig.add_trace(
        go.Bar(
            x=months,
            y=net_worth,
            name="Net Worth ($)",
            marker_color='lightblue',
            opacity=0.7
        ),
        secondary_y=False
    )
    
    # Add line chart for MSFT Stock Price
    fig.add_trace(
        go.Scatter(
            x=months,
            y=msft_price,
            mode='lines+markers',
            name="MSFT Stock Price ($)",
            line=dict(color='green', width=3),
            marker=dict(size=6)
        ),
        secondary_y=True
    )
    
    # Update x-axis
    fig.update_xaxes(title_text="Month")
    
    # Update y-axes
    fig.update_yaxes(title_text="Net Worth ($)", secondary_y=False)
    fig.update_yaxes(title_text="MSFT Stock Price ($)", secondary_y=True)
    
    # Update layout
    fig.update_layout(
        title="Financial Performance - Net Worth & MSFT Stock",
        width=None,
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Display the first chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Create separate USD/AUD exchange rate chart
    fig_forex = go.Figure()
    
    # Add USD/AUD line chart
    fig_forex.add_trace(
        go.Scatter(
            x=months,
            y=usd_aud_rate,
            mode='lines+markers',
            name="USD/AUD Exchange Rate",
            line=dict(color='red', width=3),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.1)'
        )
    )
    
    # Calculate y-axis range for better zoom
    min_rate = min(usd_aud_rate)
    max_rate = max(usd_aud_rate)
    range_padding = (max_rate - min_rate) * 0.1  # Add 10% padding
    y_min = min_rate - range_padding
    y_max = max_rate + range_padding
    
    # Update layout for forex chart
    fig_forex.update_layout(
        title="USD/AUD Exchange Rate - Past 12 Months",
        xaxis_title="Month",
        yaxis_title="Exchange Rate (USD/AUD)",
        yaxis=dict(range=[y_min, y_max]),  # Set custom y-axis range
        width=None,
        height=300,
        hovermode='x',
        showlegend=False
    )
    
    # Display the forex chart
    st.plotly_chart(fig_forex, use_container_width=True)
    
    # Create MSFT price in AUD chart
    # Calculate MSFT price in AUD by multiplying USD price by USD/AUD rate
    msft_price_aud = [usd_price * exchange_rate for usd_price, exchange_rate in zip(msft_price, usd_aud_rate)]
    
    fig_msft_aud = go.Figure()
    
    # Add MSFT AUD line chart
    fig_msft_aud.add_trace(
        go.Scatter(
            x=months,
            y=msft_price_aud,
            mode='lines+markers',
            name="MSFT Price (AUD)",
            line=dict(color='purple', width=3),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(128,0,128,0.1)'
        )
    )
    
    # Calculate y-axis range for MSFT AUD chart
    min_price_aud = min(msft_price_aud)
    max_price_aud = max(msft_price_aud)
    price_range_padding = (max_price_aud - min_price_aud) * 0.1  # Add 10% padding
    price_y_min = min_price_aud - price_range_padding
    price_y_max = max_price_aud + price_range_padding
    
    # Update layout for MSFT AUD chart
    fig_msft_aud.update_layout(
        title="MSFT Stock Price in AUD - Past 12 Months",
        xaxis_title="Month",
        yaxis_title="MSFT Price (AUD)",
        yaxis=dict(range=[price_y_min, price_y_max]),  # Set custom y-axis range
        width=None,
        height=300,
        hovermode='x',
        showlegend=False
    )
    
    # Display the MSFT AUD chart
    st.plotly_chart(fig_msft_aud, use_container_width=True)
    
    # Add some metrics below the chart
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Current Net Worth",
            value=f"${net_worth[-1]:,.0f}",
            delta=f"${net_worth[-1] - net_worth[0]:,.0f}"
        )
    
    with col2:
        st.metric(
            label="Current USD/AUD Rate",
            value=f"{usd_aud_rate[-1]:.3f}",
            delta=f"{usd_aud_rate[-1] - usd_aud_rate[0]:+.3f}"
        )
    
    with col3:
        st.metric(
            label="Current MSFT Price",
            value=f"${msft_price[-1]:.2f}",
            delta=f"${msft_price[-1] - msft_price[0]:+.2f}"
        )
    
    with col4:
        st.metric(
            label="Current MSFT Price (AUD)",
            value=f"₱{msft_price_aud[-1]:,.2f}",
            delta=f"₱{msft_price_aud[-1] - msft_price_aud[0]:+.2f}"
        )

# Page 2: Goodbye  
elif page == "Daily":
    st.title("🌍 World Clock")
    st.write("Current time in different timezones around the world")
    
    # Read timezones from environment variable
    timezones_str = os.getenv('TIMEZONES', 'Australia/Sydney,Asia/Tokyo,Europe/London,America/New_York,America/Los_Angeles')
    timezone_list = [tz.strip() for tz in timezones_str.split(',')]
    
    # Create a mapping of timezone codes to friendly names
    timezone_names = {
        'Australia/Sydney': 'Sydney',
        'Asia/Tokyo': 'Osaka', 
        'Europe/London': 'London',
        'America/New_York': 'New York',
        'America/Los_Angeles': 'Seattle'  # Using Los Angeles timezone for Seattle
    }
    
    # Create columns for the clocks
    cols = st.columns(len(timezone_list))
    
    # Auto-refresh every second
    placeholder = st.empty()
    
    with placeholder.container():
        # Create a row of clocks
        clock_cols = st.columns(len(timezone_list))
        
        for i, tz_code in enumerate(timezone_list):
            with clock_cols[i]:
                try:
                    # Get timezone
                    tz = pytz.timezone(tz_code)
                    current_time = datetime.now(tz)
                    
                    # Get friendly name
                    city_name = timezone_names.get(tz_code, tz_code.split('/')[-1])
                    
                    # Determine if it's day or night (6 AM to 6 PM is day time)
                    hour = current_time.hour
                    is_daytime = 6 <= hour < 18
                    
                    # Set colors based on time of day
                    if is_daytime:
                        # Daytime: Orange/Yellow gradient
                        background_gradient = "background: linear-gradient(135deg, #ff9a56 0%, #ffad56 50%, #ffc947 100%);"
                        time_icon = "☀️"
                    else:
                        # Nighttime: Blue gradient
                        background_gradient = "background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #2c3e50 100%);"
                        time_icon = "🌙"
                    
                    # Create a nice clock display
                    st.markdown(f"""
                    <div style="
                        text-align: center; 
                        padding: 20px; 
                        border: 2px solid #ddd; 
                        border-radius: 15px; 
                        margin: 10px;
                        {background_gradient}
                        color: white;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    ">
                        <h3 style="margin: 0; color: white;">{time_icon} {city_name}</h3>
                        <div style="font-size: 2.5em; font-weight: bold; margin: 10px 0;">
                            {current_time.strftime('%H:%M')}
                        </div>
                        <div style="font-size: 1.2em; opacity: 0.9;">
                            {current_time.strftime('%A')}
                        </div>
                        <div style="font-size: 1em; opacity: 0.8;">
                            {current_time.strftime('%B %d, %Y')}
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.7; margin-top: 5px;">
                            UTC{current_time.strftime('%z')[:3]}:{current_time.strftime('%z')[3:]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error loading timezone {tz_code}: {str(e)}")
    
    # Add refresh button and auto-refresh option
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh every 30 seconds")
    
    with col3:
        st.markdown("*Times update automatically*")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Display timezone information
    st.markdown("---")
    st.subheader("📍 Timezone Information")
    
    timezone_info = []
    for tz_code in timezone_list:
        try:
            tz = pytz.timezone(tz_code)
            current_time = datetime.now(tz)
            city_name = timezone_names.get(tz_code, tz_code.split('/')[-1])
            
            timezone_info.append({
                'City': city_name,
                'Timezone': tz_code,
                'Current Time': current_time.strftime('%H:%M'),
                'Date': current_time.strftime('%Y-%m-%d'),
                'UTC Offset': current_time.strftime('%z')
            })
        except Exception as e:
            timezone_info.append({
                'City': tz_code,
                'Timezone': tz_code,
                'Current Time': 'Error',
                'Date': 'Error',
                'UTC Offset': 'Error'
            })
    
    # Display as a table
    df_timezones = pd.DataFrame(timezone_info)
    st.dataframe(df_timezones, use_container_width=True)

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