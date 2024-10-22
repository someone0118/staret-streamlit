import requests
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def get_exchange_rates(base_currency='USD'):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['rates']
    else:
        st.error("!!! Cannot retrieve exchange rates data !!!")
        return None

# ฟังก์ชันสำหรับแสดงกราฟ
def plot_exchange_rates(exchange_rates, base_currency, x_size, y_size, x_min, x_max, y_min, y_max):
    currencies = list(exchange_rates.keys())
    rates = list(exchange_rates.values())

    plt.figure(figsize=(x_size, y_size))  # ขนาดกราฟตามค่าที่ผู้ใช้เลือก
    plt.bar(currencies, rates)
    plt.title(f'Exchange Rates from {base_currency}')
    plt.xlabel('Currency')
    plt.ylabel('Exchange Rate')
    plt.xticks(rotation=45)

    # ตั้งค่าขอบเขตของแกน X และ Y
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    plt.tight_layout()
    
    st.pyplot(plt)

# ฟังก์ชันสำหรับแสดงตารางเปรียบเทียบค่าเงิน
def show_currency_comparison(exchange_rates):
    df = pd.DataFrame(list(exchange_rates.items()), columns=['Currency', 'Exchange Rate'])
    
    # สร้างคอลัมน์เพื่อแสดงว่าเงินแข็งตัวหรืออ่อนตัว
    df['Trend'] = df['Exchange Rate'].apply(lambda x: 'Strong' if x > 1 else 'Weak')
    
    # แยกข้อมูลออกเป็นค่าเงินแข็งตัวและอ่อนตัว
    strong_currencies = df[df['Trend'] == 'Strong']
    weak_currencies = df[df['Trend'] == 'Weak']
    
    st.subheader("Currency Strength Comparison")
    st.write("### Strong Currencies")
    st.dataframe(strong_currencies)

    st.write("### Weak Currencies")
    st.dataframe(weak_currencies)

# ตั้งชื่อแอปพลิเคชัน
st.title("Currency Comparison Tool")

# รับสกุลเงินจากผู้ใช้
base_currency = st.selectbox("Select base currency:", options=["USD", "EUR", "THB", "JPY", "GBP", "AUD", "CAD"])

# ดึงข้อมูลอัตราแลกเปลี่ยน
exchange_rates = get_exchange_rates(base_currency)

if exchange_rates:
    # ให้ผู้ใช้เลือกสกุลเงินที่ต้องการเปรียบเทียบ
    target_currency = st.selectbox("Select target currency to compare:", options=list(exchange_rates.keys()))
    
    # รับจำนวนเงินจากผู้ใช้
    amount = st.number_input("Enter amount in {}:".format(base_currency), min_value=0.0, step=0.01)

    # แสดงผลลัพธ์
    if st.button("Compare"):
        rate = exchange_rates[target_currency]
        converted_amount = amount * rate
        st.success(f"{amount:.2f} {base_currency} = {converted_amount:.2f} {target_currency}")

    # ปรับขนาดกราฟจากผู้ใช้
    x_size = st.slider("Select width of graph:", min_value=5, max_value=20, value=10)
    y_size = st.slider("Select height of graph:", min_value=3, max_value=10, value=5)

    # กล่องข้อมูลสำหรับปรับย่านของแกน X และ Y
    x_min = st.number_input("Set X-axis min value:", value=0)
    x_max = st.number_input("Set X-axis max value:", value=len(exchange_rates) - 1)
    y_min = st.number_input("Set Y-axis min value:", value=0)
    y_max = st.number_input("Set Y-axis max value:", value=int(max(exchange_rates.values()) * 1.2))

    # แสดงกราฟอัตราแลกเปลี่ยนทั้งหมด
    plot_exchange_rates(exchange_rates, base_currency, x_size, y_size, x_min, x_max, y_min, y_max)

    # แสดงตารางเปรียบเทียบค่าเงินแข็งตัวและอ่อนตัว
    show_currency_comparison(exchange_rates)
