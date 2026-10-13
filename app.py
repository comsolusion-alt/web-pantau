import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman Web
st.set_page_config(page_title="Pantau Saham Emiten", page_icon="📈", layout="centered")

st.title("📈 Aplikasi Pemantau Emiten Saham")
st.write("Pantau pergerakan harga saham emiten pilihan Anda secara langsung.")

# --- BAGIAN 1: DETAIL SAHAM, GRAFIK & REKOMENDASI (DI ATAS) ---
st.subheader("🔍 Detail, Grafik & Analisis Saham")
default_ticker = "BBCA.JK"
ticker_symbol = st.text_input("Masukkan Kode Saham untuk melihat grafik detail:", value=default_ticker)

# Pilihan rentang waktu untuk grafik
time_period = st.selectbox(
    "Pilih Rentang Waktu Grafik:",
    options=["1mo", "6mo", "1y", "3y", "5y", "max"],
    format_func=lambda x: {
        "1mo": "1 Bulan",
        "6mo": "6 Bulan",
        "1y": "1 Tahun",
        "3y": "3 Tahun",
        "5y": "5 Tahun",
        "max": "Maksimum / Semua Data"
    }[x],
    index=2
)

if ticker_symbol:
    try:
        stock = yf.Ticker(ticker_symbol.strip().upper())
        hist = stock.history(period=time_period)
        
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
            price_change = latest_price - prev_price
            percent_change = (price_change / prev_price) * 100 if prev_price != 0 else 0
            
            col1, col2 = st.columns(2)
            col1.metric("Harga Terakhir", f"Rp {latest_price:,.2f}", f"{price_change:+,.2f} ({percent_change:+.2f}%)")
            
            st.write(f"### Grafik Harga ({time_period.upper()}): {ticker_symbol.upper()}")
            st.line_chart(hist['Close'])
            
            # --- FITUR REKOMENDASI OTOMATIS (BUY / SELL / HOLD) ---
            st.write("### 🤖 Indikator & Rekomendasi Otomatis")
            
            # Menghitung Moving Average 20 hari dan 50 hari untuk sinyal tren
            if len(hist) >= 50:
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                hist['MA50'] = hist['Close'].rolling(window=50).mean()
                
                ma20_latest = hist['MA20'].iloc[-1]
                ma50_latest = hist['MA50'].iloc[-1]
                
                # Logika Sinyal Sederhana Berdasarkan Tren MA & Posisi Harga
                signal = "HOLD"
                signal_color = "orange"
                reason = "Harga bergerak sideways atau dalam fase konsolidasi."
                
                if latest_price > ma20_latest and ma20_latest > ma50_latest:
                    signal = "STRONG BUY / BUY"
                    signal_color = "green"
                    reason = "Tren Bullish: Harga berada di atas rata-rata pergerakan 20 dan 50 hari."
                elif latest_price < ma20_latest and ma20_latest < ma50_latest:
                    signal = "STRONG SELL / SELL"
                    signal_color = "red"
                    reason = "Tren Bearish: Harga berada di bawah rata-rata pergerakan 20 dan 50 hari."
                
                st.markdown(f"**Rekomendasi Teknis:** <span style='color:{signal_color}; font-size:20px; font-weight:bold;'>{signal}</span>", unsafe_allow_html=True)
                st.info(f"💡 **Analisis:** {reason} (MA20: Rp {ma20_latest:,.2f} | MA50: Rp {ma50_latest:,.2f})")
            else:
                st.warning("⚠️ Data historis kurang dari 50 hari untuk menghitung indikator rekomendasi secara akurat.")
                
        else:
            st.warning("⚠️ Data untuk kode saham tersebut tidak ditemukan.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

st.divider()

# --- BAGIAN 2: FITUR WATCHLIST / DAFTAR PANTAU (DI BAWAH) ---
st.subheader("📋 Daftar Pantau (Watchlist)")
st.write("Daftar emiten pilihan yang dipantau secara berkala:")

default_watchlist = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "MBMA.JK", "POLA.JK", "ESTI.JK"]

watchlist_input = st.text_area(
    "Edit Daftar Saham (pisahkan dengan koma):", 
    value=", ".join(default_watchlist),
    help="Contoh: BBCA.JK, BBRI.JK, MBMA.JK"
)

watchlist = [s.strip().upper() for s in watchlist_input.split(",") if s.strip()]

if watchlist:
    watchlist_data = []
    for ticker in watchlist:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
                change = latest_price - prev_price
                pct_change = (change / prev_price) * 100 if prev_price != 0 else 0
                
                watchlist_data.append({
                    "Kode Saham": ticker,
                    "Harga Terakhir (Rp)": round(latest_price, 2),
                    "Perubahan": round(change, 2),
                    "Perubahan (%)": round(pct_change, 2)
                })
        except Exception:
            continue
    
    if watchlist_data:
        df_watchlist = pd.DataFrame(watchlist_data)
        df_watchlist.insert(0, "No", range(1, len(df_watchlist) + 1))
        st.dataframe(df_watchlist, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Tidak dapat memuat data untuk daftar saham tersebut.")
