import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import requests
from PIL import Image
from fpdf import FPDF

st.set_page_config(layout="wide")
st.title("📡 Simulador de Medición OTDR - Fibra Óptica")

# Parámetros
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 24.0, step=1.0)
atenuacion_km = st.slider("💡 Atenuación por km (dB)", 0.18, 0.25, 0.21, step=0.01)

# Generar puntos de fusión cada 4 km
eventos = int(distancia // 4)
puntos_evento = [round((i + 1) * 4, 2) for i in range(eventos) if (i + 1) * 4 <= distancia]

# Ajustes de atenuación por evento (editable por usuario)
atenuaciones_eventos = {}
st.subheader("🔧 Ajustar atenuación por evento de fusión")
for punto in puntos_evento:
    atenuaciones_eventos[punto] = st.slider(f"Evento en {punto} km", 0.00, 0.50, 0.15, step=0.01)

# Cálculo total de atenuación
atenuacion_total = atenuacion_km * distancia + sum(atenuaciones_eventos.values())

# Mostrar valor de atenuación máxima permitida
atenuacion_maxima_permitida = round((0.21 * distancia) + (0.15 * eventos), 2)
st.markdown(f"✅ **Atenuación máxima permitida:** {atenuacion_maxima_permitida} dB")

# Mostrar evento más atenuado
if atenuaciones_eventos:
    evento_mayor = max(atenuaciones_eventos.items(), key=lambda x: x[1])
    mayor_distancia = evento_mayor[0]
    mayor_atenuacion = evento_mayor[1]
    st.markdown(f"🔍 **Evento con mayor atenuación:** {mayor_atenuacion:.2f} dB a los {mayor_distancia} km")
else:
    mayor_distancia = None
    mayor_atenuacion = None
    st.markdown("🔍 No hay eventos de fusión para mostrar.")

# Simulación de curva OTDR
x = np.linspace(0, distancia, 1000)
y = -atenuacion_km * x

# Agregar eventos con caída
for punto, perdida in atenuaciones_eventos.items():
    idx = np.searchsorted(x, punto)
    y[idx:] -= perdida

# Graficar curva OTDR con círculo en evento mayor
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, y, label="Curva OTDR")
ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Simulación de traza OTDR")
ax.grid(True)

for punto, perdida in atenuaciones_eventos.items():
    ax.axvline(punto, color='red', linestyle='--')
    ax.text(punto, y[np.searchsorted(x, punto)], f"-{perdida:.2f} dB", color="red", rotation=90, va='bottom')

# Marca círculo rojo en evento mayor
if mayor_distancia is not None:
    idx_mayor = np.searchsorted(x, mayor_distancia)
    ax.plot(x[idx_mayor], y[idx_mayor], 'o', color='red', markersize=12, markerfacecolor='none', markeredgewidth=2)

st.pyplot(fig)

# Tabla con detalle de eventos
eventos_lista = sorted(atenuaciones_eventos.items())  # [(distancia, atenuacion), ...]
acumulado_eventos = 0
tabla_datos = []
mayor_index = -1

for i, (dist, att) in enumerate(eventos_lista, start=1):
    acumulado_eventos += att
    atenuacion_acumulada = (atenuacion_km * dist) + acumulado_eventos
    tabla_datos.append({
        "Nro Evento": i,
        "Distancia (km)": round(dist, 2),
        "Atenuación del evento (dB)": round(att, 2),
        "Atenuación acumulada (dB)": round(atenuacion_acumulada, 2)
    })
    if att == mayor_atenuacion:
        mayor_index = i - 1  # para resaltar fila

if tabla_datos:
    st.subheader("📋 Detalle de eventos de fusión y atenuación acumulada")
    df_eventos = pd.DataFrame(tabla_datos)

    def resaltar_fila(x):
        color = [''] * len(x)
        if mayor_index >= 0:
            color[mayor_index] = 'background-color: #ffcccc'
        return color

    st.dataframe(df_eventos.style.apply(resaltar_fila, axis=0))
else:
    st.info("No hay eventos de fusión para mostrar en la tabla.")

# Verificación de certificación
evento_supera_limite = next(((i+1, dist, att) for i, (dist, att) in enumerate(eventos_lista) if att > 0.15), None)
cumple_total = atenuacion_total <= atenuacion_maxima_permitida
cumple_eventos = evento_supera_limite is None

if cumple_total and cumple_eventos:
    st.success(f"✅ Atenuación Total: {atenuacion_total:.2f} dB (DENTRO del límite permitido)")
    st.markdown("### 🟢 ENLACE CERTIFICADO")
else:
    st.error(f"❌ Atenuación Total: {atenuacion_total:.2f} dB")
    st.markdown("### 🔴 NO CERTIFICA POR:")
    if not cumple_total:
        st.markdown(f"- 🔺 Atenuación total excede el máximo permitido de {atenuacion_maxima_permitida:.2f} dB")
    if not cumple_eventos:
        st.markdown(f"- 🔺 Evento N° {evento_supera_limite[0]} con {evento_supera_limite[2]:.2f} dB a los {evento_supera_limite[1]} km")

# Leyenda adicional
if atenuaciones_eventos:
    st.info(f"🔴 Evento con mayor atenuación: {mayor_atenuacion:.2f} dB a los {mayor_distancia} km")

# --- EXPORTAR PDF ---

def crear_pdf():
    # Descargar logo FICOM
    url_logo = "https://lirp.cdn-website.com/fbb70e7e/dms3rep/multi/opt/FICOMCELEST-1920w.png"
    response = requests.get(url_logo)
    logo_img = Image.open(io.BytesIO(response.content))
    logo_img = logo_img.convert("RGBA")
    logo_img.thumbnail((150, 150))

    # Crear buffer para la figura matplotlib (curva)
    buf_fig = io.BytesIO()
    # Volver a graficar para guardar sin Streamlit
    fig2, ax2 = plt.subplots(figsize=(10,5))
    ax2.plot(x, y, label="Curva OTDR")
    ax2.set_xlabel("Distancia (km)")
    ax2.set_ylabel("Potencia (dB)")
    ax2.set_title("Simulación de traza OTDR")
    ax2.grid(True)
    for punto, perdida in atenuaciones_eventos.items():
        ax2.axvline(punto, color='red', linestyle='--')
        ax2.text(punto, y[np.searchsorted(x, punto)], f"-{perdida:.2f} dB", color="red", rotation=90, va='bottom')
    if mayor_distancia is not None:
        idx_mayor = np.searchsorted(x, mayor_distancia)
        ax2.plot(x[idx_mayor], y[idx_mayor], 'o', color='red', markersize=12, markerfacecolor='none', markeredgewidth=2)
    fig2.savefig(buf_fig, format='PNG')
    plt.close(fig2)
    buf_fig.seek(0)

    # Crear PDF con fpdf
    pdf = FPDF()
    pdf.add_page()

    # Agregar marca de agua (logo con transparencia)
    pdf.image(buf=logo_img.tobytes(), x=30, y=220, w=50, h=50, type='PNG')  # Aquí se agregaría el logo, pero fpdf no soporta buffers así

    # Alternativa: guardar logo temporalmente y luego agregar imagen en pdf
    # Como en Streamlit no podemos crear archivos locales, guardamos en buffer:
    img_buf = io.BytesIO()
    logo_img.save(img_buf, format='PNG')
    img_buf.seek(0)
    pdf.image(img_buf, x=80, y=250, w=50, h=50, type='PNG')

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Simulación de Medición OTDR - Fibra Óptica", ln=True, align="C")
    pdf.ln(10)

    # Tabla con datos
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Distancia total: {distancia} km", ln=True)
    pdf.cell(0, 10, f"Atenuación por km: {atenuacion_km} dB/km", ln=True)
    pdf.cell(0, 10, f"Atenuación máxima permitida: {atenuacion_maxima_permitida} dB", ln=True)
    pdf.cell(0, 10, f"Atenuación total estimada: {atenuacion_total:.2f} dB", ln=True)
    pdf.cell(0, 10, f"Evento con mayor atenuación: {mayor_atenuacion:.2f} dB a {mayor_distancia} km", ln=True)
    pdf.ln(5)

    # Insertar imagen gráfica
    pdf.image(buf_fig, x=10, y=80, w=190)

    # Tabla de eventos
    pdf.ln(105)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Detalle de eventos:", ln=True)
    pdf.set_font("Arial", size=12)
    # Tabla cabecera
    pdf.cell(30, 10, "Nro Evento", 1)
    pdf.cell(40, 10, "Distancia (km)", 1)
    pdf.cell(60, 10, "Atenuación evento (dB)", 1)
    pdf.cell(60, 10, "Atenuación acumulada (dB)", 1)
    pdf.ln()

    for fila in tabla_datos:
        pdf.cell(30, 10, str(fila["Nro Evento"]), 1)
        pdf.cell(40, 10, str(fila["Distancia (km)"]), 1)
        pdf.cell(60, 10, str(fila["Atenuación del evento (dB)"]), 1)
        pdf.cell(60, 10, str(fila["Atenuación acumulada (dB)"]), 1)
        pdf.ln()

    # Resultado final
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    if cumple_total and cumple_eventos:
        pdf.cell(0, 10, "ENLACE CERTIFICADO", ln=True, align="C")
    else:
        pdf.cell(0, 10, "NO CERTIFICA", ln=True, align="C")

    return pdf.output(dest='S').encode('latin1')


if st.button("📥 Exportar PDF"):
    pdf_bytes = crear_pdf()
    st.download_button(label="Descargar PDF", data=pdf_bytes, file_name="simulacion_otdr.pdf", mime="application/pdf")