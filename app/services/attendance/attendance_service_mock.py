import json
import os

class AttendanceServiceMock:

    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.mock_path = os.path.join(base, "mock", "attendance.json")

        if not os.path.exists(self.mock_path):
            with open(self.mock_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    def _load(self):
        with open(self.mock_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.mock_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def registrar_asistencia(self, data):
        registros = self._load()

        data["id"] = len(registros) + 1
        registros.append(data)

        self._save(registros)
        print("✔ [MOCK] Asistencia guardada:", data)
        return {
            "status": "ok",
            "msg": "Asistencia registrada (mock)",
            "data": data
        }

    def obtener_asistencias(self):
        return self._load()
