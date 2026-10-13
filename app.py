import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman Web
st.set_page_config(page_title="Pantau Saham Emiten", page_icon="📈", layout="centered")

st.title("📈 Aplikasi Pemantau Emiten Saham")
st.write("Pantau pergerakan harga saham emiten pilihan Anda secara langsung.")

# --- BAGIAN 1: DETAIL SAHAM & GRAFIK (DENGAN REKOMENDASI DI DALAMNYA) ---
st.subheader("🔍 Detail & Grafik Pergerakan Saham")
default_ticker = "BBCA.JK"
ticker_symbol = st.text_input("Masukkan Kode Saham:", value=default_ticker)

if ticker_symbol:
    try:
        stock = yf.Ticker(ticker_symbol.strip().upper())
        
        # --- PILIHAN RENTANG WAKTU DI BAWAH GRAFIK / SETELAH INPUT SAHAM ---
        # Kita sediakan opsi lengkap termasuk detik/menit (intraday) dan jangka panjang
        time_option = st.selectbox(
            "Pilih Rentang Waktu Grafik:",
            options=["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "6mo", "1y", "3y", "5y", "max"],
            format_func=lambda x: {
                "1m": "1 Menit (Intraday - 7 hari terakhir)",
                "2m": "2 Menit (Intraday)",
                "5m": "5 Menit (Intraday)",
                "15m": "15 Menit (Intraday)",
                "30m": "30 Menit (Intraday)",
                "1h": "1 Jam (Intraday)",
                "1d": "1 Hari",
                "5d": "5 Hari",
                "1mo": "1 Bulan",
                "6mo": "6 Bulan",
                "1y": "1 Tahun",
                "3y": "3 Tahun",
                "5y": "5 Tahun",
                "max": "Maksimum / Semua Data"
            }[x],
            index=10 # Default ke 1 Tahun
        )

        # Menyesuaikan interval otomatis berdasarkan pilihan waktu agar grafik akurat
        interval_map = {
            "1m": "1m", "2m": "2m", "5m": "5m", "15m": "15m", 
            "30m": "30m", "1h": "60m", "1d": "1d", "5d": "1d", 
            "1mo": "1d", "6mo": "1wk", "1y": "1wk", "3y": "1mo", 
            "5y": "1mo", "max": "3mo"
        }
        
        selected_interval = interval_map.get(time_option, "1d")

        # Mengambil data historis dengan rentang dan interval yang dipilih
        hist = stock.history(period=time_option, interval=selected_interval)
        
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
            price_change = latest_price - prev_price
            percent_change = (price_change / prev_price) * 100 if prev_price != 0 else 0
            
            col1, col2 = st.columns(2)
            col1.metric("Harga Terakhir", f"Rp {latest_price:,.2f}", f"{price_change:+,.2f} ({percent_change:+.2f}%)")
            
            # Tampilkan Grafik
            st.line_chart(hist['Close'])
            
            # --- KOTAK REKOMENDASI BUY / SELL (MENYATU DI BAWAH GRAFIK) ---
            st.markdown("### 🤖 Analisis & Rekomendasi Sinyal")
            
            if len(hist) >= 20:
                hist['MA20'] = hist['Close'].rolling(window=min(20, len(hist))).mean()
                hist['MA50'] = hist['Close'].rolling(window=min(50, len(hist))).mean()
                
                ma20_latest = hist['MA20'].iloc[-1]
                ma50_latest = hist['MA50'].iloc[-1]
                
                signal = "HOLD"
                signal_color = "orange"
                reason = "Pergerakan harga terkonsolidasi (sideways)."
                
                if latest_price > ma20_latest and ma20_latest >= ma50_latest:
                    signal = "STRONG BUY / BUY"
                    signal_color = "green"
                    reason = "Tren Bullish: Harga berada di atas indikator rata-rata pergerakan."
                elif latest_price < ma20_latest and ma20_latest <= ma50_latest:
                    signal = "STRONG SELL / SELL"
                    signal_color = "red"
                    reason = "Tren Bearish: Harga berada di bawah indikator rata-rata pergerakan."
                
                st.markdown(f"**Rekomendasi:** <span style='color:{signal_color}; font-size:20px; font-weight:bold;'>{signal}</span>", unsafe_allow_html=True)
                st.info(f"💡 **Keterangan:** {reason}")
            else:
                st.warning("⚠️ Data belum cukup untuk kalkulasi indikator tren.")
                
        else:
            st.warning("⚠️ Data untuk rentang waktu atau kode saham tersebut tidak tersedia.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")

st.divider()

# --- BAGIAN 2: DAFTAR PANTAU (WATCHLIST) DI BAWAH ---
st.subheader("📋 Daftar Pantau (Watchlist)")
st.write("Daftar emiten pilihan yang dipantau secara berkala:")

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
    else:
        st.warning("⚠️ Tidak dapat memuat data untuk daftar saham tersebut.")
