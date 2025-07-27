import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="centered")
st.title("Simulación de Curva OTDR")

# Estilo
st.markdown("""
    <style>
        .main { background-color: #f7f7f7; }
        .stSlider > div > div { color: #1f5c99; }
        label { color: #1f5c99 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Parámetros de entrada
distancia_total = st.slider("Distancia total (km)", 1, 80, 10)
fusion_check = st.checkbox("Ajustar atenuación por evento de fusión (0.1 dB/evento)", value=True)
mostrar_1310 = st.checkbox("Longitud de onda 1310 nm", value=True)
mostrar_1550 = st.checkbox("Longitud de onda 1550 nm", value=False)
ver_tabla = st.checkbox("Mostrar tabla de eventos", value=True)
tabla_1310 = st.radio("Mostrar tabla para:", options=["1310", "1550"], horizontal=True)

# Variables
num_eventos = distancia_total - 1
pérdida_por_km = {"1310": 0.35, "1550": 0.20}
atenuaciones = {"1310": [], "1550": []}
acumulada = {"1310": [], "1550": []}

# Eventos
eventos = []
# Evento inicial (conector)
eventos.append({
    "Ubicación (km)": 0.00,
    "Tipo": "Conector",
    "Atenuación (dB)": 0.25,
    "Reflexión (dB)": -60
})

for i in range(1, distancia_total):
    tipo = "Fusión" if fusion_check else "Empalme"
    atenuacion_evento = 0.1 if fusion_check else 0.2
    eventos.append({
        "Ubicación (km)": float(i),
        "Tipo": tipo,
        "Atenuación (dB)": atenuacion_evento,
        "Reflexión (dB)": np.nan
    })

# Evento final (conector)
eventos.append({
    "Ubicación (km)": float(distancia_total),
    "Tipo": "Conector",
    "Atenuación (dB)": 0.25,
    "Reflexión (dB)": -60
})

# Cálculo de atenuación acumulada
for onda in ["1310", "1550"]:
    at_total = 0
    for e in eventos:
        km = e["Ubicación (km)"]
        if eventos.index(e) == 0:
            at_evento = e["Atenuación (dB)"]
        else:
            tramo = km - eventos[eventos.index(e)-1]["Ubicación (km)"]
            at_evento = tramo * pérdida_por_km[onda] + e["Atenuación (dB)"]
        at_total += at_evento
        atenuaciones[onda].append(round(at_evento, 2))
        acumulada[onda].append(round(at_total, 2))

# Gráfico
fig, ax = plt.subplots()
colores = {"1310": "blue", "1550": "green"}

for onda in ["1310", "1550"]:
    if (onda == "1310" and mostrar_1310) or (onda == "1550" and mostrar_1550):
        x = [e["Ubicación (km)"] for e in eventos]
        y = [-v for v in acumulada[onda]]
        ax.plot(x, y, label=f"{onda} nm", color=colores[onda])

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Presupuesto óptico
st.subheader("Presupuesto Óptico")
if mostrar_1310:
    st.write(f"🟦 1310 nm: **{acumulada['1310'][-1] + 1:.2f} dB**")
if mostrar_1550:
    st.write(f"🟩 1550 nm: **{acumulada['1550'][-1] + 1:.2f} dB**")

# Tabla de eventos
if ver_tabla:
    if tabla_1310 == "1310":
        df = pd.DataFrame(eventos)
        df["Atenuación (dB)"] = atenuaciones["1310"]
        df["Atenuación Acumulada (dB)"] = acumulada["1310"]
    else:
        df = pd.DataFrame(eventos)
        df["Atenuación (dB)"] = atenuaciones["1550"]
        df["Atenuación Acumulada (dB)"] = acumulada["1550"]

    # Redondear
    df["Atenuación (dB)"] = df["Atenuación (dB)"].apply(lambda x: round(x, 2))
    df["Atenuación Acumulada (dB)"] = df["Atenuación Acumulada (dB)"].apply(lambda x: round(x, 2))

    st.dataframe(df.style.format(subset=["Atenuación (dB)", "Atenuación Acumulada (dB)"], precision=2), use_container_width=True)
