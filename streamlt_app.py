import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("💻 Simulador de Medición OTDR - Fibra Óptica")

color_azul = "#1E90FF"

# Estilos CSS para modificar color de barras y checkbox
st.markdown(f"""
<style>
    /* Cambiar color del slider (barra) */
    div[data-baseweb="slider"] > div > div > div > div > div {{
        background-color: {color_azul} !important;
    }}
    /* Cambiar color del checkbox cuando está seleccionado */
    div[data-baseweb="checkbox"] svg {{
        stroke: {color_azul} !important;
        fill: {color_azul} !important;
    }}
    /* Cambiar color label checkbox */
    label[data-testid="stCheckboxLabel"] {{
        color: {color_azul} !important;
        font-weight: bold;
    }}
    /* Cambiar color label slider */
    label[data-testid="stSliderLabel"] {{
        color: {color_azul} !important;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

# Distancia
st.markdown(f'<p style="color:{color_azul}; font-weight:bold;">📏 Distancia del tramo (km)</p>', unsafe_allow_html=True)
distancia = st.slider("", 1.0, 80.0, 14.0, step=1.0)

# Selección longitud de onda
st.markdown(f'<p style="color:{color_azul}; font-weight:bold;">📡 Selección de longitud de onda</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    onda_1310 = st.checkbox("1310 nm (0.35 dB/km)", value=True)
with col2:
    onda_1550 = st.checkbox("1550 nm (0.21 dB/km)", value=True)

if not (onda_1310 or onda_1550):
    st.warning("Seleccioná al menos una longitud de onda para mostrar la curva.")
    st.stop()

# Ajustar atenuación por evento
st.markdown(f'<p style="color:{color_azul}; font-weight:bold;">🔧 Ajustar atenuación por evento de fusión</p>', unsafe_allow_html=True)

eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

atenuaciones_eventos = {}
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Función para calcular total y máximo
def calcular_total_y_max(atenuacion_km):
    atenuacion_total = atenuacion_km * distancia + sum(atenuaciones_eventos.values())
    atenuacion_maxima_permitida = round((0.21 * distancia) + (0.15 * eventos), 2)
    return atenuacion_total, atenuacion_maxima_permitida

# Cálculos según selección
if onda_1310:
    atenuacion_total_1310, atenuacion_maxima_1310 = calcular_total_y_max(0.35)
if onda_1550:
    atenuacion_total_1550, atenuacion_maxima_1550 = calcular_total_y_max(0.21)

# Mostrar presupuesto óptico según selección
if onda_1310 and onda_1550:
    st.markdown(f"✅ **PRESUPUESTO ÓPTICO (1310 nm): {atenuacion_maxima_1310} dB**")
    st.markdown(f"✅ **PRESUPUESTO ÓPTICO (1550 nm): {atenuacion_maxima_1550} dB**")
elif onda_1310:
    st.markdown(f"✅ **PRESUPUESTO ÓPTICO (1310 nm): {atenuacion_maxima_1310} dB**")
elif onda_1550:
    st.markdown(f"✅ **PRESUPUESTO ÓPTICO (1550 nm): {atenuacion_maxima_1550} dB**")

# Simulación curvas OTDR
x = np.linspace(0, distancia, 1000)
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor("#ffffff")
ax.set_facecolor("#ffffff")

if onda_1310:
    y_1310 = -0.35 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1310[idx:] -= perdida
    ax.plot(x, y_1310, label="1310 nm", color="#0077be")  # azul metalizado

if onda_1550:
    y_1550 = -0.21 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1550[idx:] -= perdida
    ax.plot(x, y_1550, label="1550 nm", color="#228B22")  # verde bosque

# Etiquetas de atenuación en eventos (negro, sin líneas punteadas)
for punto, perdida in atenuaciones_eventos.items():
    y_pos = 0
    if onda_1550:
        idx = np.searchsorted(x, punto)
        y_pos = y_1550[idx]
    elif onda_1310:
        idx = np.searchsorted(x, punto)
        y_pos = y_1310[idx]
    ax.text(punto, y_pos, f"-{perdida:.2f} dB", color="black", rotation=90, va='bottom')

# Evento mayor con círculo
evento_mayor = max(atenuaciones_eventos.items(), key=lambda x: x[1]) if atenuaciones_eventos else None
if evento_mayor:
    mayor_distancia = evento_mayor[0]
    idx_mayor = np.searchsorted(x, mayor_distancia)
    if onda_1310:
        ax.plot(x[idx_mayor], y_1310[idx_mayor], 'o', color="#0077be", markersize=12, markerfacecolor='none', markeredgewidth=2)
    if onda_1550:
        ax.plot(x[idx_mayor], y_1550[idx_mayor], 'o', color="#228B22", markersize=12, markerfacecolor='none', markeredgewidth=2)

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla con dos decimales
eventos_lista = sorted(atenuaciones_eventos.items())
acumulado_eventos = 0
tabla_datos = []
mayor_atenuacion = evento_mayor[1] if evento_mayor else 0
mayor_index = -1

for i, (dist, att) in enumerate(eventos_lista, start=1):
    acumulado_eventos += att
    atenuacion_km_ref = 0.21 if onda_1550 else 0.35
    atenuacion_acumulada = (atenuacion_km_ref * dist) + acumulado_eventos
    tabla_datos.append({
        "Nro Evento": i,
        "Distancia (km)": round(dist, 2),
        "Atenuación del evento (dB)": round(att, 2),
        "Atenuación acumulada (dB)": round(atenuacion_acumulada, 2)
    })
    if att == mayor_atenuacion:
        mayor_index = i - 1

if tabla_datos:
    st.subheader("📋 Detalle de eventos de fusión y atenuación acumulada")
    df_eventos = pd.DataFrame(tabla_datos)

    def resaltar_fila(x):
        color = [''] * len(x)
        if mayor_index >= 0:
            color[mayor_index] = 'background-color: #ffcccc'
        return color

    st.dataframe(df_eventos.style.apply(resaltar_fila, axis=0).format("{:.2f}"))
else:
    st.info("No hay eventos de fusión para mostrar en la tabla.")

# Verificación certificación
if onda_1550:
    atenuacion_total = atenuacion_total_1550
    atenuacion_maxima_permitida = atenuacion_maxima_1550
else:
    atenuacion_total = atenuacion_total_1310
    atenuacion_maxima_permitida = atenuacion_maxima_1310

evento_supera_limite = next(((i+1, dist, att) for i, (dist, att) in enumerate(eventos_lista) if att > 0.15), None)
cumple_total = atenuacion_total <= atenuacion_maxima_permitida
cumple_eventos = evento_supera_limite is None

if cumple_total and cumple_eventos:
    st.success(f"✅ Atenuación Total: {atenuacion_total:.2f} dB (DENTRO del límite permitido)")
    st.markdown("### 🟢 ENLACE CERTIFICADO")
else:
    st.error(f"❌ Atenuación Total: {atenuacion_total:.2f} dB")
    st.markdown("### 🔴 NO CERTIFICA POR:")
    if not cumple_total:
        st.markdown(f"- 🔺 Atenuación total excede el máximo permitido de {atenuacion_maxima_permitida:.2f} dB")
    if not cumple_eventos:
        st.markdown(f"- 🔺 Evento N° {evento_supera_limite[0]} con {evento_supera_limite[2]:.2f} dB a los {evento_supera_limite[1]} km")

# Leyenda adicional
if atenuaciones_eventos:
    st.info(f"🔴 Evento con mayor atenuación: {mayor_atenuacion:.2f} dB a los {evento_mayor[0]} km")
