import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("💻 Simulador de Medición OTDR - Fibra Óptica")

# Selección de longitudes de onda
st.markdown("<h3 style='color:#1f4e79;'>📡 Seleccione longitudes de onda</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    onda_1310 = st.checkbox("1310 nm (0.35 dB/km)", value=True)
with col2:
    onda_1550 = st.checkbox("1550 nm (0.21 dB/km)", value=True)

if not (onda_1310 or onda_1550):
    st.warning("Seleccione al menos una longitud de onda para simular.")
    st.stop()

# Parámetros
st.markdown("<h3 style='color:#1f4e79;'>📏 Configuración de enlace</h3>", unsafe_allow_html=True)
distancia = st.slider("Distancia del tramo (km)", 1.0, 80.0, 24.0, step=1.0)

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

st.markdown("<h3 style='color:#1f4e79;'>🔧 Ajustar atenuación por evento de fusión</h3>", unsafe_allow_html=True)
atenuaciones_eventos = {}
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

def calcular_y(atenuacion_km):
    x = np.linspace(0, distancia, 1000)
    y = -atenuacion_km * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y[idx:] -= perdida
    return x, y

color_1310 = "#1f77b4"  # azul metalizado
color_1550 = "#2ca02c"  # verde

fig, ax = plt.subplots(figsize=(10, 5))

if onda_1310:
    x1310, y1310 = calcular_y(0.35)
    ax.plot(x1310, y1310, label="1310 nm (0.35 dB/km)", color=color_1310)
if onda_1550:
    x1550, y1550 = calcular_y(0.21)
    ax.plot(x1550, y1550, label="1550 nm (0.21 dB/km)", color=color_1550)

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()

st.pyplot(fig)

def generar_tabla(atenuacion_km_tabla):
    eventos_lista = sorted(atenuaciones_eventos.items())
    acumulado_eventos = 0
    tabla_datos = []
    mayor_index = -1
    mayor_atenuacion = 0

    for i, (dist, att) in enumerate(eventos_lista, start=1):
        acumulado_eventos += att
        atenuacion_acumulada = (atenuacion_km_tabla * dist) + acumulado_eventos
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": round(dist, 2),
            "Atenuación del evento (dB)": round(att, 2),
            "Atenuación acumulada (dB)": round(atenuacion_acumulada, 2)
        })
        if att > mayor_atenuacion:
            mayor_atenuacion = att
            mayor_index = i - 1

    if tabla_datos:
        df_eventos = pd.DataFrame(tabla_datos)

        def resaltar_fila(x):
            color = [''] * len(x)
            if mayor_index >= 0:
                color[mayor_index] = 'background-color: #ffcccc'
            return color

        st.dataframe(df_eventos.style.apply(resaltar_fila, axis=0))
    else:
        st.info("No hay eventos de fusión para mostrar en la tabla.")

# Mostrar tabla de eventos según selección o solo disponible
if onda_1310 and onda_1550:
    tabla_opcion = st.radio("Seleccione tabla de eventos a mostrar:", ("1310 nm", "1550 nm"))
    if tabla_opcion == "1310 nm":
        st.subheader("📋 Tabla de eventos 1310 nm")
        generar_tabla(0.35)
    else:
        st.subheader("📋 Tabla de eventos 1550 nm")
        generar_tabla(0.21)
elif onda_1310:
    st.subheader("📋 Tabla de eventos 1310 nm")
    generar_tabla(0.35)
elif onda_1550:
    st.subheader("📋 Tabla de eventos 1550 nm")
    generar_tabla(0.21)

# Cálculo presupuesto óptico y verificación (para 1310 y 1550 si están seleccionados)
def calcular_presupuesto(atenuacion_km):
    atenuacion_total = atenuacion_km * distancia + sum(atenuaciones_eventos.values())
    atenuacion_maxima_permitida = round((atenuacion_km * distancia) + (0.15 * eventos), 2)
    evento_supera_limite = next((p for p in atenuaciones_eventos.values() if p > 0.15), None)
    cumple_total = atenuacion_total <= atenuacion_maxima_permitida
    cumple_eventos = evento_supera_limite is None
    return atenuacion_total, atenuacion_maxima_permitida, cumple_total, cumple_eventos

st.markdown("<h3 style='color:#1f4e79;'>📊 Presupuesto Óptico</h3>", unsafe_allow_html=True)

if onda_1310:
    at_total_1310, at_max_1310, cumple_tot_1310, cumple_ev_1310 = calcular_presupuesto(0.35)
    st.markdown(f"**1310 nm:** {at_total_1310:.2f} dB / máximo permitido {at_max_1310:.2f} dB")
    if cumple_tot_1310 and cumple_ev_1310:
        st.success(f"✅ Enlace certificado para 1310 nm")
    else:
        st.error(f"❌ No certifica para 1310 nm")

if onda_1550:
    at_total_1550, at_max_1550, cumple_tot_1550, cumple_ev_1550 = calcular_presupuesto(0.21)
    st.markdown(f"**1550 nm:** {at_total_1550:.2f} dB / máximo permitido {at_max_1550:.2f} dB")
    if cumple_tot_1550 and cumple_ev_1550:
        st.success(f"✅ Enlace certificado para 1550 nm")
    else:
        st.error(f"❌ No certifica para 1550 nm")

