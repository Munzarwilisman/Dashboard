import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import pickle
import os

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard PLTU ANGGREK", layout="wide")

# Fungsi untuk menyimpan semua sheet sebagai dict
def save_data(sheet_dict):
    with open("uploaded_data.pkl", "wb") as f:
        pickle.dump(sheet_dict, f)

# Fungsi untuk memuat data dari file pickle
def load_data():
    if os.path.exists("uploaded_data.pkl"):
        with open("uploaded_data.pkl", "rb") as f:
            return pickle.load(f)
    return None

# Fungsi untuk menghapus file pickle
def clear_saved_data():
    if os.path.exists("uploaded_data.pkl"):
        os.remove("uploaded_data.pkl")
    for key in ["df", "sheet_names", "sheet_dict"]:
        st.session_state.pop(key, None)

# Load data saat aplikasi pertama kali dijalankan
if "df" not in st.session_state:
    loaded_data = load_data()
    if loaded_data is not None:
        st.session_state.sheet_dict = loaded_data
        st.session_state.sheet_names = list(loaded_data.keys())
        st.session_state.df = list(loaded_data.values())[0]

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Utama",
        options=["Home", "Performance Indikator", "Kesiapan Peralatan"],
        icons=["house", "bar-chart", "gear"],
        menu_icon="cast",
        default_index=0,
    )

    if st.button("🗑️ Hapus Semua Data"):
        clear_saved_data()
        st.success("Data berhasil dihapus. Silakan unggah ulang pada tab Performance Indikator.")

# Halaman Home
if selected == "Home":
    st.title("📈 Dashboard Parameter PLTU ANGGREK")
    st.markdown("Tampilan ringkas dari semua parameter dalam bentuk grafik tren.")

    if "df" not in st.session_state:
        st.warning("Silakan upload data terlebih dahulu melalui menu 'Performance Indikator'.")
        st.stop()

    df = st.session_state.df

    # Fitur Card untuk memilih sheet
    st.markdown("### 📑 Pilih Sheet yang Tersedia:")
    selected_sheet = st.selectbox(
        "Pilih Sheet:",
        st.session_state.sheet_names,
        key="sheet_select"
    )

    df = st.session_state.sheet_dict[selected_sheet]
    st.session_state.df = df

    date_column = None
    for col in df.columns:
        if pd.to_datetime(df[col], errors='coerce').notna().all():
            date_column = col
            df[date_column] = pd.to_datetime(df[date_column])
            df['Month'] = df[date_column].dt.strftime('%b %Y')
            break

    numerical_columns = df.select_dtypes(include='number').columns.tolist()

    st.markdown("### 📈 Grafik Tren Parameter")

    # Dropdown for selecting the type of chart
    chart_type = st.selectbox(
        "Pilih Jenis Grafik:",
        ["Line Chart", "Bar Chart", "Scatter Plot"],
        index=0,
    )

    for i in range(0, len(numerical_columns), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(numerical_columns):
                colname = numerical_columns[i + j]
                with cols[j]:
                    st.markdown(f"**{colname}**")
                    if date_column:
                        df_sorted = df.sort_values(by=date_column)
                        if chart_type == "Line Chart":
                            fig = px.line(df_sorted, x="Month", y=colname, title="", markers=True)
                        elif chart_type == "Bar Chart":
                            fig = px.bar(df_sorted, x="Month", y=colname, title="")
                        elif chart_type == "Scatter Plot":
                            fig = px.scatter(df_sorted, x="Month", y=colname, title="")
                    else:
                        if chart_type == "Line Chart":
                            fig = px.line(df, x=df.index, y=colname, title="", markers=True)
                        elif chart_type == "Bar Chart":
                            fig = px.bar(df, x=df.index, y=colname, title="")
                        elif chart_type == "Scatter Plot":
                            fig = px.scatter(df, x=df.index, y=colname, title="")

                    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
                    st.plotly_chart(fig, use_container_width=True)

# Halaman Performance Indikator
elif selected == "Performance Indikator":
    st.title("📊 Performance Indikator")

    uploaded_file = st.file_uploader("📄 Upload file data (CSV atau Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.session_state.sheet_dict = {"Sheet1": df}
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            sheet_dict = {name: pd.read_excel(xls, sheet_name=name) for name in sheet_names}
            st.session_state.sheet_dict = sheet_dict

        st.session_state.sheet_names = list(st.session_state.sheet_dict.keys())
        st.session_state.df = list(st.session_state.sheet_dict.values())[0]
        save_data(st.session_state.sheet_dict)
        st.success("✅ Data berhasil diunggah!")

    if "sheet_dict" not in st.session_state:
        st.info("Silakan upload file terlebih dahulu untuk menampilkan grafik.")
        st.stop()

    selected_sheet = st.radio("📄 Pilih Sheet:", st.session_state.sheet_names, horizontal=True)
    df = st.session_state.sheet_dict[selected_sheet]
    st.session_state.df = df

    st.markdown("---")
    st.subheader("📈 Dashboard Parameter")

    columns = df.select_dtypes(include=['number']).columns.tolist()
    param_cols = st.columns(len(columns))
    selected_param = st.session_state.get("selected_parameter", columns[0])

    st.session_state.selected_parameter = st.radio("Pilih Parameter:", columns, horizontal=True, index=columns.index(selected_param))
    selected_param = st.session_state.selected_parameter

    date_column = None
    for col in df.columns:
        if pd.to_datetime(df[col], errors='coerce').notna().all():
            date_column = col
            df[date_column] = pd.to_datetime(df[date_column])
            df['Month'] = df[date_column].dt.strftime('%b %Y')
            break

    st.markdown("---")
    st.markdown(f"### 🔍 Analisis Parameter: {selected_param}")

    mean = df[selected_param].mean()
    median = df[selected_param].median()
    std = df[selected_param].std()
    min_val = df[selected_param].min()
    max_val = df[selected_param].max()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Mean", f"{mean:.2f}")
    col2.metric("Median", f"{median:.2f}")
    col3.metric("Std Dev", f"{std:.2f}")
    col4.metric("Min", f"{min_val:.2f}")
    col5.metric("Max", f"{max_val:.2f}")

    st.markdown("### 📉 Grafik Tren")
    fig_line = px.line(df, x='Month' if date_column else df.index, y=selected_param)
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("### 📊 Histogram")
    fig_hist = px.histogram(df, x=selected_param)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### 📦 Box Plot")
    fig_box = px.box(df, y=selected_param)
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("### 🧠 Ringkasan AI Otomatis")
    trend_desc = ""
    if date_column:
        recent = df.sort_values(by=date_column).iloc[-5:]
        if recent[selected_param].is_monotonic_increasing:
            trend_desc = "Nilai parameter menunjukkan **tren meningkat** dalam beberapa waktu terakhir."
        elif recent[selected_param].is_monotonic_decreasing:
            trend_desc = "Nilai parameter menunjukkan **tren menurun** dalam beberapa waktu terakhir."
        else:
            trend_desc = "Nilai parameter menunjukkan **fluktuasi** dalam beberapa waktu terakhir."

    st.markdown(f"Rata-rata nilai **{selected_param}** adalah **{mean:.2f}**, dengan median **{median:.2f}**, standar deviasi **{std:.2f}**, nilai minimum **{min_val:.2f}**, dan maksimum **{max_val:.2f}**. {trend_desc}")

# Halaman Kesiapan Peralatan
elif selected == "Kesiapan Peralatan":
    st.title("🔧 Kesiapan Peralatan PLTU ANGGREK")
    st.markdown("Berikut adalah tampilan langsung dari Google Spreadsheet:")

    sheet_id = "1vh_3k_6uacjs96Bpr9ap_gQ-6T3CF-xQfFYt2AuSNvo"
    st.markdown(
        f"""
        <iframe src="https://docs.google.com/spreadsheets/d/{sheet_id}/embed" width="100%" height="600"></iframe>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"[📄 Buka Google Sheet di tab baru](https://docs.google.com/spreadsheets/d/{sheet_id}/edit)")
