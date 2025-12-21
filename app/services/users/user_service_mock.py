import json
import os

class UserServiceMock:

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        print("BASE:", base)
        self.mock_path = os.path.join(base, "mock", "users.json")
        print("MOCK PATH:", self.mock_path)

    def _load(self):
        with open(self.mock_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save(self, data):
        with open(self.mock_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all_users(self):
        return self._load()
    
    def create_user(self, data):
        users = self._load()
        
        # Generar nuevo ID
        new_id = max([u.get('id', 0) for u in users], default=0) + 1
        
        # Crear nuevo usuario
        new_user = {
            'id': new_id,
            'nombre': data.get('nombre'),
            'apellido': data.get('apellido'),
            'edad': data.get('edad'),
            'dni': data.get('dni'),
            'telefono': data.get('telefono'),
            'correo': data.get('correo'),
            'direccion': data.get('direccion'),
            'estado': 'ACTIVO',
            'tipo': data.get('tipo', 'ESTUDIANTE')
        }
        
        users.append(new_user)
        self._save(users)
        
        return {
            'status': 'ok',
            'msg': 'Participante registrado exitosamente (MOCK)',
            'data': new_user
        }, 201

    def create_initiation_participant(self, data):
        """Crea un participante de iniciación con su responsable (versión MOCK)"""
        users = self._load()
        
        # Separar datos
        datos_nino = data.get('participante')
        datos_padre = data.get('responsable')
        
        if not datos_nino or not datos_padre:
            return {"status": "error", "msg": "Faltan datos del niño o responsable"}, 400
        
        # Generar nuevo ID
        new_id = max([u.get('id', 0) for u in users], default=0) + 1
        
        # Crear participante de iniciación
        new_participant = {
            'id': new_id,
            'nombre': datos_nino.get('nombre'),
            'apellido': datos_nino.get('apellido'),
            'edad': datos_nino.get('edad'),
            'dni': datos_nino.get('dni'),
            'telefono': datos_nino.get('telefono', ''),
            'correo': datos_nino.get('correo', ''),
            'direccion': datos_nino.get('direccion', ''),
            'estado': 'ACTIVO',
            'tipo': 'INICIACION',
            'responsable': {
                'nombre': datos_padre.get('nombre'),
                'apellido': datos_padre.get('apellido'),
                'dni': datos_padre.get('dni'),
                'telefono': datos_padre.get('telefono'),
                'parentesco': datos_padre.get('parentesco', 'Representante')
            }
        }
        
        users.append(new_participant)
        self._save(users)
        
        return {
            'status': 'ok',
            'msg': 'Niño y representante registrados correctamente (MOCK)',
            'data': {'id_participante': new_id}
        }, 201

    def change_status(self, user_id, nuevo_estado):
        """Cambia el estado de un participante (versión MOCK)"""
        users = self._load()
        
        # Buscar el usuario por ID
        user_found = None
        for user in users:
            if user.get('id') == user_id:
                user_found = user
                break
        
        if not user_found:
            return {"status": "error", "msg": "Participante no encontrado"}, 404
        
        # Actualizar el estado
        user_found['estado'] = nuevo_estado
        self._save(users)
        
        return {
            'status': 'ok',
            'msg': f'Estado actualizado a {nuevo_estado} (MOCK)',
            'data': user_found
        }, 200

    def search_by_dni(self, dni):
        """Busca un participante por DNI (versión MOCK)"""
        users = self._load()
        
        # Buscar el usuario por DNI
        for user in users:
            if user.get('dni') == dni:
                return {
                    'status': 'ok',
                    'msg': 'Participante encontrado (MOCK)',
                    'data': user
                }, 200
        
        return {"status": "error", "msg": "Participante no encontrado"}, 404
