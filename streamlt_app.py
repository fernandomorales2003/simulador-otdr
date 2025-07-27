import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Simulación OTDR con Conector Inicial")

# --- Parámetros configurables ---
distancia_total_km = st.slider("📏 Distancia total del tramo (km)", 1.0, 80.0, 5.0, step=1.0)
atenuacion_por_km = st.slider("💡 Atenuación (dB/km)", 0.1, 1.0, 0.35, step=0.01)
ganancia_conector = st.slider("🔺 Pico reflectivo del conector (dB)", 0.5, 3.0, 1.0, step=0.1)
nivel_post_conector = st.slider("📉 Nivel luego del conector (dB)", -2.0, 0.0, -0.5, step=0.1)

# --- Puntos clave del conector inicial ---
distancia_pico_reflex = 0.005        # 5 metros (km)
distancia_fin_conector = 0.075       # 75 metros (km)

# --- Generar traza del conector ---
x_conector = np.array([
    0.0,
    distancia_pico_reflex,
    distancia_fin_conector
])
y_conector = np.array([
    0.0,
    ganancia_conector,
    nivel_post_conector
])

# --- Traza principal (fibra óptica) ---
x_fibra = np.linspace(distancia_fin_conector, distancia_total_km, 1000)
y_fibra = -atenuacion_por_km * x_fibra + nivel_post_conector

# --- Concatenar curva completa ---
x_total = np.concatenate([x_conector, x_fibra])
y_total = np.concatenate([y_conector, y_fibra])

# --- Gráfico ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_total, y_total, label="Curva OTDR", color="blue", linewidth=2)
ax.scatter(distancia_pico_reflex, ganancia_conector, color="red", s=100, label="Pico reflectivo")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de conector de fibra óptica al inicio")
ax.grid(True)
ax.legend()
ax.set_ylim(-5, 2)
ax.set_xlim(0, distancia_total_km)

st.pyplot(fig)


