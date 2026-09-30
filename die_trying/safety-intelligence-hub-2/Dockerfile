# Imagen ligera con Python 3.12. Empaqueta el pipeline completo para que
# se ejecute exactamente igual en Mac, Windows o Linux -- resuelve el problema
# de "en mi máquina funciona" sin que nadie tenga que instalar Python a mano.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ejecuta el pipeline completo (genera datos + calcula KPIs + escribe manifest)
CMD ["python3", "orchestration/run_pipeline.py"]
