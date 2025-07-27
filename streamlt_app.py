import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("🖥️ Simulador de Medición OTDR - Fibra Óptica")

# Selección de longitud de onda
st.subheader("⚙️ Seleccioná la longitud de onda")
longitud_onda = st.selectbox(
    "Elegí la longitud de onda:",
    options=["1550 nm (0.21 dB/km)", "1310 nm (0.35 dB/km)"]
)

# Definir atenuación por km según selección
if longitud_onda.startswith("1310"):
    atenuacion_km = 0.35
else:
    atenuacion_km = 0.21

st.markdown(f"**Atenuación por km seleccionada:** {atenuacion_km} dB/km")

# Parámetros
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 24.0, step=1.0)

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

# Ajustes de atenuación por evento (editable por usuario)
atenuaciones_eventos = {}
st.subheader("🔧 Ajustar atenuación por evento de fusión")
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Cálculo total de atenuación
atenuacion_total = atenuacion_km * distancia + sum(atenuaciones_eventos.values())

# Mostrar valor de atenuación máxima permitida
atenuacion_maxima_permitida = round((atenuacion_km * distancia) + (0.15 * eventos), 2)
st.markdown(f"✅ **Atenuación máxima permitida:** {atenuacion_maxima_permitida} dB")

# Mostrar evento más atenuado
if atenuaciones_eventos:
    evento_mayor = max(atenuaciones_eventos.items(), key=lambda x: x[1])
    mayor_distancia = evento_mayor[0]
    mayor_atenuacion = evento_mayor[1]
    st.markdown(f"🔍 **Evento con mayor atenuación:** {mayor_atenuacion:.2f} dB a los {mayor_distancia} km")
else:
    mayor_distancia = None
    mayor_atenuacion = None
    st.markdown("🔍 No hay eventos de fusión para mostrar.")

# Simulación de curva OTDR
x = np.linspace(0, distancia, 1000)
y = -atenuacion_km * x

# Agregar eventos con caída
for punto, perdida in atenuaciones_eventos.items():
    idx = np.searchsorted(x, punto)
    y[idx:] -= perdida

# Graficar curva OTDR con círculo en evento mayor
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, y, label="Curva OTDR")
ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)

for punto, perdida in atenuaciones_eventos.items():
    ax.axvline(punto, color='red', linestyle='--')
    ax.text(punto, y[np.searchsorted(x, punto)], f"-{perdida:.2f} dB", color="red", rotation=90, va='bottom')

# Marca círculo rojo en evento mayor
if mayor_distancia is not None:
    idx_mayor = np.searchsorted(x, mayor_distancia)
    ax.plot(x[idx_mayor], y[idx_mayor], 'o', color='red', markersize=12, markerfacecolor='none', markeredgewidth=2)

st.pyplot(fig)

# Tabla con detalle de eventos
eventos_lista = sorted(atenuaciones_eventos.items())  # [(distancia, atenuacion), ...]
acumulado_eventos = 0
tabla_datos = []
mayor_index = -1

for i, (dist, att) in enumerate(eventos_lista, start=1):
    acumulado_eventos += att
    atenuacion_acumulada = (atenuacion_km * dist) + acumulado_eventos
    tabla_datos.append({
        "Nro Evento": i,
        "Distancia (km)": round(dist, 2),
        "Atenuación del evento (dB)": round(att, 2),
        "Atenuación acumulada (dB)": round(atenuacion_acumulada, 2)
    })
    if att == mayor_atenuacion:
        mayor_index = i - 1  # para resaltar fila

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

# Verificación de certificación
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
    st.info(f"🔴 Evento con mayor atenuación: {mayor_atenuacion:.2f} dB a los {mayor_distancia} km")
