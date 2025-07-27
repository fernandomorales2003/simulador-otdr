import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Simulación OTDR con Conectores")

# --- Parámetros generales ---
distancia_total_km = st.slider("📏 Distancia total del tramo (km)", 1.0, 80.0, 5.0, step=1.0)
atenuacion_por_km = st.slider("💡 Atenuación (dB/km)", 0.1, 1.0, 0.35, step=0.01)
ganancia_conector = st.slider("🔺 Pico reflectivo (dB)", 0.5, 3.0, 1.0, step=0.1)
nivel_post_conector = st.slider("📉 Nivel luego del conector (dB)", -2.0, 0.0, -0.5, step=0.1)
agregar_conector_final = st.checkbox("➕ Agregar conector al final", value=True)

# --- Distancias clave ---
dist_pico_inicio = 0.005      # 5 m
dist_fin_conector = 0.075     # 75 m
dist_pico_final = distancia_total_km - 0.005   # 5 m antes del final
dist_fin_final = distancia_total_km            # fin

# --- Conector inicial (pico y caída) ---
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

# --- Fibra principal ---
x_fibra = np.linspace(dist_fin_conector, dist_pico_final if agregar_conector_final else distancia_total_km, 1000)
y_fibra = -atenuacion_por_km * x_fibra + nivel_post_conector

# --- Conector final (opcional) ---
if agregar_conector_final:
    y_nivel_final = y_fibra[-1]  # último nivel antes del final
    x_final = np.array([
        dist_pico_final,
        dist_fin_final
    ])
    y_final = np.array([
        y_nivel_final + ganancia_conector,
        y_nivel_final
    ])
    x_total = np.concatenate([x_inicio, x_fibra, x_final])
    y_total = np.concatenate([y_inicio, y_fibra, y_final])
else:
    x_total = np.concatenate([x_inicio, x_fibra])
    y_total = np.concatenate([y_inicio, y_fibra])

# --- Gráfico OTDR ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_total, y_total, label="Curva OTDR", color="blue", linewidth=2)
ax.scatter(dist_pico_inicio, ganancia_conector, color="red", s=100, label="Conector inicial")

if agregar_conector_final:
    ax.scatter(dist_pico_final, y_total[-2], color="orange", s=100, label="Conector final")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de OTDR con Conectores Inicial y Final")
ax.grid(True)
ax.legend()
ax.set_ylim(-5, 2)
ax.set_xlim(0, distancia_total_km)
st.pyplot(fig)


