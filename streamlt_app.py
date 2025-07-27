import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("💻 Simulador de Medición OTDR - Fibra Óptica")

# --- Selección longitudes de onda ---
st.markdown("### 📡 Seleccione longitud(es) de onda para la simulación:")
col1, col2 = st.columns(2)
with col1:
    onda_1310 = st.checkbox("1310 nm (0.35 dB/km)", value=True)
with col2:
    onda_1550 = st.checkbox("1550 nm (0.21 dB/km)", value=True)

if not (onda_1310 or onda_1550):
    st.warning("⚠️ Seleccione al menos una longitud de onda para continuar.")
    st.stop()

# Parámetros comunes
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 24.0, step=1.0)

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

# Estilo azul metalizado para cajas y sliders
azul_metal = "#3b5998"  # tono azul metalizado

st.markdown(f'<style>div.row-widget.stSlider > div{{color:{azul_metal};font-weight:bold;}}</style>', unsafe_allow_html=True)
st.markdown(f'<style>label, .css-1q1n0ol, .css-2trqyj {{color:{azul_metal}; font-weight:bold;}}</style>', unsafe_allow_html=True)

# Ajustes de atenuación por evento (editable por usuario)
st.markdown(f"<h3 style='color:{azul_metal}'>🔧 Ajustar atenuación por evento de fusión</h3>", unsafe_allow_html=True)

atenuaciones_eventos = {}
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Función para calcular total y máximo para una atenuación por km dada
def calcular_total_y_max(atenuacion_km):
    total_eventos = sum(atenuaciones_eventos.values())
    atenuacion_total = atenuacion_km * distancia + total_eventos
    atenuacion_maxima_permitida = round((atenuacion_km * distancia) + (0.15 * eventos), 2)
    return atenuacion_total, atenuacion_maxima_permitida

# Calcular resultados según selección
resultados = {}
if onda_1310:
    total_1310, max_1310 = calcular_total_y_max(0.35)
    resultados["1310"] = (total_1310, max_1310)
if onda_1550:
    total_1550, max_1550 = calcular_total_y_max(0.21)
    resultados["1550"] = (total_1550, max_1550)

# Gráfica
x = np.linspace(0, distancia, 1000)
fig, ax = plt.subplots(figsize=(10, 5))

if onda_1310:
    y_1310 = -0.35 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1310[idx:] -= perdida
    ax.plot(x, y_1310, label="Curva OTDR 1310 nm", color="blue")

if onda_1550:
    y_1550 = -0.21 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1550[idx:] -= perdida
    ax.plot(x, y_1550, label="Curva OTDR 1550 nm", color="green")

ax.set_xlabel("Distancia (km)", color=azul_metal)
ax.set_ylabel("Potencia (dB)", color=azul_metal)
ax.set_title("Simulación de traza OTDR", color=azul_metal)
ax.grid(True)
ax.legend()

st.pyplot(fig)

# Tabla con detalle de eventos, mostrando atenuación acumulada según cada onda seleccionada
tabla_datos = []
mayor_index = -1
mayor_atenuacion = 0

eventos_lista = sorted(atenuaciones_eventos.items())  # [(distancia, atenuacion), ...]

# Para cada evento, calculamos la atenuación acumulada para cada onda activa
for i, (dist, att) in enumerate(eventos_lista, start=1):
    # Para 1310
    acumulado_1310 = (0.35 * dist) + sum([a for d, a in eventos_lista[:i]])
    # Para 1550
    acumulado_1550 = (0.21 * dist) + sum([a for d, a in eventos_lista[:i]])

    # Elegir cuál mostrar en tabla según selección
    if onda_1310 and onda_1550:
        # Mostrar ambos en columnas separadas
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": round(dist, 2),
            "Atenuación evento (dB)": round(att, 2),
            "Atenuación acumulada 1310 (dB)": round(acumulado_1310, 2),
            "Atenuación acumulada 1550 (dB)": round(acumulado_1550, 2),
        })
    elif onda_1310:
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": round(dist, 2),
            "Atenuación evento (dB)": round(att, 2),
            "Atenuación acumulada (dB)": round(acumulado_1310, 2),
        })
    elif onda_1550:
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": round(dist, 2),
            "Atenuación evento (dB)": round(att, 2),
            "Atenuación acumulada (dB)": round(acumulado_1550, 2),
        })

    if att > mayor_atenuacion:
        mayor_atenuacion = att
        mayor_index = i - 1

if tabla_datos:
    st.subheader("📋 Detalle de eventos de fusión y atenuación acumulada")
    df_eventos = pd.DataFrame(tabla_datos)

    def resaltar_fila(x):
        color = [''] * len(x)
        if mayor_index >= 0:
            color[mayor_index] = 'background-color: #ffcccc'
        return color

    st.dataframe(df_eventos.style.apply(resaltar_fila, axis=0))
else:
    st.info("No hay eventos de fusión para mostrar en la tabla.")

# Verificación certificación para cada onda
for onda, (total, max_permitido) in resultados.items():
    cumple_total = total <= max_permitido
    evento_supera_limite = next(((i+1, dist, att) for i, (dist, att) in enumerate(eventos_lista) if att > 0.15), None)
    cumple_eventos = evento_supera_limite is None
    st.markdown(f"### Resultado para {onda} nm:")
    if cumple_total and cumple_eventos:
        st.success(f"✅ Atenuación Total: {total:.2f} dB (DENTRO del límite permitido)")
        st.markdown("🟢 ENLACE CERTIFICADO")
    else:
        st.error(f"❌ Atenuación Total: {total:.2f} dB")
        st.markdown("🔴 NO CERTIFICA POR:")
        if not cumple_total:
            st.markdown(f"- 🔺 Atenuación total excede el máximo permitido de {max_permitido:.2f} dB")
        if not cumple_eventos:
            st.markdown(f"- 🔺 Evento N° {evento_supera_limite[0]} con {evento_supera_limite[2]:.2f} dB a los {evento_supera_limite[1]} km")



