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
