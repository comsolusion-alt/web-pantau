import streamlit as st
import yfinance as yf
import pandas as pd

# Judul Aplikasi Web
st.set_page_config(page_title="Pantau Saham Emiten", page_icon="📈", layout="centered")

st.title("📈 Aplikasi Pemantau Emiten Saham")
st.write("Pantau pergerakan harga saham emiten pilihan Anda secara langsung.")

# Kolom Input untuk Kode Saham
# Contoh: BBCA.JK untuk Bank Central Asia, TLKM.JK untuk Telkom Indonesia
default_ticker = "BBCA.JK"
ticker_symbol = st.text_input("Masukkan Kode Saham (contoh: BBCA.JK, TLKM.JK, ASII.JK):", value=default_ticker)

if ticker_symbol:
    try:
        # Mengambil data saham dari Yahoo Finance
        stock = yf.Ticker(ticker_symbol.strip().upper())
        hist = stock.history(period="1mo") # Data historis 1 bulan terakhir
        
        if not hist.empty:
            # Mengambil data harga terbaru
            latest_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = latest_price - prev_price
            percent_change = (price_change / prev_price) * 100
            
            # Menampilkan Metrik Utama
            st.subheader(f"Informasi Saham: {ticker_symbol.upper()}")
            col1, col2 = st.columns(2)
            col1.metric("Harga Terakhir", f"Rp {latest_price:,.2f}", f"{price_change:+,.2f} ({percent_change:+.2f}%)")
            
            # Grafik Pergerakan Harga 1 Bulan
            st.write("### Grafik Harga (1 Bulan Terakhir)")
            st.line_chart(hist['Close'])
            
            # Tabel Data Historis Singkat
            st.write("### Data Historis Terbaru")
            st.dataframe(hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5))
        else:
            st.warning("⚠️ Data untuk kode saham tersebut tidak ditemukan. Pastikan format penulisan benar (misal: BBCA.JK untuk saham bursa Indonesia).")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
