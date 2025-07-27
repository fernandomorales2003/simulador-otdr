import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("📡 Simulador de MEDICIONES OTDR")

# Parámetros
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 10.0, step=1.0)

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

# Mostrar/ocultar sliders
mostrar_eventos = st.checkbox("🔧 Ajustar atenuación por evento de fusión", value=True)

# Inicializar eventos
atenuaciones_eventos = {0.0: 0.5, distancia: 0.5}
if mostrar_eventos:
    for punto in puntos_evento:
        atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)
else:
    for punto in puntos_evento:
        atenuaciones_eventos[punto] = 0.15

# Cálculo de atenuación total
def calcular_atenuacion_total(at_km):
    return at_km * distancia + sum(atenuaciones_eventos.values())

at_total_1310 = calcular_atenuacion_total(atenuacion_1310) if check_1310 else None
at_total_1550 = calcular_atenuacion_total(atenuacion_1550) if check_1550 else None

# Presupuesto óptico (incluye conectores)
presupuesto_1310 = round((atenuacion_1310 * distancia) + (0.15 * eventos) + 1.0, 2)
presupuesto_1550 = round((atenuacion_1550 * distancia) + (0.15 * eventos) + 1.0, 2)

st.markdown("### 🔆 Presupuesto Óptico")
if check_1310:
    st.markdown(f"- 1310 nm: {presupuesto_1310} dB")
if check_1550:
    st.markdown(f"- 1550 nm: {presupuesto_1550} dB")

# Curva OTDR
def generar_curva_completa(at_km):
    x_ini = np.array([0.0, 0.005, 0.075])
    y_ini = np.array([0.0, 0.8, -0.25])
    x_fibra = np.linspace(0.075, distancia - 0.075, 1000)
    y_fibra = -at_km * x_fibra + y_ini[-1]
    for punto, perdida in atenuaciones_eventos.items():
        idx = np.searchsorted(x_fibra, punto)
        y_fibra[idx:] -= perdida
    y_fin_base = y_fibra[-1]
    x_fin = np.array([distancia - 0.075 + 0.005, distancia - 0.075 + 0.010, distancia])
    y_fin = np.array([y_fin_base, y_fin_base + 0.8, y_fin_base - 0.5])
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

# Marcar eventos con pérdida > 0.15
for punto, perdida in atenuaciones_eventos.items():
    if punto in [0.0, distancia]:
        continue
    if perdida > 0.15:
        for at_km, color in [(atenuacion_1310, 'blue'), (atenuacion_1550, 'green')]:
            if (check_1310 and at_km == atenuacion_1310) or (check_1550 and at_km == atenuacion_1550):
                y_val = -at_km * punto - sum([v for k, v in atenuaciones_eventos.items() if k <= punto])
                ax.plot(punto, y_val, 'o', color='red', markersize=10, alpha=0.6, label='_nolegend_')

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla
def generar_tabla(at_km_tabla):
    eventos_lista = sorted(atenuaciones_eventos.items())
    acumulado_eventos = 0
    tabla_datos = []
    mayor_index = -1
    mayor_at = 0

    for i, (dist, att) in enumerate(eventos_lista, start=1):
        acumulado_eventos += att
        at_acumulada = (at_km_tabla * dist) + acumulado_eventos
        reflexion = -60.0 if dist in [0.0, distancia] else 0.0
        tabla_datos.append({
            "Nro Evento": i,
            "Distancia (km)": dist,
            "Atenuación del evento (dB)": att,
            "Atenuación acumulada (dB)": at_acumulada,
            "Reflexión (dB)": reflexion
        })
        if att > mayor_at and dist not in [0.0, distancia]:
            mayor_at = att
            mayor_index = i - 1

    df = pd.DataFrame(tabla_datos)

    def resaltar_fila(x):
        colores = [''] * len(x)
        if mayor_index >= 0:
            colores[mayor_index] = 'background-color: #ffcccc'
        return colores

    st.dataframe(
        df.style
        .apply(resaltar_fila, axis=0)
        .format({
            "Distancia (km)": "{:.2f}",
            "Atenuación del evento (dB)": "{:.2f}",
            "Atenuación acumulada (dB)": "{:.2f}",
            "Reflexión (dB)": "{:.2f}"
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
    cumple_total = at_total <= presupuesto or np.isclose(at_total, presupuesto, atol=0.01)
    evento_malo = next(((i+1, dist, att) for i, (dist, att) in enumerate(atenuaciones_eventos.items()) if att > 0.15 and dist not in [0.0, distancia]), None)
    cumple_eventos = evento_malo is None
    return cumple_total, cumple_eventos, evento_malo

st.subheader("✅ Resultado de certificación")

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
    c_total_1310, c_eventos_1310, evento_1310 = verificar_certificacion(at_total_1310, presupuesto_1310)
    mostrar_resultado("1310", c_total_1310, c_eventos_1310, evento_1310, at_total_1310)
if check_1550:
    c_total_1550, c_eventos_1550, evento_1550 = verificar_certificacion(at_total_1550, presupuesto_1550)
    mostrar_resultado("1550", c_total_1550, c_eventos_1550, evento_1550, at_total_1550)
