# app/routes.py

from flask import Blueprint, jsonify, request

# Crea un Blueprint llamado 'main'
# Este blueprint se registrará en __init__.py
main = Blueprint('main', __name__)

# Ejemplo de Endpoint (Ruta) GET
@main.route('/', methods=['GET'])
def home():
    """Ruta principal para verificar que el API funciona."""
    return jsonify({
        "status": "success",
        "message": "Bienvenido al backend de kallpa-unl. El API está funcionando.",
        "version": "1.0"
    }), 200

# Ejemplo de Endpoint POST
@main.route('/usuarios', methods=['POST'])
def crear_usuario():
    """Ruta para crear un nuevo recurso (ej. usuario)."""
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({"status": "error", "message": "Datos de entrada inválidos"}), 400

    nombre = data.get('nombre')
    
    # Lógica para guardar el usuario en la base de datos (por implementar)
    
    return jsonify({
        "status": "success",
        "message": f"Usuario '{nombre}' creado exitosamente."
    }), 201