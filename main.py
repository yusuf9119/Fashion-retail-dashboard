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
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%b %Y')
    df['Quarter'] = 'Q' + df['Date'].dt.quarter.astype(str)
    df['Profit'] = df['Selling_Price'] - df['Cost_Price']
    df['Profit_Margin'] = (df['Profit'] / df['Selling_Price']) * 100
    df['Age_Group'] = pd.cut(df['Customer_Age'], bins=[0, 18, 30, 40, 55, 100],
                             labels=['Teen', '20s', '30s', '40s-50s', '55+'])
    return df.dropna()

df = load_data()

with st.sidebar:
    st.header("Filters")
    dmin, dmax = df['Date'].min().date(), df['Date'].max().date()
    date_range = st.date_input("Date Range", (dmin, dmax), min_value=dmin, max_value=dmax)
    categories = st.multiselect("Categories", df['Product_Category'].unique().tolist(), default=None)
    genders = st.multiselect("Gender", df['Gender'].unique().tolist(), default=None)
    pay_method = st.selectbox("Payment Method", ["All"] + df['Payment_Method'].unique().tolist())

filtered = df[
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1])
]

if categories:
    filtered = filtered[filtered['Product_Category'].isin(categories)]
if genders:
    filtered = filtered[filtered['Gender'].isin(genders)]
if pay_method != "All":
    filtered = filtered[filtered['Payment_Method'] == pay_method]

monthly = filtered.groupby('Month').agg({
    'Selling_Price': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum'
}).reset_index()

st.title("🛍️ Fashion Retail Dashboard")
st.subheader("KPIs")

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="metric-box">Sales<br><span class="highlight">${filtered["Selling_Price"].sum():,.0f}</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-box">Profit<br><span class="highlight">${filtered["Profit"].sum():,.0f}</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric-box">Margin<br><span class="highlight">{filtered["Profit_Margin"].mean():.1f}%</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="metric-box">Transactions<br><span class="highlight">{filtered["Bill_Number"].nunique()}</span></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Trends", "📦 Products", "👥 Customers", "📂 Data"])

with tab1:
    st.subheader("Monthly Sales")
    fig1 = px.line(monthly, x='Month', y='Selling_Price', height=400)
    st.plotly_chart(fig1, use_container_width=True)

    quarterly = filtered.groupby(['Year', 'Quarter']).agg({
        'Selling_Price': 'sum',
        'Profit': 'sum'
    }).reset_index()
    quarterly['Quarter_Label'] = quarterly['Quarter'] + ' ' + quarterly['Year'].astype(str)

    st.subheader("Quarterly Summary")
    fig2 = px.bar(quarterly, x='Quarter_Label', y='Selling_Price', color='Profit')
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Category Breakdown")
    cat_data = filtered.groupby('Product_Category').agg({
        'Selling_Price': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    fig3 = px.treemap(cat_data, path=['Product_Category'], values='Selling_Price', color='Profit')
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Sales by Size")
    size_data = filtered.groupby('Size')['Selling_Price'].sum().reset_index()
    fig4 = px.bar(size_data, x='Size', y='Selling_Price')
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("By Age Group")
    age_data = filtered.groupby('Age_Group').agg({
        'Selling_Price': 'sum',
        'Customer_ID': 'nunique'
    }).reset_index()
    fig5 = px.bar(age_data, x='Age_Group', y='Selling_Price', color='Customer_ID')
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("By Gender")
    gender_data = filtered.groupby('Gender').agg({
        'Selling_Price': 'sum'
    }).reset_index()
    fig6 = px.pie(gender_data, names='Gender', values='Selling_Price', hole=0.3)
    st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.subheader("Preview & Export")
    st.dataframe(filtered.head(500))
    csv = filtered.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name=f"retail_data_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#999;">Fashion Dashboard • Built with Streamlit</div>', unsafe_allow_html=True)
