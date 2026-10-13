import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman Web
st.set_page_config(page_title="Pantau Saham Emiten", page_icon="📈", layout="centered")

st.title("📈 Aplikasi Pemantau Emiten Saham")
st.write("Pantau pergerakan harga saham emiten pilihan Anda secara interaktif.")

# --- BAGIAN 1: DETAIL SAHAM & GRAFIK CANDLESTICK ---
st.subheader("🔍 Grafik & Analisis Teknikal")
default_ticker = "BBCA.JK"
ticker_symbol = st.text_input("Masukkan Kode Saham:", value=default_ticker)

if ticker_symbol:
    try:
        stock = yf.Ticker(ticker_symbol.strip().upper())
        
        # --- PILIHAN RENTANG WAKTU DI BAWAH GRAFIK (MODEL PILIHAN TOMBOL/MENU) ---
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            time_period = st.selectbox(
                "Rentang Waktu:",
                options=["1mo", "3mo", "6mo", "1y", "3y", "5y", "max"],
                format_func=lambda x: {
                    "1mo": "1 Bulan",
                    "3mo": "3 Bulan",
                    "6mo": "6 Bulan",
                    "1y": "1 Tahun",
                    "3y": "3 Tahun",
                    "5y": "5 Tahun",
                    "max": "Maksimum"
                }[x],
                index=3 # Default 1 Tahun
            )
        with col_t2:
            chart_interval = st.selectbox(
                "Interval Batang:",
                options=["1d", "1wk", "1mo"],
                format_func=lambda x: {
                    "1d": "Harian (Daily / D)",
                    "1wk": "Mingguan (Weekly)",
                    "1mo": "Bulanan (Monthly)"
                }[x],
                index=0
            )

        # Mengambil data historis
        hist = stock.history(period=time_period, interval=chart_interval)
        
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
            price_change = latest_price - prev_price
            percent_change = (price_change / prev_price) * 100 if prev_price != 0 else 0
            
            # Ringkasan Harga
            col1, col2 = st.columns(2)
            col1.metric("Harga Terakhir", f"Rp {latest_price:,.2f}", f"{price_change:+,.2f} ({percent_change:+.2f}%)")
            
            # --- MEMBUAT GRAFIK CANDLESTICK PROFESIONAL DENGAN PLOTLY ---
            fig = go.Figure(data=[go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Candlestick'
            )])
            
            # Menambahkan Indikator Moving Average (MA 20 & MA 50) ke Grafik
            if len(hist) >= 20:
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], mode='lines', name='MA 20', line=dict(color='orange', width=1.5)))
            
            if len(hist) >= 50:
                hist['MA50'] = hist['Close'].rolling(window=50).mean()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], mode='lines', name='MA 50', line=dict(color='blue', width=1.5)))

            fig.update_layout(
                title=f"Grafik Harga {ticker_symbol.upper()}",
                xaxis_title="Tanggal",
                yaxis_title="Harga (Rp)",
                xaxis_rangeslider_visible=False,
                height=450,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            
            # Tampilkan Grafik Interaktif
            st.plotly_chart(fig, use_container_width=True)
            
            # --- KOTAK REKOMENDASI BUY / SELL ---
            st.markdown("### 🤖 Rekomendasi Sinyal")
            if len(hist) >= 20 and 'MA20' in hist.columns and 'MA50' in hist.columns:
                ma20_latest = hist['MA20'].iloc[-1]
                ma50_latest = hist['MA50'].iloc[-1]
                
                signal = "HOLD"
                signal_color = "orange"
                reason = "Harga bergerak konsolidasi / datar."
                
                if latest_price > ma20_latest and ma20_latest >= ma50_latest:
                    signal = "BUY (Beli)"
                    signal_color = "green"
                    reason = "Tren Bullish: Harga di atas indikator rata-rata pergerakan."
                elif latest_price < ma20_latest and ma20_latest <= ma50_latest:
                    signal = "SELL (Jual)"
                    signal_color = "red"
                    reason = "Tren Bearish: Harga di bawah indikator rata-rata pergerakan."
                
                st.markdown(f"**Status Sinyal:** <span style='color:{signal_color}; font-size:18px; font-weight:bold;'>{signal}</span>", unsafe_allow_html=True)
                st.info(f"💡 **Analisis:** {reason}")
            else:
                st.warning("⚠️ Data belum cukup untuk kalkulasi indikator teknikal.")
                
        else:
            st.warning("⚠️ Data untuk rentang waktu tersebut tidak tersedia.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

st.divider()

# --- BAGIAN 2: DAFTAR PANTAU (WATCHLIST) DI BAWAH ---
st.subheader("📋 Daftar Pantau (Watchlist)")
default_watchlist = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "MBMA.JK", "POLA.JK", "ESTI.JK"]

watchlist_input = st.text_area(
    "Edit Daftar Saham (pisahkan dengan koma):", 
    value=", ".join(default_watchlist)
)

watchlist = [s.strip().upper() for s in watchlist_input.split(",") if s.strip()]

if watchlist:
    watchlist_data = []
    for ticker in watchlist:
        try:
            s_obj = yf.Ticker(ticker)
            df_hist = s_obj.history(period="5d")
            if not df_hist.empty:
                l_price = df_hist['Close'].iloc[-1]
                p_price = df_hist['Close'].iloc[-2] if len(df_hist) > 1 else l_price
                chg = l_price - p_price
                pct_chg = (chg / p_price) * 100 if p_price != 0 else 0
                
                watchlist_data.append({
                    "Kode Saham": ticker,
                    "Harga Terakhir (Rp)": round(l_price, 2),
                    "Perubahan": round(chg, 2),
                    "Perubahan (%)": round(pct_chg, 2)
                })
        except Exception:
            continue
    
    if watchlist_data:
        df_watchlist = pd.DataFrame(watchlist_data)
        df_watchlist.insert(0, "No", range(1, len(df_watchlist) + 1))
        st.dataframe(df_watchlist, use_container_width=True, hide_index=True)
