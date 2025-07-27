import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración general
st.set_page_config(page_title="Simulador de Medición OTDR", layout="centered")

st.title("🖥️ Simulador de Medición OTDR")

st.subheader("Configuración de la medición")

# Selección de distancia
distancia = st.slider("📏 Distancia total (km)", min_value=1, max_value=80, value=10, step=1)

# Selección de longitud de onda
st.markdown("### Longitud de onda (seleccione una):")
col1, col2 = st.columns(2)
with col1:
    usar_1310 = st.checkbox("1310 nm (0.35 dB/km)", value=True)
with col2:
    usar_1550 = st.checkbox("1550 nm (0.21 dB/km)", value=False)

# Validar que al menos una longitud de onda esté seleccionada
if not usar_1310 and not usar_1550:
    st.warning("Por favor, seleccione al menos una longitud de onda para continuar.")
    st.stop()

# Atenuación por evento de fusión
atenuacion_evento = st.number_input("🔧 Ajustar atenuación por evento de fusión (dB)", min_value=0.0, max_value=1.0, value=0.1, step=0.01)

# Definir eventos simulados cada 4 km
eventos = list(range(4, distancia, 4))
eventos.append(distancia) if eventos[-1] != distancia else None

# Función para calcular eventos
def calcular_eventos(lambda_nm):
    if lambda_nm == 1310:
        atenuacion_km = 0.35
    else:
        atenuacion_km = 0.21

    datos = []
    acumulada = 0.0
    anterior = 0.0
    for i, punto in enumerate(eventos):
        tramo = punto - anterior
        perdida = tramo * atenuacion_km + (atenuacion_evento if i > 0 else 0)
        acumulada += perdida
        datos.append({
            "Evento (km)": punto,
            "Tramo (km)": tramo,
            "Atenuación (dB)": round(perdida, 2),
            "Atenuación Acumulada (dB)": round(acumulada, 2)
        })
        anterior = punto

    # Agregar pérdida del tramo final si la distancia no cae justo en un evento
    if eventos[-1] < distancia:
        tramo_final = distancia - eventos[-1]
        perdida_final = tramo_final * atenuacion_km
        acumulada += perdida_final
        datos.append({
            "Evento (km)": distancia,
            "Tramo (km)": tramo_final,
            "Atenuación (dB)": round(perdida_final, 2),
            "Atenuación Acumulada (dB)": round(acumulada, 2)
        })

    return pd.DataFrame(datos)

# Mostrar tabla según selección
st.subheader("📋 Tabla de eventos")
if usar_1310 and not usar_1550:
    st.markdown("**Longitud de onda: 1310 nm**")
    df = calcular_eventos(1310)
    st.dataframe(df, use_container_width=True)

elif usar_1550 and not usar_1310:
    st.markdown("**Longitud de onda: 1550 nm**")
    df = calcular_eventos(1550)
    st.dataframe(df, use_container_width=True)

else:
    st.info("Seleccione solo una longitud de onda para mostrar la tabla de eventos.")

# Mostrar presupuesto óptico
st.subheader("📉 Presupuesto Óptico Estimado")
if usar_1310:
    perdida_1310 = round(distancia * 0.35 + (len(eventos) - 1) * atenuacion_evento, 2)
    st.write(f"🔵 1310 nm: {perdida_1310} dB")
if usar_1550:
    perdida_1550 = round(distancia * 0.21 + (len(eventos) - 1) * atenuacion_evento, 2)
    st.write(f"🟢 1550 nm: {perdida_1550} dB")

# Gráfico
st.subheader("📈 Simulación de curva OTDR")

fig, ax = plt.subplots()
if usar_1310:
    df1310 = calcular_eventos(1310)
    ax.plot(df1310["Evento (km)"], df1310["Atenuación Acumulada (dB)"], color="blue", label="1310 nm", marker="o")
if usar_1550:
    df1550 = calcular_eventos(1550)
    ax.plot(df1550["Evento (km)"], df1550["Atenuación Acumulada (dB)"], color="green", label="1550 nm", marker="o")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Atenuación acumulada (dB)")
ax.set_title("Curva OTDR Simulada")
ax.grid(True)
ax.legend()
st.pyplot(fig)


