# Catarina — Microaprendizaje supervisado con metodologías activas e IA

<img width="100%" height="auto" alt="Dibujo de Catarina y al lado el título del proyecto: Microaprendizaje supervisado con metodologías activas e IA" src="/images/banner.png" />

Descripción
---------
Sistema que genera actividades automáticamente (pipeline en `main.py`) y expone/visualiza los datos mediante una aplicación Flask (`app.py`). Para ejecución local sin una base de datos real hay una muestra en `data/` (JSON).

Requisitos previos
------------------
- Python 3.10+
- pip (o pipenv/poetry)
- Se recomienda usar un entorno virtual (venv)

Instalación
---------
1. Clonar el repositorio:
```bash
git clone https://github.com/RafaelLuizC/hack4edu_IFC
cd hack4edu_IFC
```

2. Crear y activar un venv (Windows):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1    # PowerShell
# o
.venv\Scripts\activate.bat    # CMD
```

3. Instalar dependencias:
- Si existe `requirements.txt`:
```bash
pip install -r requirements.txt
```
- Si no existe, instalar al menos:
```bash
pip install flask python-dotenv
```

Configurar variables de entorno
--------------------------------
El pipeline utiliza modelos de IA en la nube (clave en `.env`). Cree un archivo `.env` en la raíz con la clave necesaria, por ejemplo:
```
CLOUD_API_KEY=tu_clave_aqui
```

Uso
---
- Ejecutar el pipeline de generación:
```bash
python main.py
```
Edite `main.py` para indicar la ruta/URL del PDF a procesar, según el comentario en el archivo.

- Ejecutar el servidor Flask:
```bash
python app.py
```
Acceder en el navegador:
```
http://localhost:5000
```

Base de datos (muestra)
------------------------
El repositorio contiene una muestra de datos en `data/` para ejecución sin una base de datos real. Para usar una base de datos real, descomente las líneas 2, 21 y 22 en `app.py` (según el comentario en ese archivo) — confirme que esas líneas sigan correspondiendo a la configuración de la base de datos al editar.

Consejos y solución de problemas
---------------------------
- Si usa `.env`, asegúrese de que `python-dotenv` esté instalado (la app debería cargar las variables automáticamente).
- Si Flask no se inicia, verifique permisos del puerto 5000 y los mensajes en el terminal.
