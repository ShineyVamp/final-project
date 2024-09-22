import streamlit as st
import pandas as pd
import seaborn as sns
import folium
import matplotlib.pyplot as plt
from streamlit_folium import folium_static

#fungsi untuk membuat dataframe harian
def create_daily_air_quality_df(df):
    daily_air_quality_df = df.resample(rule='D', on='date').agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "SO2": "mean",
        "NO2": "mean",
        "CO": "mean",
        "O3": "mean",
        "RAIN": "mean"
    }).reset_index()
    return daily_air_quality_df

gabungan_data = pd.read_csv('gabungan.csv', parse_dates=['date'])
dongsi_data = pd.read_csv('dongsi.csv', parse_dates=['date'])
changping_data = pd.read_csv('changping.csv', parse_dates=['date'])

#buat dataframe harian
dongsi_hari_df = create_daily_air_quality_df(dongsi_data)
changping_hari_df = create_daily_air_quality_df(changping_data)

#membuat tren tahunan dan per jam
dongsi_tahun_trend = dongsi_data.groupby(dongsi_data['date'].dt.year)[['PM2.5', 'PM10']].mean().reset_index()
changping_tahun_trend = changping_data.groupby(changping_data['date'].dt.year)[['PM2.5', 'PM10']].mean().reset_index()

dongsi_jam_trend = dongsi_data.groupby(dongsi_data['date'].dt.hour)[['PM2.5', 'PM10', 'SO2', 'NO2']].mean().reset_index()
changping_jam_trend = changping_data.groupby(changping_data['date'].dt.hour)[['PM2.5', 'PM10', 'SO2', 'NO2']].mean().reset_index()


#sidebar untuk navigasi menggunakan radio button
st.sidebar.title("Air Quality Dashboard untuk daerah pada stasiun Dongsi dan Changping")
section = st.sidebar.radio("Pilih analisis", ['Tren Tahunan', 'Tren Per-Jam', 'Analisis Korelasi', 'Geospatial Distribution'])

#bagian 1: yearly trend menggunakan line chart
if section == 'Tren Tahunan':
    st.subheader('Tren tahunan PM2.5 dan PM10')

    col1, col2 = st.columns([3, 1])

    #line chart untuk songsi station
    with col1:
        st.write('### Dongsi Station')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dongsi_tahun_trend['date'], dongsi_tahun_trend['PM2.5'], label='PM2.5', marker='o')
        ax.plot(dongsi_tahun_trend['date'], dongsi_tahun_trend['PM10'], label='PM10', marker='o')
        ax.set_title('Tren tahunan - Dongsi Station')
        ax.set_xlabel('Tahun')
        ax.set_ylabel('Konsentrasi polutan (µg/m³)')
        ax.legend()
        st.pyplot(fig)

    #line chart untuk changping station
    col3, col4 = st.columns([3, 1])

    with col3:
        st.write('### Changping Station')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(changping_tahun_trend['date'], changping_tahun_trend['PM2.5'], label='PM2.5', marker='o')
        ax.plot(changping_tahun_trend['date'], changping_tahun_trend['PM10'], label='PM10', marker='o')
        ax.set_title('Yearly Trend - Changping Station')
        ax.set_xlabel('Year')
        ax.set_ylabel('Konsentrasi polutan (µg/m³)')
        ax.legend()
        st.pyplot(fig)

#bagian 2: hourly trend
elif section == 'Tren Per-Jam':
    st.subheader('Rata rata PM2.5 dan PM10 pada setiap jam')

    col1, col2 = st.columns(2)

    #heatmap untuk dongsi station
    with col1:
        st.write('### Dongsi Station')
        dongsi_pivot = dongsi_jam_trend.pivot_table(values='PM2.5', index='date', aggfunc='mean')
        fig, ax = plt.subplots()  
        sns.heatmap(dongsi_pivot, cmap="YlOrBr", ax=ax, cbar_kws={'label': 'PM2.5 (µg/m³)'})
        ax.set_title('PM2.5 Perjam - Dongsi')
        ax.set_ylabel('jam', fontsize=15)
        st.pyplot(fig)

    #heatmap untuk changping station
    with col2:
        st.write('### Changping Station')
        changping_pivot = changping_jam_trend.pivot_table(values='PM2.5', index='date', aggfunc='mean')
        fig, ax = plt.subplots()  
        sns.heatmap(changping_pivot, cmap="YlOrBr", ax=ax, cbar_kws={'label': 'PM2.5 (µg/m³)'})
        ax.set_title('PM2.5 perjam - Changping')
        ax.set_ylabel('jam', fontsize=15)
        st.pyplot(fig)
        
    st.write("")
    st.write("")
    
    #stacked bar chart untuk dongsi dan changping
    st.subheader('Rata rata beberapa polutan pada setiap jam')
    
    col3, col4 = st.columns(2)

    with col3:
        st.write('### Dongsi Station')
        st.bar_chart(dongsi_jam_trend.set_index('date')[['PM2.5', 'PM10', 'SO2', 'NO2']])

    with col4:
        st.write('### Changping Station')
        st.bar_chart(changping_jam_trend.set_index('date')[['PM2.5', 'PM10', 'SO2', 'NO2']])

#bagian 3: korelasi antara hujan dan polutan
elif section == 'Analisis Korelasi':
    st.subheader('Korelasi Antara Hujan dan Polutan (SO2, CO)')

    selected_station = st.sidebar.selectbox('Pilih Station untuk Analisis Korelasi', ['Dongsi', 'Changping'])

    if selected_station == 'Dongsi':
        dongsi_corr = dongsi_data[['RAIN', 'SO2', 'CO']].corr()

        st.write('### Korelasi Pada - Dongsi Station')
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(dongsi_corr, annot=True, cmap="coolwarm", center=0, ax=ax, cbar_kws={'label': 'Korelasi'})
        st.pyplot(fig)

    else:
        changping_corr = changping_data[['RAIN', 'SO2', 'CO']].corr()

        st.write('### Korelasi Pada - Changping Station')
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(changping_corr, annot=True, cmap="coolwarm", center=0, ax=ax, cbar_kws={'label': 'Korelasi'})
        st.pyplot(fig)

#bagian 4: geospatial analysis
elif section == 'Geospatial Distribution':
    st.subheader('Geospatial Distribution dari PM2.5 dan PM10 di daerah Urban(dongsi) vs Suburban(changping)')

    #koordinat untuk dongsi dan changping
    dongsi_coords = [39.929, 116.417]
    changping_coords = [40.218, 116.231]

    #rata-rata polusi untuk marker di peta
    changping_mean = changping_data[['PM2.5', 'PM10']].mean()
    dongsi_mean = dongsi_data[['PM2.5', 'PM10']].mean()

    # Membuat peta menggunakan Folium
    m = folium.Map(location=[40.06, 116.2], zoom_start=10)

    #menambahkan marker untuk dongsi
    folium.CircleMarker(
        location=dongsi_coords,
        radius=20,
        popup=f"Dongsi<br>PM2.5: {dongsi_mean['PM2.5']:.0f}<br>PM10: {dongsi_mean['PM10']:.0f}",
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.7
    ).add_to(m)
    #menambahkan marker untuk changping
    folium.CircleMarker(
        location=changping_coords,
        radius=20,
        popup=f"Changping<br>PM2.5: {changping_mean['PM2.5']:.0f}<br>PM10: {changping_mean['PM10']:.0f}",
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.7
    ).add_to(m)

    #enampilkan peta menggunakan folium
    folium_static(m)

    #menambahkan visualisasi boxplot untuk distribusi PM2.5 dan PM10
    st.subheader('Distribusi PM2.5 dan PM10 di daerah Urban(dongsi) vs Suburban(changping)')

    #menggabungkan data harian dari dongsi dan changping
    combined_data = pd.concat([dongsi_hari_df.assign(Station='Dongsi'), changping_hari_df.assign(Station='Changping')])

    #membuat dua kolom untuk boxplot PM2.5 dan PM10
    col1, col2 = st.columns(2)

    #boxplot untuk PM2.5 di kolom pertama
    with col1:
        st.write('### Distribusi PM2.5')
        fig, ax = plt.subplots(figsize=(6, 6))
        sns.boxplot(data=combined_data, x='Station', y='PM2.5', ax=ax)
        ax.set_title('PM2.5 Distribusi berdasarkan Station')
        ax.set_xlabel('Station')
        ax.set_ylabel('PM2.5 (µg/m³)')
        st.pyplot(fig)

    #boxplot untuk PM10 di kolom kedua
    with col2:
        st.write('###  Distribusi PM10 ')
        fig, ax = plt.subplots(figsize=(6, 6))
        sns.boxplot(data=combined_data, x='Station', y='PM10', ax=ax)
        ax.set_title('PM10 Distribusi berdasarkan Station')
        ax.set_xlabel('Station')
        ax.set_ylabel('PM10 (µg/m³)')
        st.pyplot(fig)


