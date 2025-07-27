import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Simulación OTDR con Conectores y Ruido Final")

# --- Parámetros fijos ---
distancia_total_km = 5.0
atenuacion_por_km = 0.35
ganancia_conector = 0.80
nivel_post_conector = -0.25
agregar_conector_final = True

# --- Distancias clave ---
longitud_conector_km = 0.075
dist_pico_inicio = 0.005
dist_fin_conector = longitud_conector_km
espacio_extra = 0.2  # aumentamos para ver el ruido

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

# --- Fibra intermedia ---
if agregar_conector_final:
    dist_fibra = distancia_total_km - longitud_conector_km
else:
    dist_fibra = distancia_total_km

x_fibra = np.linspace(dist_fin_conector, dist_fibra, 1000)
y_fibra = -atenuacion_por_km * x_fibra + nivel_post_conector

# --- Conector final (igual al inicial pero invertido) ---
if agregar_conector_final:
    y_base_final = y_fibra[-1]
    x_final = np.array([
        dist_fibra + 0.005,
        dist_fibra + 0.010,
        distancia_total_km
    ])
    y_final = np.array([
        y_base_final,
        y_base_final + ganancia_conector,
        y_base_final - 0.5
    ])

    # --- Ruido posterior (zona muerta o ruido electrónico) ---
    x_ruido = np.linspace(distancia_total_km, distancia_total_km + espacio_extra, 300)
    ruido = np.random.normal(loc=y_final[-1], scale=0.15, size=len(x_ruido))
    
    # Combinar todo
    x_total = np.concatenate([x_inicio, x_fibra, x_final, x_ruido])
    y_total = np.concatenate([y_inicio, y_fibra, y_final, ruido])
else:
    x_total = np.concatenate([x_inicio, x_fibra])
    y_total = np.concatenate([y_inicio, y_fibra])

# --- Gráfico OTDR ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_total, y_total, label="Curva OTDR", color="blue", linewidth=2)
ax.scatter(dist_pico_inicio, ganancia_conector, color="red", s=100, label="Conector inicial")

if agregar_conector_final:
    ax.scatter(dist_fibra + 0.010, y_final[1], color="orange", s=100, label="Conector final")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de OTDR con Conectores y Ruido Final")
ax.grid(True)
ax.legend()
ax.set_ylim(-5, 2)
ax.set_xlim(0, distancia_total_km + espacio_extra)
st.pyplot(fig)
