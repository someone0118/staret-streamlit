import requests
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time

def get_exchange_rates(base_currency='USD'):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['rates']
    else:
        st.error("!!! Cannot retrieve exchange rates data !!!")
        return None

# Function to plot exchange rates
def plot_exchange_rates(exchange_rates, base_currency, x_size, y_size):
    plt.clf()  # Clear the current figure
    currencies = list(exchange_rates.keys())
    rates = list(exchange_rates.values())

    plt.figure(figsize=(x_size, y_size))
    plt.bar(currencies, rates, color='steelblue', edgecolor='black')
    plt.title(f'Exchange Rates from {base_currency}', fontsize=14)
    plt.xlabel('Currency', fontsize=12)
    plt.ylabel('Exchange Rate', fontsize=12)
    plt.xticks(rotation=45, fontsize=10)
    
    plt.ylim(0, max(rates) * 1.2)  # Set Y-axis limits dynamically
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(plt)

# Function to show currency comparison
def show_currency_comparison(exchange_rates):
    df = pd.DataFrame(list(exchange_rates.items()), columns=['Currency', 'Exchange Rate'])
    df['Trend'] = df['Exchange Rate'].apply(lambda x: 'Strong' if x > 1 else 'Weak')
    
    strong_currencies = df[df['Trend'] == 'Strong']
    weak_currencies = df[df['Trend'] == 'Weak']
    
    st.subheader("Currency Strength Comparison")
    st.write("### Strong Currencies")
    st.dataframe(strong_currencies.style.highlight_max(axis=0, color='lightgreen'))

    st.write("### Weak Currencies")
    st.dataframe(weak_currencies.style.highlight_min(axis=0, color='lightcoral'))

# Function to show mixed currency rates
def show_mixed_currency_rates(exchange_rates, selected_currencies):
    mixed_rates = {currency: exchange_rates[currency] for currency in selected_currencies}
    df = pd.DataFrame(list(mixed_rates.items()), columns=['Currency', 'Exchange Rate'])
    st.subheader("Mixed Currency Rates")
    st.dataframe(df)

# Set up the application title
st.title("Currency Comparison Tool")
st.markdown("""
    <style>
    body {
        background-color: #f4f4f4;  /* Light gray color */
        font-family: 'Arial', sans-serif;
    }
    .title {
        font-size: 22px;
        font-weight: bold;
        color: #333;
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

# User selects base currency
base_currency = st.selectbox("Select base currency:", options=["USD", "EUR", "THB", "JPY", "GBP", "AUD", "CAD"])

# Refresh rates every minute or on button press
if 'exchange_rates' not in st.session_state or st.session_state.last_update < time.time() - 60:
    exchange_rates = get_exchange_rates(base_currency)
    if exchange_rates is not None:
        st.session_state.exchange_rates = exchange_rates
        st.session_state.last_update = time.time()
else:
    exchange_rates = st.session_state.exchange_rates

if st.button("Refresh Exchange Rates"):
    exchange_rates = get_exchange_rates(base_currency)
    if exchange_rates is not None:
        st.session_state.exchange_rates = exchange_rates
        st.session_state.last_update = time.time()

if exchange_rates:
    # User selects target currencies
    target_currencies = st.multiselect("Select target currencies to compare:", options=list(exchange_rates.keys()))
    
    # Show mixed currency rates if selected
    if target_currencies:
        show_mixed_currency_rates(exchange_rates, target_currencies)

    # User inputs amount
    amount = st.number_input(f"Enter amount in {base_currency}:", min_value=0.0, step=0.01)

    # Show result on button press
    if st.button("Compare"):
        if target_currencies:
            results = []
            for currency in target_currencies:
                rate = exchange_rates[currency]
                converted_amount = amount * rate
                results.append(f"{amount:.2f} {base_currency} = {converted_amount:.2f} {currency}")

            st.success("\n".join(results))
        else:
            st.warning("Please select at least one target currency to compare.")

    # Set graph size from user input
    x_size = st.slider("Select width of graph:", min_value=5, max_value=20, value=10)
    y_size = st.slider("Select height of graph:", min_value=3, max_value=10, value=5)

    # Show the exchange rates graph
    plot_exchange_rates(exchange_rates, base_currency, x_size, y_size)

    # Show the currency comparison table
    show_currency_comparison(exchange_rates)
