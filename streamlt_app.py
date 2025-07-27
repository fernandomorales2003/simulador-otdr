import matplotlib.pyplot as plt
import numpy as np

# Parámetros de la fibra
distancia_total_km = 5
atenuacion_por_km = 0.35

# Segmento inicial (conector de fibra óptica)
x_conector = np.array([0.0, 0.005, 0.075])  # 0 m, 5 m, 75 m
y_conector = np.array([0.0, 1.0, -0.5])     # ganancia y caída reflejada

# Segmento de la fibra óptica (desde 75 m en adelante)
x_fibra = np.linspace(0.075, distancia_total_km, 1000)
y_fibra = -atenuacion_por_km * x_fibra - 0.5  # continuar desde el nivel del conector

# Combinar ambos segmentos
x_total = np.concatenate([x_conector, x_fibra])
y_total = np.concatenate([y_conector, y_fibra])

# Graficar
plt.figure(figsize=(10, 5))
plt.plot(x_total, y_total, label="Traza OTDR", color="blue")
plt.xlabel("Distancia (km)")
plt.ylabel("Potencia (dB)")
plt.title("Simulación de conector de fibra óptica al inicio")
plt.grid(True)
plt.ylim(-5, 2)
plt.xlim(0, distancia_total_km)
plt.tight_layout()
plt.show()

