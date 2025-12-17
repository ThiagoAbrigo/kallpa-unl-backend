📘 Manual de Instalación – KALLPA-UNL Backend

Backend desarrollado con Flask + PostgreSQL.

Requisitos:

**Python 3.12**

**PostgreSQL 18**

*pgAdmin 4 (opcional)*

*Dependencias incluidas en requirements.txt*

📦 Instalación en Windows
Paso 1: 
Clonar el repositorio
git clone <https://github.com/ThiagoAbrigo/kallpa-unl-backend>
cd KALLPA-UNL-BACKEND

Paso 2:
Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate

Paso 3:
Instalar dependencias del proyecto
pip install -r requirements.txt

🗄️ Configuración de la Base de Datos (PostgreSQL)

Abrir pgAdmin o terminal.

Crear base de datos:

kallpa_db

🔧 Configurar archivo .env

Crear un archivo .env en la raíz del proyecto

▶️ Ejecutar el proyecto

python index.py


Servidor disponible en:

http://localhost:5000