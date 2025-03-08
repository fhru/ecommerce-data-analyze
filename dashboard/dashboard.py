import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import timedelta
sns.set(style='dark')

# Load data
all_df = pd.read_csv("dashboard/main_data.csv")

# Konversi kolom timestamp ke datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
if "order_delivered_customer_date" in all_df.columns:
    all_df["order_delivered_customer_date"] = pd.to_datetime(all_df["order_delivered_customer_date"])

def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    # Menentukan batas bawah dan batas atas
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Menyaring data agar hanya yang berada dalam batas
    df_clean = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].reset_index(drop=True)
    
    return df_clean

def calculate_rfm(df, start_date, end_date):
    # Filter berdasarkan rentang tanggal
    filtered_df = df[(df["order_purchase_timestamp"] >= start_date) & 
                     (df["order_purchase_timestamp"] <= end_date)]
    
    # Gunakan payment_value sebagai "price"
    if "payment_value" in filtered_df.columns:
        price_col = "payment_value"
    
    # Menentukan tanggal referensi (tanggal akhir yang dipilih)
    reference_date = end_date
    
    # Hitung RFM
    rfm = filtered_df.groupby("customer_id").agg(
        Recency=("order_purchase_timestamp", lambda x: (reference_date - x.max()).days),
        Frequency=("order_purchase_timestamp", "count"),
        Monetary=(price_col, "sum")
    ).reset_index()
    
    return rfm

def analyze_monthly_trends(df, start_date, end_date):
    # Filter berdasarkan rentang tanggal
    filtered_df = df[(df["order_purchase_timestamp"] >= start_date) & 
                     (df["order_purchase_timestamp"] <= end_date)]
    
    # Buat kolom bulan dan tahun
    filtered_df["order_month"] = filtered_df["order_purchase_timestamp"].dt.to_period("M")
    
    # Hitung total revenue per bulan
    monthly_revenue = filtered_df.groupby("order_month")["payment_value"].sum().reset_index()
    
    # Hitung jumlah order per bulan
    monthly_orders = filtered_df.groupby("order_month")["order_id"].nunique().reset_index()
    
    # Gabungkan revenue dan jumlah order menjadi satu tabel
    monthly_stats = monthly_orders.merge(monthly_revenue, on="order_month")
    
    # Ubah order_month menjadi string agar bisa ditampilkan dengan baik
    monthly_stats["order_month_str"] = monthly_stats["order_month"].astype(str)
    
    # Ubah nama kolom
    monthly_stats.rename(columns={"payment_value": "total_revenue", "order_id": "total_orders"}, inplace=True)
    
    return monthly_stats

st.sidebar.header("E-Commerce Dashboard")

# Menambahkan filter rentang tanggal
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

option = st.sidebar.selectbox("Pilih Analisis:", [
    "Pola Pembayaran",
    "Waktu Pengiriman",
    "Jumlah Pesanan per Hari",
    "Rata-rata Nilai Transaksi",
    "Analisis RFM",
    "Tren Bulanan"
])

st.sidebar.subheader("Filter Rentang Waktu")
start_date = st.sidebar.date_input("Tanggal Mulai", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Tanggal Akhir", max_date, min_value=min_date, max_value=max_date)

# Konversi date_input ke datetime untuk memfilter dataframe
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)  # untuk mengambil seluruh hari terakhir

# Filter dataframe berdasarkan rentang tanggal
filtered_df = all_df[(all_df["order_purchase_timestamp"] >= start_date) & 
                     (all_df["order_purchase_timestamp"] <= end_date)]

# Menampilkan informasi rentang waktu yang dipilih
st.sidebar.info(f"Data ditampilkan dari {start_date.strftime('%d %B %Y')} hingga {end_date.strftime('%d %B %Y')}")

st.title("E-Commerce Dashboard")
st.write(f"Data dari tanggal **{start_date.strftime('%d %B %Y')}** hingga **{end_date.strftime('%d %B %Y')}**")
st.write(f"Jumlah transaksi: **{len(filtered_df)}**")

if option == "Pola Pembayaran":
    st.subheader("Pola Pembayaran yang Paling Sering Digunakan")
    payment_counts = filtered_df["payment_type"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=payment_counts.index, y=payment_counts.values, ax=ax)
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Jumlah Pengguna")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)
    st.subheader("Bagaimana Pola Pembayaran yang Paling Sering Digunakan?")

# Analisis Waktu Pengiriman
elif option == "Waktu Pengiriman":
    st.subheader("Rata-rata Waktu Pengiriman")
    
    delivered_orders = filtered_df.dropna(subset=["order_delivered_customer_date"])

    # Hitung selisih hari antara pembelian dan diterima pelanggan
    delivered_orders["delivery_time_days"] = (delivered_orders["order_delivered_customer_date"] - delivered_orders["order_purchase_timestamp"]).dt.days

    # remove outliers
    delivered_orders_clean_df = remove_outliers(delivered_orders, 'delivery_time_days')

    avg_delivery_time = delivered_orders_clean_df["delivery_time_days"].mean()
    st.write(f"Rata-rata waktu pengiriman: {avg_delivery_time:.2f} hari")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(delivered_orders_clean_df["delivery_time_days"].dropna(), bins=20, kde=True, ax=ax)
    ax.set_xlabel("Waktu Pengiriman (hari)")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Waktu Pengiriman")
    st.pyplot(fig)

# Analisis Jumlah Pesanan per Hari
elif option == "Jumlah Pesanan per Hari":
    st.subheader("Jumlah Pesanan Berdasarkan Hari dalam Seminggu")
    filtered_df["order_dayofweek"] = filtered_df["order_purchase_timestamp"].dt.day_name()

    # Urutkan hari dalam seminggu
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    order_counts = filtered_df["order_dayofweek"].value_counts().reindex(day_order)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=order_counts.index, y=order_counts.values, ax=ax)
    ax.set_xlabel("Hari")
    ax.set_ylabel("Jumlah Pesanan")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

# Analisis Rata-rata Nilai Transaksi per Metode Pembayaran
elif option == "Rata-rata Nilai Transaksi":
    st.subheader("Rata-rata Nilai Transaksi Berdasarkan Metode Pembayaran")
    avg_payment_value = filtered_df.groupby("payment_type")["payment_value"].mean()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=avg_payment_value.index, y=avg_payment_value.values, ax=ax)
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Rata-rata Nilai Transaksi")
    plt.xticks(rotation=45, ha='right')
    
    # Tambahkan label nilai pada diagram
    for p in ax.patches:
        ax.annotate(f"R$ {p.get_height():.2f}", 
                   (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center', va = 'bottom',
                   xytext = (0, 5), textcoords = 'offset points')
    
    st.pyplot(fig)

# Analisis RFM
elif option == "Analisis RFM":
    st.subheader("Analisis RFM (Recency, Frequency, Monetary)")
    
    # Hitung RFM berdasarkan range tanggal yang dipilih
    rfm = calculate_rfm(all_df, start_date, end_date)
    
    if rfm is not None:
        st.write("### Statistik RFM")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata Recency", f"{rfm['Recency'].mean():.1f} hari")
        with col2:
            st.metric("Rata-rata Frequency", f"{rfm['Frequency'].mean():.1f} kali")
        with col3:
            st.metric("Rata-rata Monetary", f"R$ {rfm['Monetary'].mean():.2f}")
        
        st.write("### Data RFM")
        st.dataframe(rfm.head(10))
        
        rfm_view = st.radio("Pilih Tampilan:", ["Top Customers", "Distribusi RFM"])
        
        if rfm_view == "Top Customers":
          top_recency = rfm.sort_values(by="Recency", ascending=False).head(5)
          top_frequency = rfm.sort_values(by="Frequency", ascending=False).head(5)
          top_monetary = rfm.sort_values(by="Monetary", ascending=False).head(5)
          
          # Tampilkan top customers chart
          st.write("### Top 5 Customers berdasarkan Recency")
          fig_recency, ax_recency = plt.subplots(figsize=(10, 5))
          bars_recency = ax_recency.barh(top_recency["customer_id"].astype(str), top_recency["Recency"], color="skyblue")
          ax_recency.set_xlabel("Recency (days)")
          ax_recency.set_ylabel("Customer ID")
          ax_recency.set_title("Pelanggan dengan Recency Tertinggi (Paling Lama)")
          ax_recency.invert_yaxis() 
          
          # Tambahkan nilai pada bar chart
          for bar in bars_recency:
              width = bar.get_width()
              ax_recency.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.0f} hari", 
                              ha='left', va='center')
          
          plt.tight_layout()
          st.pyplot(fig_recency)
          
          st.write("### Top 5 Customers berdasarkan Frequency")
          fig_freq, ax_freq = plt.subplots(figsize=(10, 5))
          bars_freq = ax_freq.barh(top_frequency["customer_id"].astype(str), top_frequency["Frequency"], color="lightgreen")
          ax_freq.set_xlabel("Frequency (jumlah transaksi)")
          ax_freq.set_ylabel("Customer ID")
          ax_freq.set_title("Pelanggan dengan Frequency Tertinggi")
          ax_freq.invert_yaxis() 
          
          # Tambahkan nilai pada bar chart
          for bar in bars_freq:
              width = bar.get_width()
              ax_freq.text(width + 0.2, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                          ha='left', va='center')
          
          plt.tight_layout()
          st.pyplot(fig_freq)
          
          st.write("### Top 5 Customers berdasarkan Monetary")
          fig_mon, ax_mon = plt.subplots(figsize=(10, 5))
          bars_mon = ax_mon.barh(top_monetary["customer_id"].astype(str), top_monetary["Monetary"], color="salmon")
          ax_mon.set_xlabel("Monetary (R$)")
          ax_mon.set_ylabel("Customer ID")
          ax_mon.set_title("Pelanggan dengan Total Pembelian Tertinggi")
          ax_mon.invert_yaxis()
          
          # Format x-axis sebagai currency
          ax_mon.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'R$ {x:,.0f}'))
          
          # Tambahkan nilai pada bar chart
          for bar in bars_mon:
              width = bar.get_width()
              ax_mon.text(width + (width*0.02), bar.get_y() + bar.get_height()/2, f"R$ {width:,.2f}", 
                          ha='left', va='center')
          
          plt.tight_layout()
          st.pyplot(fig_mon)
        
        
        else:
            rfm_tabs = st.tabs(["Recency Distribution", "Frequency Distribution", "Monetary Distribution"])
            
            with rfm_tabs[0]:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(rfm["Recency"].dropna(), bins=30, kde=True, ax=ax)
                ax.set_xlabel("Recency (hari)")
                ax.set_ylabel("Jumlah Pelanggan")
                ax.set_title("Distribusi Recency")
                st.pyplot(fig)
            
            with rfm_tabs[1]:
                freq_filtered = remove_outliers(rfm, "Frequency")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(freq_filtered["Frequency"].dropna(), bins=20, kde=True, ax=ax)
                ax.set_xlabel("Frequency (jumlah transaksi)")
                ax.set_ylabel("Jumlah Pelanggan")
                ax.set_title("Distribusi Frequency")
                st.pyplot(fig)
            
            with rfm_tabs[2]:
                mon_filtered = remove_outliers(rfm, "Monetary")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(mon_filtered["Monetary"].dropna(), bins=20, kde=True, ax=ax)
                ax.set_xlabel("Monetary (R$)")
                ax.set_ylabel("Jumlah Pelanggan")
                ax.set_title("Distribusi Monetary")
                st.pyplot(fig)

elif option == "Tren Bulanan":
    st.subheader("Analisis Tren Bulanan (Revenue & Jumlah Order)")
    
    monthly_stats = analyze_monthly_trends(all_df, start_date, end_date)
    
    if monthly_stats is not None:
        st.write("### Tabel Revenue & Jumlah Order per Bulan")
        display_stats = monthly_stats[['order_month_str', 'total_orders', 'total_revenue']].copy()
        display_stats.rename(columns={'order_month_str': 'Bulan', 'total_orders': 'Total Orders', 'total_revenue': 'Total Revenue (R$)'}, inplace=True)
        display_stats['Total Revenue (R$)'] = display_stats['Total Revenue (R$)'].round(2)
        st.dataframe(display_stats)
        
        st.write("### Grafik Tren Bulanan")
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        ax1.set_xlabel("Bulan")
        ax1.set_ylabel("Total Revenue (R$)", color="blue")
        line1 = ax1.plot(monthly_stats["order_month_str"], monthly_stats["total_revenue"], 
                  marker="o", linestyle="-", color="blue", label="Total Revenue")
        ax1.tick_params(axis="y", labelcolor="blue")
        
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"R${x:,.0f}"))
        
        ax2 = ax1.twinx()
        ax2.set_ylabel("Total Orders", color="red")
        line2 = ax2.plot(monthly_stats["order_month_str"], monthly_stats["total_orders"], 
                  marker="s", linestyle="--", color="red", label="Total Orders")
        ax2.tick_params(axis="y", labelcolor="red")
        
        plt.xticks(rotation=45, ha="right")
        
        ax1.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc="upper left")
        
        plt.title("Tren Revenue & Jumlah Order per Bulan")
        plt.tight_layout()
        
        st.pyplot(fig)
        
        st.write("### Analisis Tren")
        
        monthly_stats["revenue_pct_change"] = monthly_stats["total_revenue"].pct_change() * 100
        monthly_stats["orders_pct_change"] = monthly_stats["total_orders"].pct_change() * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Bulan dengan revenue tertinggi
            max_revenue_month = monthly_stats.loc[monthly_stats["total_revenue"].idxmax(), "order_month_str"]
            max_revenue = monthly_stats["total_revenue"].max()
            st.metric("Bulan dengan Revenue Tertinggi", f"{max_revenue_month}", f"R$ {max_revenue:,.2f}")
        
        with col2:
            # Bulan dengan jumlah order tertinggi
            max_orders_month = monthly_stats.loc[monthly_stats["total_orders"].idxmax(), "order_month_str"]
            max_orders = monthly_stats["total_orders"].max()
            st.metric("Bulan dengan Order Tertinggi", f"{max_orders_month}", f"{max_orders:,} orders")
        
        with col3:
            # Rata-rata revenue per order
            avg_revenue_per_order = (monthly_stats["total_revenue"].sum() / monthly_stats["total_orders"].sum())
            st.metric("Rata-rata Revenue per Order", f"R$ {avg_revenue_per_order:.2f}")