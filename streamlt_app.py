import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

st.title("Simulador de Curva OTDR")
st.markdown("Ajusta los parámetros para generar una curva OTDR personalizada.")

# Parámetros
distancia = st.slider("Selecciona la distancia (km):", 1, 80, 20)
atenuacion_km_1310 = 0.35
atenuacion_km_1550 = 0.25

# Selector de longitud de onda
modo = st.radio("Selecciona longitud de onda:", ["1310 nm", "1550 nm"])
atenuacion_km = atenuacion_km_1310 if modo == "1310 nm" else atenuacion_km_1550

# Eventos en dB por distancia
atenuaciones_eventos_1310 = {4: 0.3, 12: 1.5, 18: 0.8}
atenuaciones_eventos_1550 = {4: 0.6, 12: 2.0, 18: 1.0}
atenuaciones_eventos = atenuaciones_eventos_1310 if modo == "1310 nm" else atenuaciones_eventos_1550

# Función para generar datos de curva
def generar_datos_curva(distancia, atenuacion_km, atenuaciones_eventos):
    pasos = distancia * 100
    x = np.linspace(0, distancia, pasos)
    y = np.zeros_like(x)
    eventos_aplicados = np.zeros_like(x)
    acumulado_eventos = 0

    for i, distancia_actual in enumerate(x):
        eventos_aplicados[i] = acumulado_eventos
        if int(distancia_actual) in atenuaciones_eventos:
            acumulado_eventos += atenuaciones_eventos[int(distancia_actual)]
        y[i] = -(atenuacion_km * distancia_actual + eventos_aplicados[i])

    return x, y

# Generar datos
x, y = generar_datos_curva(distancia, atenuacion_km, atenuaciones_eventos)

# Graficar curva
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, y, label="Curva OTDR", color="blue", linewidth=2)
ax.set_title(f"Curva OTDR Simulada - {modo}")
ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla de eventos
st.subheader("Tabla de eventos")

def generar_tabla(atenuacion_km_tabla):
    eventos_lista = sorted(atenuaciones_eventos.items())
    acumulado_eventos = 0
    tabla_datos = []
    mayor_index = -1
    mayor_atenuacion = 0

    for i, (dist, att) in enumerate(eventos_lista, start=1):
        acumulado_eventos += att
        atenuacion_acumulada = (atenuacion_km_tabla * dist) + acumulado_eventos
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": dist,
            "Atenuación del evento (dB)": att,
            "Atenuación acumulada (dB)": atenuacion_acumulada
        })
        if att > mayor_atenuacion:
            mayor_atenuacion = att
            mayor_index = i - 1

    # Agregar fila final: pérdida total si no hay evento en el último km
    atenuacion_total_final = (atenuacion_km_tabla * distancia) + sum(atenuaciones_eventos.values())
    tabla_datos.append({
        "Nro Evento": "—",
        "Distancia (km)": distancia,
        "Atenuación del evento (dB)": 0.00,
        "Atenuación acumulada (dB)": round(atenuacion_total_final, 2)
    })

    df_eventos = pd.DataFrame(tabla_datos)

    def resaltar_fila(x):
        estilos = []
        for i in range(len(x)):
            if i == mayor_index:
                estilos.append('background-color: #ffcccc')  # Evento más alto
            elif i == len(x) - 1:
                estilos.append('background-color: #ccffcc')  # Fila final
            else:
                estilos.append('')
        return estilos

    st.dataframe(
        df_eventos.style
        .apply(resaltar_fila, axis=0)
        .format({
            "Distancia (km)": "{:.2f}",
            "Atenuación del evento (dB)": "{:.2f}",
            "Atenuación acumulada (dB)": "{:.2f}"
        }),
        use_container_width=True
    )

# Mostrar tabla
generar_tabla(atenuacion_km)
