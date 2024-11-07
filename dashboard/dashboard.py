import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "total_value": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_category_sum_order(df):
    category_sum_order = df['product_category_name'].value_counts().reset_index(name='order_count')
    return category_sum_order

def create_delivery_status_count(df):
    delivery_status_count = df.groupby(by='delivery_status').order_id.nunique().reset_index()
    delivery_status_count.rename(columns={
        "order_id": "delivery_count"
    }, inplace=True)
    return delivery_status_count

def create_total_spending_count_by_city(df):
    total_spending_count_by_city = df.groupby('customer_city').agg(
        total_spending = ('total_value', 'sum'), # Mengambil total harga dengan menjumlahkan seluruh total_value
        customer_count = ('customer_id', 'nunique') # Mengambil jumlah customer
    ).sort_values(by='total_spending', ascending=False).reset_index()
    return total_spending_count_by_city

def create_average_spending_by_city_and_customer_density(df):
    average_spending_by_city = df.groupby('customer_city').agg(
        average_spending = ('total_value', 'mean'), # Mengambil average spending dengan rata-rata dari total_value
        customer_count = ('customer_id', 'nunique') # Mengambil jumlah customer
    ).sort_values(by='average_spending', ascending=False).reset_index()
    # Mendapatkan kota yang memiliki lebih dari satu customer
    average_spending_by_city = average_spending_by_city[average_spending_by_city['customer_count'] > 1]

    # Menghitung tertile dan memberikan kategori kota berdasarkan kepadatan pelanggannya
    average_spending_by_city['customer_density'] = pd.qcut(average_spending_by_city['customer_count'], q=3, labels=['Low', 'Medium', 'High'])
    average_spending_by_city['customer_density'].value_counts()
    return average_spending_by_city

st.header('Brazil E-Commerce Dashboard')

#-------------------SIDEBAR------------------------

all_df = pd.read_csv('all_data.csv')
datetime_columns = ['order_purchase_timestamp', 
                    'order_approved_at',
                    'order_delivered_customer_date'
                    ]
all_df.sort_values(by='order_approved_at')
all_df.reset_index(inplace=True)

for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()
 
with st.sidebar:
    st.header('A. Fuad Ahsan Basir')
    # Menambahkan logo perusahaan
    st.image("logo.png")
    st.write("Date Filter")
    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)
    
    try:
        if start_date and end_date:
            main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                            (all_df["order_approved_at"] <= str(end_date))]
        elif start_date:
            main_df = all_df[(all_df["order_approved_at"] == str(start_date))]
        elif end_date:
            main_df = all_df[(all_df["order_approved_at"] == str(end_date))]
        else:
            main_df = all_df
        daily_orders_df = create_daily_orders_df(main_df)
    
    except Exception as e:
        st.error(f"An error occurred while filtering data: {e}")
        st.write(all_df)  # Tampilkan semua data jika terjadi error

#-------------------DAILY ORDER------------------------

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

#-------------------PRODUCT CATEGORY SUM------------------------

st.subheader("Best & Worst Performing Product")

category_sum_order = create_category_sum_order(all_df)
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_count", y="product_category_name", data=category_sum_order.head(), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=40)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(x="order_count", y="product_category_name", data=category_sum_order.tail().sort_values(by='order_count'), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)

#-------------------DELIVERY PERFORMANCE------------------------

st.subheader("Delivery Performance")

delivery_status_count = create_delivery_status_count(all_df)

fig, ax = plt.subplots(figsize=(8, 4))

ax.pie(
    delivery_status_count['delivery_count'], 
    labels=delivery_status_count['delivery_status'],
    # show percentage with two decimal points
    autopct='%1.2f%%',
    colors=sns.color_palette('bright')[1:5],
    # increase the size of all text elements
    # textprops={'fontsize':18},
    explode=[0, 0.15]
)
# ax.tick_params(axis='y', labelsize=20)
# ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

#-------------------Top Cities by Number of Customers------------------------

st.subheader("Top Cities by Number of Customers")

total_spending_count_by_city = create_total_spending_count_by_city(all_df)

fig, ax = plt.subplots(figsize=(20,10))

sns.barplot(
    y="customer_city", 
    x="customer_count",
    data=total_spending_count_by_city.head(10),
    color='#72BCD4',
    ax=ax
)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

#-------------------Cities with the Highest Total Spending (in Million)------------------------

st.subheader("Cities with the Highest Total Spending (in Million)")

fig, ax = plt.subplots(figsize=(20,10))

sns.barplot(
    y="total_spending", 
    x="customer_city",
    data=total_spending_count_by_city.head(10),
    color='#72BCD4',
    ax=ax
)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=25, rotation=45)

st.pyplot(fig)

#-------------------Top Cities by Avg Spending & Customer Density------------------------

st.subheader("Top Cities by Average Spending & Customer Density")

average_spending_by_city_and_customer_density = create_average_spending_by_city_and_customer_density(all_df)
# Mendapatkan 3 kota dengan rata-rata pengeluaran tertinggi sesuai dengan kategori kepadatan pelanggannya
top_cities = average_spending_by_city_and_customer_density.groupby('customer_density').apply(lambda x: x.nlargest(3, 'average_spending')).reset_index(drop=True)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(24,8))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="customer_city", y="average_spending", data=top_cities[top_cities['customer_density'] == 'Low'], palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_ylim(0, 1400)
ax[0].set_title("Low Density", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15, rotation=45)

sns.barplot(x="customer_city", y="average_spending", data=top_cities[top_cities['customer_density'] == 'Medium'], palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_ylim(0, 1400)
ax[1].set_title("Medium Density", loc="center", fontsize=18)
ax[1].tick_params(axis ='x', labelsize=15, rotation=45)

sns.barplot(x="customer_city", y="average_spending", data=top_cities[top_cities['customer_density'] == 'High'], palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_ylim(0, 1400)
ax[2].set_title("High Density", loc="center", fontsize=18)
ax[2].tick_params(axis ='x', labelsize=15, rotation=45)

st.pyplot(fig)

#-------------------Customer Distribution Map------------------------
st.subheader("Customer Distribution Heatmap")

# Membaca file HTML dari disk
with open("customer_density_heatmap.html", "r") as file:
    html_content = file.read()

# Menampilkan HTML di Streamlit
st.components.v1.html(html_content, width=700, height=500)

#-------------------Seller Distribution Map------------------------
st.subheader("Seller Distribution Heatmap")

# Membaca file HTML dari disk
with open("seller_density_heatmap.html", "r") as file:
    html_content = file.read()

# Menampilkan HTML di Streamlit
st.components.v1.html(html_content, width=700, height=500)