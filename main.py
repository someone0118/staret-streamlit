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

def plot_exchange_rates(exchange_rates, base_currency, x_size, y_size, graph_type, color_scheme):
    df = pd.DataFrame(list(exchange_rates.items()), columns=['Currency', 'Exchange Rate'])
    df['Trend'] = df['Exchange Rate'].apply(lambda x: 'Strong' if x > 1 else 'Weak')

    plt.figure(figsize=(x_size, y_size))
    colors = ['lightgreen' if x == 'Strong' else 'lightcoral' for x in df['Trend']] if color_scheme == 'Default' else ['blue' if x == 'Strong' else 'red' for x in df['Trend']]
    
    if graph_type == 'Bar':
        plt.bar(df['Currency'], df['Exchange Rate'], color=colors, edgecolor='black')
    else:
        plt.plot(df['Currency'], df['Exchange Rate'], marker='o', linestyle='-', color='blue')

    plt.title(f'Exchange Rates from {base_currency}', fontsize=14)
    plt.xlabel('Currency', fontsize=12)
    plt.ylabel('Exchange Rate', fontsize=12)
    plt.xticks(rotation=45, fontsize=10)
    
    plt.axhline(1, color='gray', linestyle='--')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(plt)

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

def calculate_tax(amount, tax_rate):
    return amount * (tax_rate / 100)

st.title("Currency Comparison Tool")
st.markdown("""<style>
    body {
        background-color: #f4f4f4;
        font-family: 'Arial', sans-serif;
        background-image: url('https://www.transparenttextures.com/patterns/paper.png');
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

base_currency = st.selectbox("Select base currency:", options=["USD", "EUR", "THB", "JPY", "GBP", "AUD", "CAD"])

# Refresh rates every minute
if 'exchange_rates' not in st.session_state or st.session_state.last_update < time.time() - 60:
    exchange_rates = get_exchange_rates(base_currency)
    st.session_state.exchange_rates = exchange_rates
    st.session_state.last_update = time.time()
else:
    exchange_rates = st.session_state.exchange_rates

if exchange_rates:
    target_currency = st.selectbox("Select target currency to compare:", options=list(exchange_rates.keys()))
    
    amount = st.number_input(f"Enter amount in {base_currency}:", min_value=0.0, step=0.01)
    tax_rate = st.number_input("Enter tax rate (%):", min_value=0.0, step=0.01)

    if st.button("Compare"):
        rate = exchange_rates[target_currency]
        converted_amount = amount * rate
        tax_amount = calculate_tax(converted_amount, tax_rate)
        total_amount = converted_amount + tax_amount
        
        st.success(f"{amount:.2f} {base_currency} = {converted_amount:.2f} {target_currency} (Tax: {tax_amount:.2f}, Total: {total_amount:.2f})")

    x_size = st.slider("Select width of graph:", min_value=5, max_value=20, value=10)
    y_size = st.slider("Select height of graph:", min_value=3, max_value=10, value=5)
    graph_type = st.selectbox("Select graph type:", options=["Bar", "Line"])
    color_scheme = st.selectbox("Select color scheme:", options=["Default", "Alternative"])

    plot_exchange_rates(exchange_rates, base_currency, x_size, y_size, graph_type, color_scheme)
    show_currency_comparison(exchange_rates)
