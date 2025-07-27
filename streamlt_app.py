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

# Evento inicial (conector)
atenuaciones_eventos[0.0] = st.slider(f"Conector INICIO en 0.0 km", 0.00, 1.00, 0.30, step=0.01)

# Eventos intermedios
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Evento final (conector)
atenuaciones_eventos[distancia] = st.slider(f"Conector FINAL en {distancia} km", 0.00, 1.00, 0.30, step=0.01)

def calcular_atenuacion_total(at_km):
    return at_km * distancia + sum(atenuaciones_eventos.values())

at_total_1310 = calcular_atenuacion_total(atenuacion_1310) if check_1310 else None
at_total_1550 = calcular_atenuacion_total(atenuacion_1550) if check_1550 else None

# Presupuesto óptico considerando los conectores como eventos adicionales
presupuesto_1310 = round((atenuacion_1310 * distancia) + (0.15 * eventos) + 0.60, 2)  # 0.3 + 0.3 conectores
presupuesto_1550 = round((atenuacion_1550 * distancia) + (0.15 * eventos) + 0.60, 2)

st.markdown("### 🔆 Presupuesto Óptico")
if check_1310:
    st.markdown(f"- 1310 nm: {presupuesto_1310} dB")
if check_1550:
    st.markdown(f"- 1550 nm: {presupuesto_1550} dB")

x = np.linspace(0, distancia, 1000)

def generar_curva(at_km):
    y = -at_km * x
    # Para cada evento, aplicar la atenuación a partir del punto
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x, punto)
        y[idx:] -= perdida
    return y

fig, ax = plt.subplots(figsize=(10, 5))
if check_1310:
    y_1310 = generar_curva(atenuacion_1310)
    ax.plot(x, y_1310, label="1310 nm", color="blue")
if check_1550:
    y_1550 = generar_curva(atenuacion_1550)
    ax.plot(x, y_1550, label="1550 nm", color="green")

# 🔴 Círculos rojos para eventos > 0.15 dB
for punto, perdida in atenuaciones_eventos.items():
    if perdida > 0.15:
        for at_km, color, check in [(atenuacion_1310, 'blue', check_1310), (atenuacion_1550, 'green', check_1550)]:
            if check:
                y_val = -at_km * punto - sum([v for k, v in atenuaciones_eventos.items() if k <= punto])
                ax.plot(punto, y_val, 'o', color='red', markersize=10, alpha=0.6, label='_nolegend_')

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla de eventos con fila final y eventos inicial y final incluidos
def generar_tabla(at_km_tabla):
    eventos_lista = sorted(atenuaciones_eventos.items())
    acumulado_eventos = 0
    tabla_datos = []
    mayor_index = -1
    mayor_at = 0

    for i, (dist, att) in enumerate(eventos_lista, start=1):
        acumulado_eventos += att
        at_acumulada = (at_km_tabla * dist) + acumulado_eventos
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": dist,
            "Atenuación del evento (dB)": att,
            "Atenuación acumulada (dB)": at_acumulada
        })
        if att > mayor_at:
            mayor_at = att
            mayor_index = i - 1

    at_total_final = round(at_km_tabla * distancia + sum(atenuaciones_eventos.values()), 2)
    tabla_datos.append({
        "Nro Evento": "—",
        "Distancia (km)": distancia,
        "Atenuación del evento (dB)": 0.00,
        "Atenuación acumulada (dB)": at_total_final
    })
    fila_total_index = len(tabla_datos) - 1

    df = pd.DataFrame(tabla_datos)

    def resaltar_fila(x):
        colores = [''] * len(x)
        if mayor_index >= 0:
            colores[mayor_index] = 'background-color: #ffcccc'
        colores[fila_total_index] = 'background-color: #ccffcc'
        return colores

    st.dataframe(
        df.style
        .apply(resaltar_fila, axis=0)
        .format({
            "Distancia (km)": "{:.2f}",
            "Atenuación del evento (dB)": "{:.2f}",
            "Atenuación acumulada (dB)": "{:.2f}"
        }),
        use_container_width=True
    )

    return mayor_at, mayor_index, df

# Mostrar tabla
st.subheader("📋 Seleccione la tabla de eventos a mostrar:")
tabla_1310 = st.checkbox("Mostrar tabla para 1310 nm", value=True)
tabla_1550 = st.checkbox("Mostrar tabla para 1550 nm", value=False)

if tabla_1310 and tabla_1550:
    st.warning("Por favor seleccione solo una tabla a la vez.")
    st.stop()
elif not tabla_1310 and not tabla_1550:
    st.info("Seleccione una tabla para mostrar.")
    st.stop()

if tabla_1310:
    mayor_at, _, df_eventos = generar_tabla(atenuacion_1310)
elif tabla_1550:
    mayor_at, _, df_eventos = generar_tabla(atenuacion_1550)

# Verificación
def verificar_certificacion(at_total, presupuesto):
    cumple_total = at_total <= presupuesto
    evento_malo = next(((i+1, dist, att) for i, (dist, att) in enumerate(atenuaciones_eventos.items()) if att > 0.15), None)
    cumple_eventos = evento_malo is None
    return cumple_total, cumple_eventos, evento_malo

st.subheader("✅ Resultado de certificación")

if check_1310:
    c_total_1310, c_eventos_1310, evento_1310 = verificar_certificacion(at_total_1310, presupuesto_1310)
if check_1550:
    c_total_1550, c_eventos_1550, evento_1550 = verificar_certificacion(at_total_1550, presupuesto_1550)

def mostrar_resultado(longitud, cumple_total, cumple_eventos, evento, at_total):
    if cumple_total and cumple_eventos:
        st.success(f"✅ {longitud} nm - Atenuación Total: {at_total:.2f} dB (DENTRO del límite permitido)")
        st.markdown("### 🟢 ENLACE CERTIFICADO")
    else:
        st.error(f"❌ {longitud} nm - Atenuación Total: {at_total:.2f} dB")
        st.markdown("### 🔴 NO CERTIFICA POR:")
        if not cumple_total:
            st.markdown(f"- 🔺 Atenuación total excede el máximo permitido")
        if not cumple_eventos and evento is not None:
            st.markdown(f"- 🔺 Evento N° {evento[0]} con {evento[2]:.2f} dB a los {evento[1]} km")

if check_1310:
    mostrar_resultado("1310", c_total_1310, c_eventos_1310, evento_1310, at_total_1310)
if check_1550:
    mostrar_resultado("1550", c_total_1550, c_eventos_1550, evento_1550, at_total_1550)
