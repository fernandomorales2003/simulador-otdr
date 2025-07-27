import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("💻 Simulador de Medición OTDR - Fibra Óptica")

# Parámetros
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 24.0, step=1.0)

col1, col2 = st.columns(2)
with col1:
    onda_1310 = st.checkbox("Longitud de onda 1310 nm (0.35 dB/km)", value=True)
with col2:
    onda_1550 = st.checkbox("Longitud de onda 1550 nm (0.21 dB/km)", value=True)

# Validar que al menos uno esté seleccionado
if not (onda_1310 or onda_1550):
    st.warning("Seleccioná al menos una longitud de onda para mostrar la curva.")
    st.stop()

# Atenuaciones por km según longitud de onda
atenuacion_1310 = 0.35
atenuacion_1550 = 0.21

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

# Ajustes de atenuación por evento (editable por usuario)
atenuaciones_eventos = {}
st.subheader("🔧 Ajustar atenuación por evento de fusión")
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Cálculos para cada longitud de onda
def calcular_total_y_max(atenuacion_km):
    atenuacion_total = atenuacion_km * distancia + sum(atenuaciones_eventos.values())
    atenuacion_maxima_permitida = round((0.21 * distancia) + (0.15 * eventos), 2)
    return atenuacion_total, atenuacion_maxima_permitida

# Calcular para 1310 y 1550 (solo si están seleccionados)
if onda_1310:
    atenuacion_total_1310, atenuacion_maxima_1310 = calcular_total_y_max(atenuacion_1310)
if onda_1550:
    atenuacion_total_1550, atenuacion_maxima_1550 = calcular_total_y_max(atenuacion_1550)

# Mostrar valor de atenuación máxima permitida (para 1550 por ser el más usado como referencia)
st.markdown(f"✅ **Atenuación máxima permitida (referencia 1550 nm):** {round((0.21 * distancia) + (0.15 * eventos), 2)} dB")

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

# Simulación de curvas OTDR
x = np.linspace(0, distancia, 1000)

fig, ax = plt.subplots(figsize=(10, 5))

if onda_1310:
    y_1310 = -atenuacion_1310 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1310[idx:] -= perdida
    ax.plot(x, y_1310, label="1310 nm (azul)", color="blue")

if onda_1550:
    y_1550 = -atenuacion_1550 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1550[idx:] -= perdida
    ax.plot(x, y_1550, label="1550 nm (verde)", color="green")

# Marcar eventos (líneas y texto)
for punto, perdida in atenuaciones_eventos.items():
    ax.axvline(punto, color='red', linestyle='--')
    # Mostrar atenuación evento en la curva 1550 si existe, sino en 1310
    y_pos = 0
    if onda_1550:
        idx = np.searchsorted(x, punto)
        y_pos = y_1550[idx]
    elif onda_1310:
        idx = np.searchsorted(x, punto)
        y_pos = y_1310[idx]
    ax.text(punto, y_pos, f"-{perdida:.2f} dB", color="red", rotation=90, va='bottom')

# Marca círculo rojo en evento mayor (en ambas curvas si están activas)
if mayor_distancia is not None:
    idx_mayor = np.searchsorted(x, mayor_distancia)
    if onda_1310:
        ax.plot(x[idx_mayor], y_1310[idx_mayor], 'o', color='blue', markersize=12, markerfacecolor='none', markeredgewidth=2)
    if onda_1550:
        ax.plot(x[idx_mayor], y_1550[idx_mayor], 'o', color='green', markersize=12, markerfacecolor='none', markeredgewidth=2)

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# Tabla con detalle de eventos
eventos_lista = sorted(atenuaciones_eventos.items())  # [(distancia, atenuacion), ...]
acumulado_eventos = 0
tabla_datos = []
mayor_index = -1

for i, (dist, att) in enumerate(eventos_lista, start=1):
    acumulado_eventos += att
    # Usamos atenuacion_km de 1550 como referencia para tabla y cálculo de acumulado
    atenuacion_km_ref = atenuacion_1550 if onda_1550 else atenuacion_1310
    atenuacion_acumulada = (atenuacion_km_ref * dist) + acumulado_eventos
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

# Verificación de certificación (usamos 1550 si está, si no 1310)
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
    st.info(f"🔴 Evento con mayor atenuación: {mayor_atenuacion:.2f} dB a los {mayor_distancia} km")
