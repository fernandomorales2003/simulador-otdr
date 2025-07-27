import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("💻 Simulador de Medición OTDR - Fibra Óptica")

# Color azul metalizado para títulos importantes
color_azul = "#1E90FF"

# Estilo css para aplicar color azul metalizado en subtítulos (usamos markdown con estilo inline)
def titulo_azul(texto):
    return f'<p style="color:{color_azul}; font-weight:bold;">{texto}</p>'

# Título azul para distancia
st.markdown(titulo_azul("📏 Distancia del tramo (km)"), unsafe_allow_html=True)
distancia = st.slider("", 1.0, 80.0, 14.0, step=1.0)

# Título azul para selección de longitud de onda
st.markdown(titulo_azul("📡 Selección de longitud de onda"), unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    onda_1310 = st.checkbox("1310 nm (0.35 dB/km)", value=True)
with col2:
    onda_1550 = st.checkbox("1550 nm (0.21 dB/km)", value=True)

if not (onda_1310 or onda_1550):
    st.warning("Seleccioná al menos una longitud de onda para mostrar la curva.")
    st.stop()

# Título azul para ajustes de atenuación
st.markdown(titulo_azul("🔧 Ajustar atenuación por evento de fusión"), unsafe_allow_html=True)

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

# Ajustes de atenuación por evento (editable por usuario)
atenuaciones_eventos = {}
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Colores por defecto para gráfico
color_fondo_default = "#ffffff"
color_1310_default = "#0077be"  # azul metalizado un poco más oscuro
color_1550_default = "#228B22"  # verde bosque

# Botón para mostrar opciones de personalización
personalizar = st.checkbox("🔧 Personalizar gráfica")

if personalizar:
    st.markdown(titulo_azul("🎨 Configuración de colores"), unsafe_allow_html=True)
    color_fondo = st.color_picker("Color de fondo", color_fondo_default)
    color_1310 = st.color_picker("Color curva 1310 nm", color_1310_default)
    color_1550 = st.color_picker("Color curva 1550 nm", color_1550_default)
else:
    color_fondo = color_fondo_default
    color_1310 = color_1310_default
    color_1550 = color_1550_default

# Función para calcular total y máximo
def calcular_total_y_max(atenuacion_km):
    atenuacion_total = atenuacion_km * distancia + sum(atenuaciones_eventos.values())
    atenuacion_maxima_permitida = round((0.21 * distancia) + (0.15 * eventos), 2)
    return atenuacion_total, atenuacion_maxima_permitida

# Calcular para 1310 y 1550 si están activos
if onda_1310:
    atenuacion_total_1310, atenuacion_maxima_1310 = calcular_total_y_max(0.35)
if onda_1550:
    atenuacion_total_1550, atenuacion_maxima_1550 = calcular_total_y_max(0.21)

# Mostrar Presupuesto óptico con longitud de onda seleccionada
if onda_1550:
    texto_presupuesto = f"PRESUPUESTO ÓPTICO (1550 nm): {atenuacion_maxima_1550} dB"
else:
    texto_presupuesto = f"PRESUPUESTO ÓPTICO (1310 nm): {atenuacion_maxima_1310} dB"
st.markdown(f"✅ **{texto_presupuesto}**")

# Simulación curvas OTDR
x = np.linspace(0, distancia, 1000)
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(color_fondo)
ax.set_facecolor(color_fondo)

if onda_1310:
    y_1310 = -0.35 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1310[idx:] -= perdida
    ax.plot(x, y_1310, label="1310 nm", color=color_1310)

if onda_1550:
    y_1550 = -0.21 * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y_1550[idx:] -= perdida
    ax.plot(x, y_1550, label="1550 nm", color=color_1550)

# Texto de atenuación en eventos (negro, sin líneas punteadas)
for punto, perdida in atenuaciones_eventos.items():
    y_pos = 0
    if onda_1550:
        idx = np.searchsorted(x, punto)
        y_pos = y_1550[idx]
    elif onda_1310:
        idx = np.searchsorted(x, punto)
        y_pos = y_1310[idx]
    ax.text(punto, y_pos, f"-{perdida:.2f} dB", color="black", rotation=90, va='bottom')

# Marcar evento mayor con círculo
evento_mayor = max(atenuaciones_eventos.items(), key=lambda x: x[1]) if atenuaciones_eventos else None
if evento_mayor:
    mayor_distancia = evento_mayor[0]
    idx_mayor = np.searchsorted(x, mayor_distancia)
    if onda_1310:
        ax.plot(x[idx_mayor], y_1310[idx_mayor], 'o', color=color_1310, markersize=12, markerfacecolor='none', markeredgewidth=2)
    if onda_1550:
        ax.plot(x[idx_mayor], y_1550[idx_mayor], 'o', color=color_1550, markersize=12, markerfacecolor='none', markeredgewidth=2)

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
