import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import redis
import pickle
import streamlit as st
import ssl
import plotly.graph_objs as go

# Define Redis connection parameters
redis_url = "rediss://red-co8egigl5elc738tgqn0:HFzRb4hmIrjFUU12illslOXzCSR39WTQ@oregon-redis.render.com:6379"

# Create Redis connection
redis_client = redis.StrictRedis.from_url(redis_url, ssl_cert_reqs=ssl.CERT_NONE)

# Function to get data from Yahoo Finance or Redis cache
def get_data(symbol):
    # Check if data is already cached
    cached_data = redis_client.get(symbol)
    if cached_data:
        return pickle.loads(cached_data)

    # Download data
    current_date = datetime.now()

# Add one day to the current date
    end_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    data = yf.download(symbol, start=start_date, end=end_date)

    # Cache data
    redis_client.setex(symbol, timedelta(hours=1), pickle.dumps(data))

    return data

# Function to get Bollinger Bands
def get_bollinger_bands(data, window=20, num_std=2):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()

    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)

    return upper_band, lower_band

# Function to check signal
def check_signal(data):
    last_price = data['Close'].iloc[-1]
    upper_band, lower_band = get_bollinger_bands(data)
    sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]

    if last_price <= lower_band.iloc[-1] * 1.03:
        return 'Long', 'green'

    if last_price >= sma_20 * 1.01 and last_price < sma_20 * 1.05:
        return 'Long', 'green'

    upper_band_price = upper_band.iloc[-1]
    if last_price >= upper_band_price or last_price <= upper_band_price * 0.99:
        return 'Short', 'red'

    return 'No signal', 'blue'

# Function to display data
def display_data(symbol, data, signal, color):
    st.write(f"Symbol: {symbol}")
    st.write("Signal:", signal)
    st.write("Last Close Price:", data['Close'].iloc[-1])

# Main function
def main():
    st.title("Stock Signals")

    # NIFTY 200 Stocks List
    symbols = [
        'ABB.NS', 'ACC.NS', 'APLAPOLLO.NS', 'AUBANK.NS', 'ADANIENSOL.NS', 'ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS',
        'ATGL.NS', 'ABCAPITAL.NS', 'ABFRL.NS', 'ALKEM.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS', 'APOLLOTYRE.NS', 'ASHOKLEY.NS', 'ASIANPAINT.NS',
        'ASTRAL.NS', 'AUROPHARMA.NS', 'DMART.NS', 'AXISBANK.NS', 'BSE.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BAJAJHLDNG.NS',
        'BALKRISIND.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BANKINDIA.NS', 'MAHABANK.NS', 'BERGEPAINT.NS', 'BDL.NS', 'BEL.NS', 'BHARATFORG.NS',
        'BHEL.NS', 'BPCL.NS', 'BHARTIARTL.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'BRITANNIA.NS', 'CGPOWER.NS', 'CANBK.NS', 'CHOLAFIN.NS', 'CIPLA.NS',
        'COALINDIA.NS', 'COFORGE.NS', 'COLPAL.NS', 'CONCOR.NS', 'CUMMINSIND.NS', 'DLF.NS', 'DABUR.NS', 'DALBHARAT.NS', 'DEEPAKNTR.NS', 'DELHIVERY.NS',
        'DIVISLAB.NS', 'DIXON.NS', 'LALPATHLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'ESCORTS.NS', 'NYKAA.NS', 'FEDERALBNK.NS', 'FACT.NS', 'FORTIS.NS',
        'GAIL.NS', 'GMRINFRA.NS', 'GLAND.NS', 'GODREJCP.NS', 'GODREJPROP.NS', 'GRASIM.NS', 'GUJGASLTD.NS', 'HCLTECH.NS', 'HDFCAMC.NS', 'HDFCBANK.NS',
        'HDFCLIFE.NS', 'HAVELLS.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HAL.NS', 'HINDPETRO.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 'ICICIGI.NS',
        'ICICIPRULI.NS', 'IDBI.NS', 'IDFCFIRSTB.NS', 'ITC.NS', 'INDIANB.NS', 'INDHOTEL.NS', 'IOC.NS', 'IRCTC.NS', 'IRFC.NS', 'IGL.NS', 'INDUSTOWER.NS',
        'INDUSINDBK.NS', 'NAUKRI.NS', 'INFY.NS', 'INDIGO.NS', 'IPCALAB.NS', 'JSWENERGY.NS', 'JSWINFRA.NS', 'JSWSTEEL.NS', 'JINDALSTEL.NS', 'JIOFIN.NS',
        'JUBLFOOD.NS', 'KPITTECH.NS', 'KALYANKJIL.NS', 'KOTAKBANK.NS', 'LTF.NS', 'LTTS.NS', 'LICHSGFIN.NS', 'LTIM.NS', 'LT.NS', 'LAURUSLABS.NS', 'LICI.NS',
        'LUPIN.NS', 'MRF.NS', 'LODHA.NS', 'M&MFIN.NS', 'M&M.NS', 'MANKIND.NS', 'MARICO.NS', 'MARUTI.NS', 'MFSL.NS', 'MAXHEALTH.NS', 'MAZDOCK.NS', 'MPHASIS.NS',
        'NHPC.NS', 'NMDC.NS', 'NTPC.NS', 'NESTLEIND.NS', 'OBEROIRLTY.NS', 'ONGC.NS', 'OIL.NS', 'PAYTM.NS', 'OFSS.NS', 'POLICYBZR.NS', 'PIIND.NS', 'PAGEIND.NS',
        'PATANJALI.NS', 'PERSISTENT.NS', 'PETRONET.NS', 'PIDILITIND.NS', 'PEL.NS', 'POLYCAB.NS', 'POONAWALLA.NS', 'PFC.NS', 'POWERGRID.NS', 'PRESTIGE.NS',
        'PNB.NS', 'RECLTD.NS', 'RVNL.NS', 'RELIANCE.NS', 'SBICARD.NS', 'SBILIFE.NS', 'SJVN.NS', 'SRF.NS', 'MOTHERSON.NS', 'SHREECEM.NS', 'SHRIRAMFIN.NS',
        'SIEMENS.NS', 'SONACOMS.NS', 'SBIN.NS', 'SAIL.NS', 'SUNPHARMA.NS', 'SUNTV.NS', 'SUPREMEIND.NS', 'SUZLON.NS', 'SYNGENE.NS', 'TVSMOTOR.NS', 'TATACHEM.NS',
        'TATACOMM.NS', 'TCS.NS', 'TATACONSUM.NS', 'TATAELXSI.NS', 'TATAMTRDVR.NS', 'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TATATECH.NS', 'TECHM.NS',
        'TITAN.NS', 'TORNTPHARM.NS', 'TORNTPOWER.NS', 'TRENT.NS', 'TIINDIA.NS', 'UPL.NS', 'ULTRACEMCO.NS', 'UNIONBANK.NS', 'MCDOWELL-N.NS', 'VBL.NS', 'VEDL.NS',
        'IDEA.NS', 'VOLTAS.NS', 'WIPRO.NS', 'YESBANK.NS', 'ZEEL.NS', 'ZOMATO.NS', 'ZYDUSLIFE.NS'
    ]

    results = []
    
    for symbol in symbols:
            # Get data from cache or download if not cached
            data = get_data(symbol)

            # Check signal
            signal = check_signal(data)

            last_close_price = data['Close'].iloc[-1]
            
            results.append({'Date':datetime.now().strftime('%Y-%m-%d'), 'Symbol': symbol, 'Last Close Price': last_close_price, 'Signal': signal[0]})

    # Create DataFrame from results
    df = pd.DataFrame(results)
    # Display symbols in a table
    st.write("NIFTY 200 Stocks List:")
    st.write(df)
    
    st.sidebar.title("Filter Options")

# Create a checkbox for each signal type
    long_filter = st.sidebar.checkbox("Long")
    short_filter = st.sidebar.checkbox("Short")
    no_signal_filter = st.sidebar.checkbox("No Signal")

    # Filter the DataFrame based on the selected options
    filtered_df = df.copy()

    if long_filter:
        filtered_df = filtered_df[filtered_df['Signal'] == 'Long']
    if short_filter:
        filtered_df = filtered_df[filtered_df['Signal'] == 'Short']
    if no_signal_filter:
        filtered_df = filtered_df[filtered_df['Signal'] == 'No signal']

    # Display the filtered DataFrame
    st.write("Filtered Stocks List:")
    st.write(filtered_df)

    # Text input for user input
    user_input = st.text_input("Enter a stock symbol (e.g., TCS.NS):")

    if user_input:
        data = get_data(user_input)
        if data.empty:
            st.error(f"No data available for symbol: {user_input}")
        else:
            signal, color = check_signal(data)
            display_data(user_input, data, signal, color)
            
            st.subheader(f"Stock Data for {user_input}")
            st.write(data)

            # Plot the closing price
            st.subheader("Closing Price Chart")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
            fig.update_layout(title=f'{user_input} Closing Price', xaxis_title='Date', yaxis_title='Price')
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
