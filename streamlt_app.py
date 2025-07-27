import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("📡 Simulador de Medición OTDR - Fibra Óptica")

# Parámetros
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 24.0, step=1.0)

# Selección de longitud de onda
st.markdown("### 🎛️ Seleccione la(s) longitud(es) de onda para simular:")
check_1310 = st.checkbox("1310 nm (Atenuación 0.35 dB/km)", value=True)
check_1550 = st.checkbox("1550 nm (Atenuación 0.21 dB/km)", value=True)

if not (check_1310 or check_1550):
    st.warning("⚠️ Seleccione al menos una longitud de onda para continuar.")
    st.stop()

# Atenuaciones por km
atenuacion_1310 = 0.35
atenuacion_1550 = 0.21

# Generar eventos cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

st.subheader("🔧 Ajustar atenuación por evento de fusión")
atenuaciones_eventos = {}
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Presupuesto óptico (incluye conectores: 0.5 dB x 2)
presupuesto_1310 = round((atenuacion_1310 * distancia) + (0.15 * eventos) + 1.0, 2)
presupuesto_1550 = round((atenuacion_1550 * distancia) + (0.15 * eventos) + 1.0, 2)

st.markdown("### 🔆 Presupuesto Óptico")
if check_1310:
    st.markdown(f"- 1310 nm: {presupuesto_1310} dB")
if check_1550:
    st.markdown(f"- 1550 nm: {presupuesto_1550} dB")

def calcular_atenuacion_total(at_km):
    return at_km * distancia + sum(atenuaciones_eventos.values()) + 1.0

at_total_1310 = calcular_atenuacion_total(atenuacion_1310) if check_1310 else None
at_total_1550 = calcular_atenuacion_total(atenuacion_1550) if check_1550 else None

# Función para generar curva con conectores y ruido
def generar_curva_completa(at_km):
    x_ini = np.array([0.0, 0.005, 0.075])
    y_ini = np.array([0.0, 0.8, -0.25])

    x_fibra = np.linspace(0.075, distancia - 0.075, 1000)
    y_fibra = -at_km * x_fibra + y_ini[-1]
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x_fibra, punto)
        y_fibra[idx:] -= perdida

    y_fin_base = y_fibra[-1]
    x_fin = np.array([
        distancia - 0.075 + 0.005,
        distancia - 0.075 + 0.010,
        distancia
    ])
    y_fin = np.array([
        y_fin_base,
        y_fin_base + 0.8,
        y_fin_base - 0.5
    ])

    x_ruido = np.linspace(distancia, distancia + 0.1, 300)
    y_ruido = np.random.normal(loc=y_fin[-1], scale=0.15, size=len(x_ruido))

    x_total = np.concatenate([x_ini, x_fibra, x_fin, x_ruido])
    y_total = np.concatenate([y_ini, y_fibra, y_fin, y_ruido])
    return x_total, y_total

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
if check_1310:
    x_1310, y_1310 = generar_curva_completa(atenuacion_1310)
    ax.plot(x_1310, y_1310, label="1310 nm", color="blue")
if check_1550:
    x_1550, y_1550 = generar_curva_completa(atenuacion_1550)
    ax.plot(x_1550, y_1550, label="1550 nm", color="green")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla de eventos
def generar_tabla(at_km_tabla):
    eventos_lista = sorted(atenuaciones_eventos.items())
    acumulado_eventos = 0
    tabla_datos = []

    mayor_index = -1
    mayor_at = 0

    nro_evento = 1

    # Conector inicial
    acumulado_eventos += 0.5
    tabla_datos.append({
        "Nro Evento": nro_evento,
        "Distancia (km)": 0.00,
        "Atenuación del evento (dB)": 0.50,
        "Atenuación acumulada (dB)": acumulado_eventos
    })
    mayor_index = 0
    mayor_at = 0.5
    nro_evento += 1

    for dist, att in eventos_lista:
        acumulado_eventos += att
        at_acumulada = (at_km_tabla * dist) + acumulado_eventos
        tabla_datos.append({
            "Nro Evento": nro_evento,
            "Distancia (km)": dist,
            "Atenuación del evento (dB)": att,
            "Atenuación acumulada (dB)": at_acumulada
        })
        if att > mayor_at:
            mayor_at = att
            mayor_index = nro_evento - 1
        nro_evento += 1

    # Conector final
    acumulado_eventos += 0.5
    at_final = (at_km_tabla * distancia) + acumulado_eventos
    tabla_datos.append({
        "Nro Evento": nro_evento,
        "Distancia (km)": distancia,
        "Atenuación del evento (dB)": 0.50,
        "Atenuación acumulada (dB)": at_final
    })

    fila_total_index = len(tabla
