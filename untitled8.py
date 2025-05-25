import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="OXXO Analytics Dashboard", layout="wide")

df = pd.read_csv("df_binary_train.csv")
df_numeric = pd.read_csv("df_train_numeric.csv")

color_mapping = {
    'A': 'darkgreen',
    'AB': 'green',
    'B': 'lime',
    'BC': 'lightgreen',
    'C': 'yellow',
    'CD': 'orange',
    'D': 'red'
}

MEXICO_MIN_LAT, MEXICO_MAX_LAT = 14.5, 32.7
MEXICO_MIN_LNG, MEXICO_MAX_LNG = -118.4, -86.7

with st.sidebar:
    st.title("Filtros")
    selected_level = st.selectbox("Nivel Socioeconómico", sorted(df['NIVELSOCIOECONOMICO_DES'].unique()))
    selected_entorno = st.selectbox("Entorno", sorted(df['ENTORNO_DES'].unique()))

st.title("🛒 OXXO Store Performance Dashboard")

st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Stores", len(df))
with col2:
    st.metric("Success Rate", f"{df['labelExito'].mean()*100:.1f}%")
with col3:
    st.metric("Avg Store Size", f"{df['MTS2VENTAS_NUM'].mean():.1f} m²")
with col4:
    st.metric("Avg Parking", f"{df['CAJONESESTACIONAMIENTO_NUM'].mean():.1f}")

st.markdown("---")

st.subheader("Store Characteristics")
row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    fig, ax = plt.subplots()
    ax.hist(df['MTS2VENTAS_NUM'], bins=20, color='lightblue', edgecolor='black')
    ax.set_title("Distribución del Tamaño de Tienda (m²)")
    st.pyplot(fig)
with row1_col2:
    fig, ax = plt.subplots()
    ax.hist(df['PUERTASREFRIG_NUM'], bins=10, color='green', edgecolor="black")
    ax.set_title("Distribución de Puertas de Refrigerador")
    st.pyplot(fig)
with row1_col3:
    fig, ax = plt.subplots()
    ax.hist(df['CAJONESESTACIONAMIENTO_NUM'], bins=10, color='salmon')
    ax.set_title("Distribución de Cajones de Estacionamiento")
    st.pyplot(fig)

st.subheader("Store Distribution by Category")
row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1:
    fig, ax = plt.subplots()
    sns.countplot(data=df, x='ENTORNO_DES', order=df['ENTORNO_DES'].value_counts().index)
    plt.xticks(rotation=45)
    st.pyplot(fig)
with row2_col2:
    fig, ax = plt.subplots()
    sns.countplot(data=df, x='SEGMENTO_MAESTRO_DESC', order=df['SEGMENTO_MAESTRO_DESC'].value_counts().index, palette="plasma")
    plt.xticks(rotation=45)
    st.pyplot(fig)
with row2_col3:
    fig, ax = plt.subplots()
    sns.countplot(data=df, x='NIVELSOCIOECONOMICO_DES', order=['A','AB','B','BC','C','CD','D'], palette=color_mapping.values())
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.subheader("Success Rate by Environment")
entornos = df['ENTORNO_DES'].unique()
cols = st.columns(3)
for i, entorno in enumerate(entornos):
    with cols[i%3]:
        subset = df[df['ENTORNO_DES'] == entorno]
        counts = subset['labelExito'].value_counts()
        fig, ax = plt.subplots()
        
        labels = counts.index.tolist()
        values = counts.values.tolist()
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'][:len(labels)])
        
        ax.set_title(f"{entorno}")
        st.pyplot(fig)

st.subheader("Geographical Distribution")
map_col1, map_col2 = st.columns(2)
with map_col1:
    mexico_map = folium.Map(location=[25.0, -101.5], zoom_start=7)
    for lat, lng, nivel in zip(df['LATITUD_NUM'], df['LONGITUD_NUM'], df['NIVELSOCIOECONOMICO_DES']):
        if (MEXICO_MIN_LAT <= lat <= MEXICO_MAX_LAT) and (MEXICO_MIN_LNG <= lng <= MEXICO_MAX_LNG):
            folium.CircleMarker(
                location=[lat, lng],
                radius=5,
                color=color_mapping.get(nivel, '#808080'),
                fill=True,
                popup=f"Nivel: {nivel}"
            ).add_to(mexico_map)
    st_folium(mexico_map, width=400, height=400)

with map_col2:
    mapa_exito = folium.Map(location=[25.0, -101.5], zoom_start=7)
    for lat, lng, exito in zip(df['LATITUD_NUM'], df['LONGITUD_NUM'], df['labelExito']):
        if (MEXICO_MIN_LAT <= lat <= MEXICO_MAX_LAT) and (MEXICO_MIN_LNG <= lng <= MEXICO_MAX_LNG):
            folium.CircleMarker(
                location=[lat, lng],
                radius=5,
                color='green' if exito == 1 else 'red',
                fill=True,
                popup=f"Éxito: {exito}"
            ).add_to(mapa_exito)
    st_folium(mapa_exito, width=400, height=400)
