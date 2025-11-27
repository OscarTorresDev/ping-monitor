# Monitor de Internet Definitivo

![Captura de pantalla](output/ejemplo-pantallazo.png)  <!-- Sube una captura tuya aquí -->

Monitorea tu conexión en tiempo real con ping inteligente a 1.1.1.1 (Cloudflare preferido), detecta caídas, gráfica oscura épica y exporta a Excel.

```bash
git clone https://github.com/OscarTorresDev/monitor-internet.git
cd monitor-internet
uv pip install matplotlib numpy requests openpyxl
python ping.py
