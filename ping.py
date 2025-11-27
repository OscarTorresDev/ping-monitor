# -*- coding: utf-8 -*-
"""
MONITOR DE INTERNET DEFINITIVO - TU VERSIÓN FAVORITA
Funciona en Windows · Linux · macOS · Docker
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import time
import subprocess
import platform
import numpy as np
import socket
import requests
import os
import sys

# ================== INSTALACIÓN AUTOMÁTICA CON UV ==================
def instalar_si_falta(paquete):
    try:
        __import__(paquete.replace("-", "_"))
    except ImportError:
        print(f"Instalando {paquete} con uv...")
        try:
            subprocess.check_call(["uv", "pip", "install", paquete],
                                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except:
            subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

for pkg in ["matplotlib", "numpy", "requests", "openpyxl"]:
    instalar_si_falta(pkg)

import openpyxl

# ====== TEMA OSCURO ======
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(13, 7), facecolor='#0e1117')
ax.set_facecolor('#0e1117')

# ====== CONFIGURACIÓN (igual que la tuya) ======
HOST_PRIMARIO = "1.1.1.1"
HOST_SECUNDARIO = "8.8.8.8"
INTERVALO = 4000
MAX_PUNTOS = 300
PING_MAX_BUENO = 100

# RUTA INTELIGENTE: Docker → /app/output | Windows/Linux/macOS → ./output
BASE_OUTPUT = "/app/output" if os.path.exists("/app/output") else "output"
EXCEL_FILE = f"{BASE_OUTPUT}/historial_caidas.xlsx"
os.makedirs(BASE_OUTPUT, exist_ok=True)  # Crea la carpeta si no existe

# ====== IPs ======
try:
    MI_IP_PUBLICA = requests.get('https://api.ipify.org', timeout=5).text
except:
    MI_IP_PUBLICA = "Sin conexión"
try:
    MI_IP_LOCAL = socket.gethostbyname(socket.gethostname())
except:
    MI_IP_LOCAL = "Desconocida"

# ====== VARIABLES ======
tiempos = []
latencias = []
colores = []
en_caida = False
inicio_caida = None
ULTIMOS_TIMEOUTS = 0
TIMEOUT_PARA_CAIDA = 3
log_caidas = []
pantallazo_pendiente = False
tiempo_pantallazo = 0.0
ultimo_host = HOST_PRIMARIO

# ====== PING UNIVERSAL (Windows / Linux / macOS) ======
def intentar_ping(host):
    global ultimo_host
    sistema = platform.system()
    param = "-n" if sistema == "Windows" else "-c"
    timeout_flag = "-w" if sistema == "Windows" else "-W"
    timeout_val = "2000" if sistema == "Windows" else "2"
    try:
        comando = ["ping", param, "1", timeout_flag, timeout_val, host]
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, timeout=4)
        salida = resultado.stdout.lower()
        if "ttl" in salida or "time" in salida:
            ultimo_host = host
            if sistema == "Windows":
                t = (salida.split("tiempo=")[-1] if "tiempo=" in salida else salida.split("time=")[-1])
                t = t.split("ms")[0].replace("<", "").strip()
            else:
                t = salida.split("time=")[-1].split(" ms")[0].strip()
            return float(t)
        return None
    except:
        return None

def hacer_ping():
    ping = intentar_ping(HOST_PRIMARIO)
    if ping is not None:
        return ping
    return intentar_ping(HOST_SECUNDARIO)

# ====== DURACIÓN BONITA ======
def formato_duracion(segundos):
    if segundos < 60:
        return f"{segundos} seg"
    mins = segundos // 60
    segs = segundos % 60
    return f"{mins} min {segs} seg" if segs else f"{mins} min"

# ====== REGISTRAR + PANTALLAZO EN output/ ======
def registrar_caida_excel(inicio, fin):
    global pantallazo_pendiente, tiempo_pantallazo
    try:
        h1, m1, s1 = map(int, inicio.split(":"))
        h2, m2, s2 = map(int, fin.split(":"))
        duracion_seg = (h2*3600 + m2*60 + s2) - (h1*3600 + m1*60 + s1)
    except:
        duracion_seg = 0

    fecha = datetime.now().strftime("%Y-%m-%d")
    fila = [fecha, inicio, fin, formato_duracion(duracion_seg), MI_IP_PUBLICA, MI_IP_LOCAL, ultimo_host]

    if os.path.exists(EXCEL_FILE):
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Fecha", "Inicio", "Fin", "Duración", "IP Pública", "IP Local", "Destino"])

    ws.append(fila)
    wb.save(EXCEL_FILE)

    pantallazo_pendiente = True
    tiempo_pantallazo = time.time() + 1.0
    print(f"RECUPERADO → Caída de {formato_duracion(duracion_seg)}")

def tomar_pantallazo(inicio, fin):
    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre = f"{BASE_OUTPUT}/CAIDA_{inicio.replace(':', '-')}_a_{fin.replace(':', '-')}_{fecha_hora}.png"
    fig.savefig(nombre, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Pantallazo guardado: {nombre}")

# ====== GRÁFICA (con tu letrero rojo que tanto te gusta) ======
ax.set_title(f"Monitor Internet • {MI_IP_PUBLICA} ({MI_IP_LOCAL}) → 1.1.1.1", fontsize=14, color='cyan', pad=20)
ax.set_xlabel("Hora", color='white')
ax.set_ylabel("Latencia (ms)", color='white')
ax.grid(True, alpha=0.3, color='#333333')
ax.tick_params(colors='white')

texto_estado = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=14, color='white',
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.9))
texto_log = ax.text(0.02, 0.05, "Sin caídas", transform=ax.transAxes, fontsize=11, color='#00ff88',
                    verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.8))
texto_corte = ax.text(0.02, 0.5, "", transform=ax.transAxes, fontsize=16, color='#ff0066',
                      fontweight='bold', rotation=90, verticalalignment='center',
                      bbox=dict(boxstyle='round', facecolor='#330000', alpha=0.9))

lineas = []

def actualizar(frame):
    global ULTIMOS_TIMEOUTS, en_caida, inicio_caida, pantallazo_pendiente, tiempo_pantallazo

    ahora = datetime.now().strftime("%H:%M:%S")
    tiempos.append(ahora)
    ping = hacer_ping()
    latencias.append(ping if ping is not None else np.nan)

    if ping is None:
        color = "red"
        ULTIMOS_TIMEOUTS += 1
    elif ping > PING_MAX_BUENO:
        color = "orange"
        ULTIMOS_TIMEOUTS = 0
    else:
        color = "lime"
        ULTIMOS_TIMEOUTS = 0
    colores.append(color)

    if ULTIMOS_TIMEOUTS >= TIMEOUT_PARA_CAIDA and not en_caida:
        en_caida = True
        inicio_caida = ahora
        fecha_corte = datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")
        texto_corte.set_text(f"CAÍDA\n{fecha_corte}")
        log_caidas.append(f"Caída desde {ahora}")
        if len(log_caidas) > 5: log_caidas.pop(0)

    if en_caida and ping is not None:
        en_caida = False
        fin_caida = ahora
        texto_corte.set_text("")
        log_caidas.append(f"Recuperado {fin_caida}")
        if len(log_caidas) > 5: log_caidas.pop(0)
        registrar_caida_excel(inicio_caida, fin_caida)

    if pantallazo_pendiente and time.time() >= tiempo_pantallazo:
        tomar_pantallazo(inicio_caida, ahora)
        pantallazo_pendiente = False

    for l in lineas:
        l.remove()
    lineas.clear()

    x = np.arange(len(tiempos))
    for i in range(1, len(tiempos)):
        if not np.isnan(latencias[i-1]) and not np.isnan(latencias[i]):
            seg = ax.plot(x[i-1:i+1], [latencias[i-1], latencias[i]], color=colores[i], lw=1)[0]
        else:
            seg = ax.plot(x[i-1:i+1], [0, 0], color="red", ls="--", lw=1)[0]
        lineas.append(seg)

    if len(tiempos) > 10:
        paso = max(1, len(tiempos)//15)
        ticks = np.arange(0, len(tiempos), paso)
        labels = [tiempos[i] if i < len(tiempos) else "" for i in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)

    ax.relim()
    ax.autoscale_view()

    estado = "CONECTADO" if ping is not None else "SIN INTERNET"
    color_estado = "#00ff00" if ping is not None else "#ff0000"
    texto_estado.set_text(f"Estado: {estado} • Ping: {ping if ping else '---'} ms • Host: {ultimo_host}")
    texto_estado.set_color(color_estado)
    texto_log.set_text("Últimas caídas:\n" + "\n".join(log_caidas[-5:]) if log_caidas else "Sin caídas")

    return lineas

# ====== INICIO ======
try:
    ani = animation.FuncAnimation(fig, actualizar, interval=INTERVALO, blit=False, cache_frame_data=False)
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    print("\nMonitor cerrado correctamente.")
    sys.exit(0)