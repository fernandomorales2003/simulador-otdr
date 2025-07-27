import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Simulación OTDR con Conectores")

# --- Parámetros configurables ---
distancia_total_km = st.slider("📏 Distancia total del tramo (km)", 1.0, 80.0, 5.0, step=1.0)
atenuacion_por_km = st.slider("💡 Atenuación (dB/km)", 0.1, 1.0, 0.35, step=0.01)
ganancia_conector = st.slider("🔺 Pico reflectivo (dB)", 0.5, 3.0, 1.0, step=0.1)
nivel_post_conector = st.slider("📉 Nivel luego del conector (dB)", -2.0, 0.0, -0.5, step=0.1)
agregar_conector_final = st.checkbox("➕ Agregar conector al final", value=True)

# --- Distancias clave ---
espacio_extra = 0.1  # para visualizar mejor el pico final
dist_pico_inicio = 0.005
dist_fin_conector = 0.075
dist_pico_final = distancia_total_km - 0.005
dist_fin_final = distancia_total_km
dist_post_final = distancia_total_km + espacio_extra

# --- Conector inicial ---
x_inicio = np.array([
    0.0,
    dist_pico_inicio,
    dist_fin_conector
])
y_inicio = np.array([
    0.0,
    ganancia_conector,
    nivel_post_conector
])

# --- Fibra óptica (hasta justo antes del conector final) ---
x_fibra = np.linspace(dist_fin_conector, dist_pico_final if agregar_conector_final else distancia_total_km, 1000)
y_fibra = -atenuacion_por_km * x_fibra + nivel_post_conector

# --- Conector final + tramo plano final ---
if agregar_conector_final:
    y_nivel_final = y_fibra[-1]
    x_final = np.array([
        dist_pico_final,
        dist_fin_final,
        dist_post_final  # tramo extra para que se vea el reflejo
    ])
    y_final = np.array([
        y_nivel_final + ganancia_conector,
        y_nivel_final,
        y_nivel_final
    ])
    x_total = np.concatenate([x_inicio, x_fibra, x_final])
    y_total = np.concatenate([y_inicio, y_fibra, y_final])
else:
    x_total = np.concatenate([x_inicio, x_fibra])
    y_total = np.concatenate([y_inicio, y_fibra])

# --- Gráfico ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_total, y_total, label="Curva OTDR", color="blue", linewidth=2)
ax.scatter(dist_pico_inicio, ganancia_conector, color="red", s=100, label="Conector inicial")

if agregar_conector_final:
    ax.scatter(dist_pico_final, y_total[-3], color="orange", s=100, label="Conector final")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de OTDR con Conectores Inicial y Final")
ax.grid(True)
ax.legend()
ax.set_ylim(-5, 2)
ax.set_xlim(0, dist_post_final)
st.pyplot(fig)

