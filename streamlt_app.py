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

# Atenuaciones por km según selección
atenuacion_1310 = 0.35
atenuacion_1550 = 0.21

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

st.subheader("🔧 Ajustar atenuación por evento de fusión")
atenuaciones_eventos = {}
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

def calcular_atenuacion_total(atenuacion_km):
    return atenuacion_km * distancia + sum(atenuaciones_eventos.values())

# Cálculos totales
atenuacion_total_1310 = calcular_atenuacion_total(atenuacion_1310) if check_1310 else None
atenuacion_total_1550 = calcular_atenuacion_total(atenuacion_1550) if check_1550 else None

# Presupuesto óptico por longitud de onda
presupuesto_1310 = round((atenuacion_1310 * distancia) + (0.15 * eventos), 2)
presupuesto_1550 = round((atenuacion_1550 * distancia) + (0.15 * eventos), 2)

# Mostrar presupuesto óptico
st.markdown("### 🔆 Presupuesto Óptico")
if check_1310:
    st.markdown(f"- 1310 nm: {presupuesto_1310} dB")
if check_1550:
    st.markdown(f"- 1550 nm: {presupuesto_1550} dB")

# Preparar datos para graficar
x = np.linspace(0, distancia, 1000)

def generar_curva(atenuacion_km):
    y = -atenuacion_km * x
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y[idx:] -= perdida
    return y

# Graficar curvas según selección
fig, ax = plt.subplots(figsize=(10, 5))
if check_1310:
    y_1310 = generar_curva(atenuacion_1310)
    ax.plot(x, y_1310, label="1310 nm", color="blue")
if check_1550:
    y_1550 = generar_curva(atenuacion_1550)
    ax.plot(x, y_1550, label="1550 nm", color="green")

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# Función para generar tabla con formato y resaltar evento mayor
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

    if tabla_datos:
        df_eventos = pd.DataFrame(tabla_datos)

        def resaltar_fila(x):
            color = [''] * len(x)
            if mayor_index >= 0:
                color[mayor_index] = 'background-color: #ffcccc'
            return color

        st.dataframe(
            df_eventos.style
            .apply(resaltar_fila, axis=0)
            .format({
                "Distancia (km)": "{:.2f}",
                "Atenuación del evento (dB)": "{:.2f}",
                "Atenuación acumulada (dB)": "{:.2f}"
            })
        )
        return mayor_atenuacion, mayor_index, df_eventos
    else:
        st.info("No hay eventos de fusión para mostrar en la tabla.")
        return None, None, None

st.subheader("📋 Seleccione la tabla de eventos a mostrar:")
tabla_1310 = st.checkbox("Mostrar tabla para 1310 nm", value=True)
tabla_1550 = st.checkbox("Mostrar tabla para 1550 nm", value=False)

# Evitar seleccionar ambas tablas a la vez
if tabla_1310 and tabla_1550:
    st.warning("Por favor seleccione solo una tabla a la vez.")
    st.stop()
elif not tabla_1310 and not tabla_1550:
    st.info("Seleccione una tabla para mostrar.")
    st.stop()

mayor_atenuacion_tabla = None
mayor_index_tabla = None

if tabla_1310:
    mayor_atenuacion_tabla, mayor_index_tabla, df_eventos = generar_tabla(atenuacion_1310)
elif tabla_1550:
    mayor_atenuacion_tabla, mayor_index_tabla, df_eventos = generar_tabla(atenuacion_1550)

# Verificación de certificación
def verificar_certificacion(atenuacion_total, presupuesto_optico):
    cumple_total = atenuacion_total <= presupuesto_optico
    evento_supera_limite = next(((i+1, dist, att) for i, (dist, att) in enumerate(atenuaciones_eventos.items()) if att > 0.15), None)
    cumple_eventos = evento_supera_limite is None
    return cumple_total, cumple_eventos, evento_supera_limite

st.subheader("✅ Resultado de certificación")

if check_1310:
    cumple_total_1310, cumple_eventos_1310, evento_supera_limite_1310 = verificar_certificacion(atenuacion_total_1310, presupuesto_1310)
if check_1550:
    cumple_total_1550, cumple_eventos_1550, evento_supera_limite_1550 = verificar_certificacion(atenuacion_total_1550, presupuesto_1550)

def mostrar_resultado(longitud, cumple_total, cumple_eventos, evento_supera_limite, atenuacion_total):
    if cumple_total and cumple_eventos:
        st.success(f"✅ {longitud} nm - Atenuación Total: {atenuacion_total:.2f} dB (DENTRO del límite permitido)")
        st.markdown("### 🟢 ENLACE CERTIFICADO")
    else:
        st.error(f"❌ {longitud} nm - Atenuación Total: {atenuacion_total:.2f} dB")
        st.markdown("### 🔴 NO CERTIFICA POR:")
        if not cumple_total:
            st.markdown(f"- 🔺 Atenuación total excede el máximo permitido")
        if not cumple_eventos and evento_supera_limite is not None:
            st.markdown(f"- 🔺 Evento N° {evento_supera_limite[0]} con {evento_supera_limite[2]:.2f} dB a los {evento_supera_limite[1]} km")

if check_1310:
    mostrar_resultado("1310", cumple_total_1310, cumple_eventos_1310, evento_supera_limite_1310, atenuacion_total_1310)
if check_1550:
    mostrar_resultado("1550", cumple_total_1550, cumple_eventos_1550, evento_supera_limite_1550, atenuacion_total_1550)
