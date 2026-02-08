"""
SMOKE TESTS — KALLPA-UNL Backend
================================
Pruebas de humo (smoke tests) para verificar que los componentes
críticos del sistema están operativos después de un despliegue.

Objetivo: Validar rápidamente que las funcionalidades esenciales
del sistema responden correctamente (no se "incendian").

Criterios de un Smoke Test:
  - Ejecución rápida (< 30 segundos en total)
  - Cubre solo el "camino feliz" principal de cada módulo
  - No modifica datos permanentemente cuando es posible
  - Falla rápido si algo crítico está roto
  - Se ejecuta contra el sistema desplegado (servidor activo)

Requisitos:
  - Servidor Flask activo en http://127.0.0.1:5000
  - Base de datos PostgreSQL configurada y accesible
  - Usuario admin@kallpa.com con contraseña 123456

Ejecución:
  python -m unittest tests.test_unitarios.smoke_tests -v
"""

import unittest
import requests
import uuid
import random
import string
import time

BASE_URL = "http://127.0.0.1:5000/api"
TIMEOUT = 5  # Timeout en segundos por petición


class SmokeTests(unittest.TestCase):
    """
    Suite de Smoke Tests para KALLPA-UNL Backend.

    Cada test verifica una funcionalidad crítica del sistema con una
    única petición HTTP, asegurando que el servicio está operativo.
    """

    # ================================================================
    # SETUP
    # ================================================================

    def setUp(self):
        """Configuración común para todos los smoke tests."""
        self.start_time = time.time()
        self.headers = {"Content-Type": "application/json"}
        self.token = None

    def tearDown(self):
        """Registra el tiempo de ejecución de cada test."""
        elapsed = time.time() - self.start_time
        print(f"  [Tiempo: {elapsed:.3f}s]")

    # ================================================================
    # HELPERS
    # ================================================================

    def _get_auth_headers(self):
        """Obtiene headers con token JWT válido."""
        if not self.token:
            payload = {"email": "admin@kallpa.com", "password": "123456"}
            resp = requests.post(
                f"{BASE_URL}/auth/login", json=payload, timeout=TIMEOUT
            )
            self.assertEqual(resp.status_code, 200, "No se pudo autenticar")
            self.token = resp.json()["token"]
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def _generate_dni(self):
        """Genera un DNI numérico único de 10 dígitos."""
        return "19" + "".join(random.choices(string.digits, k=8))

    # ================================================================
    # SM-01: SALUD DEL SERVIDOR
    # ================================================================

    def test_sm_01_server_is_alive(self):
        """SM-01: El servidor responde en la ruta raíz.

        Verifica que el servidor Flask está levantado y responde HTTP 200
        en el endpoint raíz. Es la prueba más básica: si falla, nada más
        funcionará.

        Justificación Smoke Test: Valida la disponibilidad del servicio.
        """
        resp = requests.get("http://127.0.0.1:5000/", timeout=TIMEOUT)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Kallpa", resp.text)
        print("  SM-01 PASS: Servidor activo y respondiendo")

    # ================================================================
    # SM-02: SALUD DE LA BASE DE DATOS
    # ================================================================

    def test_sm_02_database_health(self):
        """SM-02: La conexión a la base de datos está operativa.

        Ejecuta una consulta simple (SELECT 1) a través del endpoint
        /health/db para verificar que PostgreSQL está accesible.

        Justificación Smoke Test: Sin BD, todo el sistema es inoperante.
        """
        resp = requests.get(f"{BASE_URL}/health/db", timeout=TIMEOUT)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["db"], "ok")
        print("  SM-02 PASS: Base de datos conectada y operativa")

    # ================================================================
    # SM-03: AUTENTICACIÓN - LOGIN EXITOSO
    # ================================================================

    def test_sm_03_login_returns_token(self):
        """SM-03: El sistema de autenticación genera tokens JWT.

        Verifica que el endpoint de login acepta credenciales válidas
        y retorna un token JWT. Sin autenticación funcional, ningún
        endpoint protegido es accesible.

        Justificación Smoke Test: La autenticación es prerrequisito
        de todas las operaciones del sistema.
        """
        payload = {"email": "admin@kallpa.com", "password": "123456"}
        resp = requests.post(
            f"{BASE_URL}/auth/login", json=payload, timeout=TIMEOUT
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("token", data)
        self.assertTrue(len(data["token"]) > 20, "Token JWT demasiado corto")
        print(f"  SM-03 PASS: Token JWT generado ({len(data['token'])} chars)")

    # ================================================================
    # SM-04: AUTENTICACIÓN - LOGIN RECHAZADO
    # ================================================================

    def test_sm_04_login_rejects_invalid_credentials(self):
        """SM-04: El sistema rechaza credenciales inválidas.

        Verifica que el login rechaza contraseñas incorrectas con
        código 401. Complementa SM-03 para confirmar que la autenticación
        no está deshabilitada ni acepta cualquier credencial.

        Justificación Smoke Test: Validar que la seguridad básica
        está activa es esencial en un smoke test post-despliegue.
        """
        payload = {"email": "admin@kallpa.com", "password": "contraseña_erronea"}
        resp = requests.post(
            f"{BASE_URL}/auth/login", json=payload, timeout=TIMEOUT
        )
        # El servidor debe rechazar credenciales inválidas (no retornar 200)
        self.assertNotEqual(resp.status_code, 200, "El login NO debería aceptar credenciales inválidas")
        self.assertIn(resp.status_code, [400, 401, 403, 500])
        print(f"  SM-04 PASS: Credenciales inválidas rechazadas (HTTP {resp.status_code})")

    # ================================================================
    # SM-05: PROTECCIÓN JWT - ENDPOINTS PROTEGIDOS
    # ================================================================

    def test_sm_05_protected_endpoint_requires_auth(self):
        """SM-05: Los endpoints protegidos rechazan peticiones sin token.

        Verifica que un endpoint protegido (@jwt_required) retorna
        401/403 cuando no se envía token de autenticación.

        Justificación Smoke Test: Garantiza que el middleware de
        seguridad JWT está activo y protegiendo los recursos.
        """
        resp = requests.get(f"{BASE_URL}/users", timeout=TIMEOUT)
        self.assertIn(resp.status_code, [401, 403])
        print("  SM-05 PASS: Endpoint protegido rechaza acceso sin token")

    # ================================================================
    # SM-06: LISTAR USUARIOS
    # ================================================================

    def test_sm_06_list_users(self):
        """SM-06: El módulo de usuarios puede listar participantes.

        Verifica que el endpoint GET /users responde correctamente
        con autenticación válida. Confirma que el módulo de usuarios
        y la consulta a BD funcionan.

        Justificación Smoke Test: El listado de usuarios es la
        operación de lectura más frecuente del sistema.
        """
        headers = self._get_auth_headers()
        resp = requests.get(f"{BASE_URL}/users", headers=headers, timeout=TIMEOUT)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("data", data)
        print(f"  SM-06 PASS: Listado de usuarios OK ({len(data.get('data', []))} registros)")

    # ================================================================
    # SM-07: REGISTRO DE PARTICIPANTE
    # ================================================================

    def test_sm_07_create_participant(self):
        """SM-07: Se puede registrar un nuevo participante.

        Verifica el flujo completo de creación de participante con datos
        válidos. Es la operación de escritura principal del sistema.

        Justificación Smoke Test: Si el registro de participantes falla,
        el sistema no puede cumplir su función principal.
        """
        unique_id = str(uuid.uuid4())[:8]
        dni = self._generate_dni()
        payload = {
            "firstName": "Smoke",
            "lastName": "Test",
            "dni": dni,
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": f"smoke.{unique_id}@test.com",
            "address": "Calle de Prueba Smoke",
        }
        headers = self._get_auth_headers()
        resp = requests.post(
            f"{BASE_URL}/save-participants",
            json=payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        self.assertIn(resp.status_code, [200, 201], f"Fallo al crear participante: {resp.text}")
        data = resp.json()
        self.assertIn("data", data)
        print(f"  SM-07 PASS: Participante creado -> DNI: {dni}")

    # ================================================================
    # SM-08: LISTAR EVALUACIONES ANTROPOMÉTRICAS
    # ================================================================

    def test_sm_08_list_assessments(self):
        """SM-08: El módulo de medidas antropométricas responde.

        Verifica que el endpoint de listado de evaluaciones antropométricas
        responde correctamente.

        Justificación Smoke Test: Confirma que el módulo de evaluaciones
        y sus consultas a BD están operativos.
        """
        headers = self._get_auth_headers()
        resp = requests.get(
            f"{BASE_URL}/list-assessment", headers=headers, timeout=TIMEOUT
        )
        self.assertEqual(resp.status_code, 200)
        print("  SM-08 PASS: Módulo de evaluaciones antropométricas operativo")

    # ================================================================
    # SM-09: LISTAR TESTS DE EVALUACIÓN
    # ================================================================

    def test_sm_09_list_tests(self):
        """SM-09: El módulo de tests de evaluación responde.

        Verifica que el endpoint de listado de tests de rendimiento
        responde correctamente.

        Justificación Smoke Test: Los tests de rendimiento son un
        módulo central del sistema deportivo KALLPA.
        """
        headers = self._get_auth_headers()
        resp = requests.get(
            f"{BASE_URL}/list-test", headers=headers, timeout=TIMEOUT
        )
        self.assertEqual(resp.status_code, 200)
        print("  SM-09 PASS: Módulo de tests de evaluación operativo")

    # ================================================================
    # SM-10: LISTAR HORARIOS DE ASISTENCIA
    # ================================================================

    def test_sm_10_list_schedules(self):
        """SM-10: El módulo de asistencia/horarios responde.

        Verifica que el endpoint de listado de horarios/sesiones
        responde correctamente.

        Justificación Smoke Test: El módulo de asistencia es uno de
        los cinco módulos principales del sistema.
        """
        headers = self._get_auth_headers()
        resp = requests.get(
            f"{BASE_URL}/attendance/v2/public/schedules",
            headers=headers,
            timeout=TIMEOUT,
        )
        self.assertEqual(resp.status_code, 200)
        print("  SM-10 PASS: Módulo de horarios/asistencia operativo")

    # ================================================================
    # SM-11: HISTORIAL DE ASISTENCIA
    # ================================================================

    def test_sm_11_attendance_history(self):
        """SM-11: El historial de asistencia es consultable.

        Verifica que el endpoint de historial de asistencia responde
        correctamente con filtros opcionales.

        Justificación Smoke Test: La consulta de historial es la
        operación de lectura principal del módulo de asistencia.
        """
        headers = self._get_auth_headers()
        resp = requests.get(
            f"{BASE_URL}/attendance/v2/public/history",
            headers=headers,
            timeout=TIMEOUT,
        )
        self.assertEqual(resp.status_code, 200)
        print("  SM-11 PASS: Historial de asistencia consultable")

    # ================================================================
    # SM-12: CONTEO DE PARTICIPANTES ACTIVOS
    # ================================================================

    def test_sm_12_active_participants_count(self):
        """SM-12: El conteo de participantes activos funciona.

        Verifica que el endpoint de estadísticas de participantes
        activos responde correctamente.

        Justificación Smoke Test: Las estadísticas alimentan el
        dashboard principal del sistema.
        """
        headers = self._get_auth_headers()
        resp = requests.get(
            f"{BASE_URL}/participants/active/count",
            headers=headers,
            timeout=TIMEOUT,
        )
        self.assertEqual(resp.status_code, 200)
        print("  SM-12 PASS: Conteo de participantes activos OK")


# ====================================================================
# EJECUCIÓN
# ====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  SMOKE TESTS — KALLPA-UNL Backend")
    print("  Verificación rápida post-despliegue")
    print("=" * 60)
    unittest.main(verbosity=2)
