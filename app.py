import numpy as np
from scipy.interpolate import interp1d
import streamlit as st
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador Clínico Dinámico", layout="centered")

# Título y encabezado médico
st.title("👁️ Simulador Dinámico: Concentración de Conos vs. Visión")
st.write("Mueve la barra deslizante hacia la derecha para ir descubriendo y dibujando la curva de agudeza visual a medida que aumenta la densidad de receptores.")

# 1. Datos reales de referencia anatómica (CONCENTRACIÓN)
x_puntos_totales = np.array([5000, 15000, 40000, 80000, 150000])
y_puntos_totales = np.array([5, 15, 40, 70, 100])
zonas_totales = ["Periferia Lejana", "Periferia Media", "Mácula Externa", "Fóvea (Borde)", "Fóvea Central"]

# Crear el modelo matemático de fondo (interpolación)
modelo_vision = interp1d(x_puntos_totales, y_puntos_totales, kind='cubic', bounds_error=False, fill_value="extrapolate")

# --- PANEL INTERACTIVO ---
st.subheader("🎛️ Panel de Exploración Anatómica")

# Slider para seleccionar la concentración de conos (Inicia en el mínimo: 5,000)
concentracion_usuario = st.slider(
    label="Incrementa la Concentración de Conos del Paciente (células / mm²):",
    min_value=5000,
    max_value=150000,
    value=5000, 
    step=5000,
    format="%d"
)

# Calcular la agudeza visual actual (evitando que supere matemáticamente el 100%)
agudeza_calculada = float(np.clip(modelo_vision(concentracion_usuario), 0, 100))

# Mostrar los resultados clínicos en tarjetas llamativas (Métricas)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Concentración Actual", value=f"{concentracion_usuario:,} cél/mm²")
with col2:
    st.metric(label="Agudeza Visual Alcanzada", value=f"{agudeza_calculada:.1f} %")

# --- FILTRADO EN TIEMPO REAL (El efecto de dibujado) ---
# Generamos la línea suave únicamente HASTA el valor que el usuario ha seleccionado
x_suave_dinamica = np.linspace(5000, concentracion_usuario, max(2, int((concentracion_usuario - 5000) / 500)))
y_suave_dinamica = np.clip(modelo_vision(x_suave_dinamica), 0, 100)

# Filtramos las zonas anatómicas para que solo aparezcan en la gráfica si ya las "descubrimos"
mascara_puntos = x_puntos_totales <= concentracion_usuario
x_puntos_visibles = x_puntos_totales[mascara_puntos]
y_puntos_visibles = y_puntos_totales[mascara_puntos]
zonas_visibles = [zonas_totales[i] for i, visible in enumerate(mascara_puntos) if visible]

# --- CONSTRUCCIÓN DEL GRÁFICO DINÁMICO ---
fig = go.Figure()

# 1. Línea de tendencia que crece con el slider
if concentracion_usuario > 5000:
    fig.add_trace(go.Scatter(
        x=x_suave_dinamica, y=y_suave_dinamica,
        mode='lines',
        name='Curva Revelada',
        line=dict(color='#0077b6', width=3),
        hoverinfo='skip'
    ))

# 2. Puntos anatómicos reales de referencia que se van encendiendo
if len(x_puntos_visibles) > 0:
    fig.add_trace(go.Scatter(
        x=x_puntos_visibles, y=y_puntos_visibles,
        mode='markers',
        name='Zonas Descubiertas',
        marker=dict(color='#2b2d42', size=10, symbol='circle'),
        text=zonas_visibles,
        hovertemplate="<b>%{text}</b><br>Concentración: %{x:,} cél/mm²<br>Agudeza: %{y}%<extra></extra>"
    ))

# 3. El marcador del "Paciente Simulado" (El diamante que va al frente dibujando la línea)
fig.add_trace(go.Scatter(
    x=[concentracion_usuario],
    y=[agudeza_calculada],
    mode='markers+text',
    name='Posición Actual',
    marker=dict(color='#e63946', size=16, symbol='diamond'),
    text=[f"Punto Actual ({agudeza_calculada:.1f}%)"],
    textposition="top left",
    hovertemplate="<b>Exploración</b><br>Concentración: %{x:,} cél/mm²<br>Agudeza: %{y:.1f}%<extra></extra>"
))

# Configuración estética fija (Los límites no se mueven para que no maree al alumno)
fig.update_layout(
    xaxis_title="Variable Independiente (X): Concentración de Conos (células / mm²)",
    yaxis_title="Variable Dependiente (Y): Agudeza Visual (%)",
    xaxis=dict(range=[-5000, 160000], tickformat=","),
    yaxis=dict(range=[-5, 115]),
    hovermode="closest",
    template="plotly_white",
    showlegend=False
)

# Enviar el gráfico dinámico a Streamlit
st.plotly_chart(fig, use_container_width=True)
