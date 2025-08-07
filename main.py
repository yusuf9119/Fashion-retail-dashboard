import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide", page_title="Fashion Retail Dashboard", page_icon="🛍️")

st.markdown("""
<style>
.metric-box {
    padding: 14px;
    border-radius: 8px;
    background-color: #f2f2f2;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    font-size: 16px;
    text-align: center;
}
.highlight {
    font-weight: bold;
    color: #0066cc;
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("Fashion_Retail_Sales.csv")
    df['Date Purchase'] = pd.to_datetime(df['Date Purchase'], errors='coerce')
    df = df.dropna(subset=['Date Purchase', 'Purchase Amount (USD)'])
    df['Year'] = df['Date Purchase'].dt.year
    df['Month'] = df['Date Purchase'].dt.strftime('%b %Y')
    df['Quarter'] = 'Q' + df['Date Purchase'].dt.quarter.astype(str)
    return df

df = load_data()

with st.sidebar:
    st.header("Filters")
    dmin, dmax = df['Date Purchase'].min().date(), df['Date Purchase'].max().date()
    date_range = st.date_input("Date Range", (dmin, dmax), min_value=dmin, max_value=dmax)
    categories = st.multiselect("Items Purchased", sorted(df['Item Purchased'].dropna().unique()), default=None)
    pay_methods = ["All"] + sorted(df['Payment Method'].dropna().unique().tolist())
    pay_method = st.selectbox("Payment Method", pay_methods)

filtered = df[
    (df['Date Purchase'].dt.date >= date_range[0]) &
    (df['Date Purchase'].dt.date <= date_range[1])
]

if categories:
    filtered = filtered[filtered['Item Purchased'].isin(categories)]
if pay_method != "All":
    filtered = filtered[filtered['Payment Method'] == pay_method]

monthly = filtered.groupby('Month').agg({'Purchase Amount (USD)': 'sum'}).reset_index()

st.title("🛍️ Fashion Retail Dashboard")
st.subheader("KPIs")

c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="metric-box">Sales<br><span class="highlight">${filtered["Purchase Amount (USD)"].sum():,.0f}</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-box">Average Rating<br><span class="highlight">{filtered["Review Rating"].mean():.2f}</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric-box">Transactions<br><span class="highlight">{filtered["Customer Reference ID"].nunique()}</span></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Trends", "📦 Items Purchased", "📂 Data"])

with tab1:
    st.subheader("Monthly Sales")
    fig1 = px.line(monthly, x='Month', y='Purchase Amount (USD)', height=400)
    st.plotly_chart(fig1, use_container_width=True)

    quarterly = filtered.groupby(['Year', 'Quarter']).agg({'Purchase Amount (USD)': 'sum'}).reset_index()
    quarterly['Quarter_Label'] = quarterly['Quarter'] + ' ' + quarterly['Year'].astype(str)
    st.subheader("Quarterly Summary")
    fig2 = px.bar(quarterly, x='Quarter_Label', y='Purchase Amount (USD)')
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Items Purchased Breakdown")
    item_data = filtered.groupby('Item Purchased').agg({
        'Purchase Amount (USD)': 'sum',
        'Customer Reference ID': 'nunique'
    }).reset_index()
    fig3 = px.bar(item_data, x='Item Purchased', y='Purchase Amount (USD)', color='Customer Reference ID', labels={"Customer Reference ID": "Unique Customers"})
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Preview & Export")
    st.dataframe(filtered.head(500))
    csv = filtered.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name=f"retail_data_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#999;">Fashion Dashboard • Built with Streamlit</div>', unsafe_allow_html=True)

