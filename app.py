
import pandas as pd
import re
import regex
import emoji
import numpy as np
import demoji
from collections import Counter
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import streamlit as st
from PIL import Image










st.title('Análisis de un chat de whatsApp')
st.write('Creado por Carlos Antonio Torres')




ruta = r"C:\Users\carlo\OneDrive\Desktop\analisis mensajes con mi novia"



with open("_chat.txt", "r", encoding="utf-8") as file:
    lineas = file.readlines()


patron = r"\[(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2}:\d{2})\] (.*?): (.*)"

data = []

for lineas in lineas:
    match = re.match(patron, lineas)
    if match:
        fecha, hora, usuario, mensaje = match.groups()
        data.append([fecha, hora, usuario, mensaje])
    
df = pd.DataFrame(data, columns=["Fecha", "Hora", "Usuario", "Mensaje"])

df["Hora_dt"] = pd.to_datetime(df["Hora"], format="%H:%M:%S")
df["Hora_24"] = df["Hora_dt"].dt.hour
df["Horario"] = df["Hora_dt"].dt.strftime("%I %p").str.lstrip("0")
df = df[~df["Mensaje"].str.contains("end-to-end encrypted", na=False)]



st.title('¿Quién dice más “Te Amo”?')

df['te_amo'] = df['Mensaje'].str.lower().str.count(r'\bte amo\b')
te_amo_por_usuario = df.groupby('Usuario')['te_amo'].sum().reset_index()
te_amo_por_usuario = te_amo_por_usuario.sort_values(by='te_amo', ascending=False)
te_amo_por_usuario

import plotly.express as px
colores_rojos = ['#FF6666', '#FF3333', '#CC0000', '#990000']

fig = px.pie(
    te_amo_por_usuario,
    names='Usuario',       
    values='te_amo',       
    color='Usuario',       
    color_discrete_sequence=colores_rojos
)

fig.update_traces(textposition='inside', textinfo='percent+label', 
                  hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}')

fig.update_layout(title='Distribución interactiva de "te amo" por usuario')
st.plotly_chart(fig, use_container_width=True)



st.title('En que horario tenemos mas interaccion')
st.write('LAS 3 HORAS DONDE TENEMOS MAS INTERACCION')

mensajes_por_hora = df.groupby('Horario')[['Mensaje']].count()

mensajes_por_hora = mensajes_por_hora.rename(columns={'Hora_12' : 'Horario', 'Mensaje' : 'Cantidad'})
mensajes_por_hora = mensajes_por_hora.sort_values(by = "Cantidad", ascending=False)

top_3 = mensajes_por_hora.head(3)
top_3 = top_3.reset_index()
top_3


colores_rojos = ['#FF6666', '#FF3333', '#CC0000', '#990000']

fig = px.pie(
    top_3,
    names='Horario',       
    values='Cantidad',       
    color='Horario',       
    color_discrete_sequence=colores_rojos
)

fig.update_traces(textposition='inside', textinfo='percent+label', 
                  hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}')

fig.update_layout(title='Distribución interactiva de "te amo" por usuario')

st.plotly_chart(fig, use_container_width=True)



df['Palabras_usasdas_por_mensaje'] = df['Mensaje'].str.split().str.len()


st.title('Palabras que mas usamos en nuestro chat')

total_palabras = ' '
stopwords = STOPWORDS.update(['que', 'qué', 'con', 'de', 'te', 'en', 'la', 'lo', 'le', 'el', 'las', 'los', 'les', 
                              'por', 'es', 'son', 'se', 'para', 'un', 'una', 'chicos', 'su', 'si', 'chic','nos', 'ya', 
                              'hay', 'esta', 'pero', 'del', 'mas', 'más', 'eso', 'este', 'como', 'así', 'todo', 
                              'https','Media','omitted','y', 'mi', 'o', 'q', 'yo', 'al'])

mask = np.array(Image.open('heart.jpg'))


for mensaje in df['Mensaje'].values:
    palabras = str(mensaje).lower().split()
    for palabra in palabras:
        total_palabras += palabra + ' '


wordcloud = WordCloud(
    width=800,
    height=800,
    background_color='black',
    stopwords=stopwords,
    max_words=100,
    min_font_size=5,
    mask=mask,
    colormap='OrRd'
).generate(total_palabras)


imagen_wc = wordcloud.to_image()

st.image(imagen_wc, use_column_width=True)

import emoji

def ObtenerEmojis(texto):
    return [e['emoji'] for e in emoji.emoji_list(str(texto))]

# Crear columna nueva
df['Emoji_list'] = df['Mensaje'].apply(ObtenerEmojis)

grouped = df.groupby('Usuario').agg(
    Mensajes=('Mensaje', 'count'),
    Total_Emojis=('Emoji_list', lambda x: sum(len(i) for i in x)),
    Total_Palabras=('Palabras_usasdas_por_mensaje', 'sum'),
    Promedio_palabras=('Palabras_usasdas_por_mensaje', 'mean')
).reset_index()


st.title('Estadistica de nuestra conversacion')

total_mensajes = grouped['Mensajes'].sum()
grouped['%Mensajes'] = (grouped['Mensajes'] / total_mensajes) * 100
grouped['%Mensajes'] = grouped['%Mensajes'].round(2)

grouped

st.title('Emojis mas usados')

emojis_lista = list([a for b in df.Emoji_list for a in b])
emoji_diccionario = dict(Counter(emojis_lista))
emoji_diccionario = sorted(emoji_diccionario.items(), key=lambda x: x[1], reverse=True)


emoji_df = pd.DataFrame(emoji_diccionario, columns=['Emoji', 'Cantidad'])

emoji_df = pd.DataFrame(emoji_diccionario, columns=['Emoji', 'Cantidad'])

print('Número emojis únicos usados: ', len(emoji_df), '\n')
emoji_df

colores_rojos = ['#FF6666', '#FF3333', '#CC0000', '#990000']

fig = px.pie(
    emoji_df,
    names='Emoji',       
    values='Cantidad',       
    color='Emoji',       
    color_discrete_sequence=colores_rojos
)

fig.update_traces(textposition='inside', textinfo='percent+label', 
                  hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}')

fig.update_layout(title='Distribución interactiva de "te amo" por usuario')

st.plotly_chart(fig, use_container_width=True)

df['rangoHora'] = pd.to_datetime(df['Hora'], format='%H:%M:%S')


def create_range_hour(hour):
    hour = pd.to_datetime(hour)  
    start_hour = hour.hour
    end_hour = (hour + pd.Timedelta(hours=1)).hour
    return f'{start_hour:02d} - {end_hour:02d} h'


df['rangoHora'] = df['rangoHora'].apply(create_range_hour)
df = pd.DataFrame({
    'FECHA' : df['Fecha'],
    'usuario' : df['Usuario'],
    'HORA' : df['Horario'],
    'Rango Hora' : df['rangoHora']

})

st.title('Rango de horarios de nuestra conversacion')

df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')  
df['DiaSemana'] = df['FECHA'].dt.strftime('%A')
mapeo_dias_espanol = {'Monday': '1 Lunes','Tuesday': '2 Martes','Wednesday': '3 Miércoles','Thursday': '4 Jueves',
                      'Friday': '5 Viernes','Saturday': '6 Sábado','Sunday': '7 Domingo'}
df['DiaSemana'] = df['DiaSemana'].map(mapeo_dias_espanol)
df 



df['# Mensajes por hora'] = 1


mensajes_hora = df.groupby('Rango Hora').count().reset_index()


fig = px.line(mensajes_hora, x='Rango Hora', y='# Mensajes por hora', color_discrete_sequence=['salmon'], template='plotly_dark')


fig.update_layout(
    title={'text': 'Mensajes por hora', 'y':0.96, 'x':0.5, 'xanchor': 'center'},
    font=dict(size=17))
fig.update_traces(mode='markers+lines', marker=dict(size=10))
fig.update_xaxes(title_text='Rango de hora', tickangle=30)
fig.update_yaxes(title_text='# Mensajes')
st.plotly_chart(fig, use_container_width=True)



st.title('Los días en que más hablamos')


df['# Mensajes por día'] = 1

date_df = df.groupby('DiaSemana').count().reset_index()


fig = px.line(date_df, x='DiaSemana', y='# Mensajes por día', color_discrete_sequence=['salmon'], template='plotly_dark')


fig.update_layout(
    title={'text': 'Mensajes que tenemos por dia en la semana', 'y':0.96, 'x':0.5, 'xanchor': 'center'},
    font=dict(size=17))
fig.update_traces(mode='markers+lines', marker=dict(size=10))
fig.update_xaxes(title_text='Día', tickangle=30)
fig.update_yaxes(title_text='# Mensajes')
st.plotly_chart(fig, use_container_width=True)


st.title('Mensaje por dia')

df['# Mensajes por día'] = 1

date_df = df.groupby('FECHA')['# Mensajes por día'].sum().reset_index()

fig = px.line(
    date_df,
    x='FECHA',
    y='# Mensajes por día',
    color_discrete_sequence=['salmon'],
    template='plotly_dark',
    title='Mensajes por día '
)

st.plotly_chart(fig, use_container_width=True)





