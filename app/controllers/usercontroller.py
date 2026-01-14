from app.models.participant import Participant
from app.models.responsible import Responsible
from app.models.user import User
from app.services.java_sync_service import java_sync
from app.utils.responses import error_response, success_response
from flask import request
from app import db
from werkzeug.security import generate_password_hash
import uuid

class UserController:
    def _get_token(self):
        """Obtiene el token del header Authorization."""
        auth_header = request.headers.get("Authorization", "")
        return auth_header

    def _is_sequential(self, number_str):
        """
        Verifica si un número es secuencial (ej: 1234567890, 0987654321).
        Retorna True si es secuencial, False si es válido.
        """
        # Patrones secuenciales comunes
        sequential_patterns = [
            "1234567890",
            "0987654321",
            "0123456789",
            "9876543210",
            "1111111111",
            "2222222222",
            "3333333333",
            "4444444444",
            "5555555555",
            "6666666666",
            "7777777777",
            "8888888888",
            "9999999999",
        ]
        
        if number_str in sequential_patterns:
            return True
        
        # Verificar si todos los dígitos son iguales
        if len(set(number_str)) == 1:
            return True
        
        # Verificar secuencia ascendente o descendente
        is_ascending = all(int(number_str[i]) == int(number_str[i-1]) + 1 for i in range(1, len(number_str)))
        is_descending = all(int(number_str[i]) == int(number_str[i-1]) - 1 for i in range(1, len(number_str)))
        
        return is_ascending or is_descending

    def get_users(self):
        try:
            participants = Participant.query.all()

            data = [
                {
                    "external_id": p.external_id,
                    "firstName": p.firstName,
                    "lastName": p.lastName,
                    "email": p.email,
                    "dni": p.dni,
                    "age": p.age,
                    "status": p.status,
                    "type": p.type,
                    "java_external": p.java_external,
                }
                for p in participants
            ]

            return success_response(msg="Usuarios listados correctamente", data=data)
        except Exception:
            return error_response("Error interno del servidor", code=500)

    def create_user(self, data):
        import re
        
        try:
            # ---------- Validación general ----------
            if not data or not isinstance(data, dict):
                return error_response("Datos inválidos", 400)

            # ---------- Campos obligatorios ----------
            required_fields = [
                "firstName",
                "lastName",
                "dni",
                "email",
                "password",
                "role",
            ]

            missing_fields = {}
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    missing_fields[field] = "Campo requerido"

            if missing_fields:
                return error_response(
                    "Campo requerido",
                    code=400,
                    data=missing_fields,
                )

            errors = {}

            # ---------- Validar DNI ----------
            dni = str(data["dni"]).strip()
            if not dni.isdigit():
                errors["dni"] = "DNI debe contener solo números"
            elif len(dni) != 10:
                errors["dni"] = "DNI debe tener exactamente 10 dígitos"
            elif dni == "0000000000":
                errors["dni"] = "DNI no puede ser solo ceros"
            elif self._is_sequential(dni):
                errors["dni"] = "DNI no puede ser un número secuencial"
            elif User.query.filter_by(dni=dni).first():
                errors["dni"] = "El DNI ya está registrado"

            # ---------- Validar Email ----------
            email = str(data["email"]).strip().lower()
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, email):
                errors["email"] = "Formato de correo electrónico inválido"
            elif len(email) > 100:
                errors["email"] = "Email no puede tener más de 100 caracteres"
            elif User.query.filter_by(email=email).first():
                errors["email"] = "El correo ya está registrado"

            # ---------- Validar Nombres ----------
            name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+$'
            firstName = str(data["firstName"]).strip()
            if len(firstName) < 2:
                errors["firstName"] = "Nombre debe tener al menos 2 caracteres"
            elif len(firstName) > 50:
                errors["firstName"] = "Nombre no puede tener más de 50 caracteres"
            elif not re.match(name_pattern, firstName):
                errors["firstName"] = "Nombre solo puede contener letras (sin espacios)"

            lastName = str(data["lastName"]).strip()
            if len(lastName) < 2:
                errors["lastName"] = "Apellido debe tener al menos 2 caracteres"
            elif len(lastName) > 50:
                errors["lastName"] = "Apellido no puede tener más de 50 caracteres"
            elif not re.match(name_pattern, lastName):
                errors["lastName"] = "Apellido solo puede contener letras (sin espacios)"

            # ---------- Validar Password ----------
            password = str(data["password"])
            if len(password) < 6:
                errors["password"] = "Contraseña debe tener al menos 6 caracteres"
            elif len(password) > 50:
                errors["password"] = "Contraseña no puede tener más de 50 caracteres"

            # ---------- Validar rol ----------
            allowed_roles = ["DOCENTE", "PASANTE", "ADMINISTRADOR"]
            if data["role"] not in allowed_roles:
                errors["role"] = f"Rol inválido. Use: {allowed_roles}"

            # ---------- Validar teléfono (opcional) ----------
            phone = data.get("phone")
            if phone:
                phone_str = str(phone).strip()
                if phone_str and phone_str != "NINGUNA":
                    if not phone_str.isdigit():
                        errors["phone"] = "Teléfono debe contener solo números"
                    elif len(phone_str) != 10:
                        errors["phone"] = "Teléfono debe tener exactamente 10 dígitos"
                    elif phone_str == "0000000000":
                        errors["phone"] = "Teléfono no puede ser solo ceros"
                    elif phone_str[0] != "0":
                        errors["phone"] = "Teléfono debe iniciar con 0"
                    elif self._is_sequential(phone_str):
                        errors["phone"] = "Teléfono no puede ser un número secuencial"

            # Si hay errores, retornarlos
            if errors:
                return error_response("Errores de validación", code=400, data=errors)

            # ---------- Hashear contraseña ----------
            hashed_password = generate_password_hash(
                data["password"], method="pbkdf2:sha256", salt_length=16
            )

            # ---------- Valores por defecto ----------
            phone = data.get("phone")
            address = data.get("address")
            phone = phone.strip() if phone and str(phone).strip() else "NINGUNA"
            address = address.strip() if address and str(address).strip() else "NINGUNA"

            # ---------- Crear usuario ----------
            user = User(
                firstName=firstName,
                lastName=lastName,
                dni=dni,
                phone=phone,
                address=address,
                email=email,
                password=hashed_password,
                role=data["role"],
                status="ACTIVO",
            )

            db.session.add(user)
            db.session.commit()

            # ---------- Sincronizar con Java ----------
            token = self._get_token()
            java_synced = False
            if token:
                java_data = {
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "dni": user.dni,
                    "phone": user.phone,
                    "address": user.address,
                    "type": user.role,
                    "email": user.email,
                    "password": data["password"],  # sin hashear
                }

                java_result = java_sync.create_person_with_account(java_data, token)
                if java_result and java_result.get("success"):
                    user.java_external = java_result.get("data", {}).get("external")
                    db.session.commit()
                    java_synced = True
                else:
                    print(
                        f"[UserService] ⚠️ No se pudo sincronizar con Java: {java_result}"
                    )

            return success_response(
                "Usuario registrado correctamente",
                data={
                    "external_id": user.external_id,
                    "role": user.role,
                    "java_synced": java_synced,
                },
                code=200,
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Error interno del servidor: {str(e)}", 500)

    def change_status(self, external_id, new_state):
        """RF010: Cambiar estado (Activar/Inactivar) y sincroniza con Java."""
        token = self._get_token()

        try:
            # Validar que el estado sea válido
            if new_state not in ["ACTIVO", "INACTIVO"]:
                return error_response(
                    msg="Estado inválido. Use ACTIVO o INACTIVO",
                )

            participant = Participant.query.filter_by(external_id=external_id).first()

            if not participant:
                return error_response(
                    msg="Participant not found",
                )

            participant.status = new_state
            db.session.commit()

            java_external = participant.java_external
            if token and java_external:
                java_result = java_sync.change_state(java_external, token)
                if java_result and java_result.get("success"):
                    print(
                        f"[UserServiceDB] Estado sincronizado con Java para {java_external}"
                    )
                else:
                    print(
                        f"[UserServiceDB] No se pudo sincronizar estado con Java: {java_result}"
                    )

            return success_response(
                msg=f"Status updated to {new_state}",
                data={"external_id": participant.external_id},
            )

        except Exception:
            db.session.rollback()
            return error_response(
                msg="Error interno del servidor al cambiar el estado", code=500
            )

    def search_in_java(self, dni):
        token = self._get_token()

        if not token:
            return error_response(msg="Token requerido para buscar en Java", code=401)

        java_result = java_sync.search_by_identification(dni, token)
        if java_result.get("found"):
            return success_response(
                msg="Participante encontrado en Java", data=java_result.get("data")
            )

        return error_response(msg="Participante no encontrado en Java", code=404)

    def create_participant(self, data):
        token = self._get_token()

        try:
            # Determinar si es menor basado en type o age
            # Si viene "participant" como clave, usar esa estructura
            # Si no, usar data directamente
            has_participant_key = "participant" in data and data.get("participant") is not None
            
            if has_participant_key:
                participant_data = data.get("participant")
                responsible_data = data.get("responsible")
                age = participant_data.get("age", 0) if participant_data else 0
            else:
                participant_data = data
                responsible_data = data.get("responsible")
                age = data.get("age", 0)
            
            # Es menor si tiene menos de 18 años
            is_minor = age < 18

            # 1. Validaciones
            validation_result = self._validate_participant(
                participant_data, responsible_data, is_minor
            )
            if validation_result:
                return validation_result

            # Validate program (Phase 3 requirement)
            valid_programs = ["INICIACION", "FUNCIONAL"]
            program = participant_data.get("program")
            if program and program not in valid_programs:
                return error_response(f"Programa inválido. Use: {valid_programs}")

            # 2. Verificar en Java
            self._check_java_duplicate(participant_data, token)

            # 3. Crear participante
            participant = self._build_participant(participant_data, is_minor, program)
            db.session.add(participant)

            # # 4. Sincronizar Java
            # self._sync_with_java(participant, participant_data, token, is_minor)

            # db.session.add(participant)
            # db.session.flush()

            # 5. Responsable (solo iniciación)
            responsible = None
            if is_minor:
                responsible = self._create_responsible(responsible_data, participant)

            db.session.commit()
            try:
                self._sync_with_java(participant, participant_data, token, is_minor)
            except Exception as e:
                print(f"[Warning] Error sincronizando con Java: {e}")

            return success_response(
                msg="Participante registrado correctamente",
                data={
                    "participant_external_id": participant.external_id,
                    "responsible_external_id": (
                        responsible.external_id if responsible else None
                    ),
                },
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    def _validate_participant(self, participant, responsible, is_minor):
        import re
        
        errors = {}
        required_fields = [
            "firstName",
            "lastName",
            "dni",
            "age",
            "phone",
            "program",
            "email",
            "type",
        ]
        for field in required_fields:
            if not participant.get(field):
                errors[field] = "Campo requerido"

        # ========== VALIDACIÓN DE DNI ==========
        dni = participant.get("dni")
        if dni:
            dni_str = str(dni).strip()
            # Debe ser exactamente 10 dígitos numéricos
            if not dni_str.isdigit():
                errors["dni"] = "DNI debe contener solo números"
            elif len(dni_str) != 10:
                errors["dni"] = "DNI debe tener exactamente 10 dígitos"
            elif dni_str == "0000000000":
                errors["dni"] = "DNI no puede ser solo ceros"
            elif self._is_sequential(dni_str):
                errors["dni"] = "DNI no puede ser un número secuencial"
            elif Participant.query.filter_by(dni=dni).first():
                errors["dni"] = "El DNI ya está registrado"

        # ========== VALIDACIÓN DE TELÉFONO ==========
        phone = participant.get("phone")
        if phone:
            phone_str = str(phone).strip()
            if not phone_str.isdigit():
                errors["phone"] = "Teléfono debe contener solo números (sin letras ni caracteres especiales)"
            elif len(phone_str) != 10:
                errors["phone"] = "Teléfono debe tener exactamente 10 dígitos"
            elif phone_str == "0000000000":
                errors["phone"] = "Teléfono no puede ser solo ceros"
            elif phone_str[0] != "0":
                errors["phone"] = "Teléfono debe iniciar con 0"
            elif self._is_sequential(phone_str):
                errors["phone"] = "Teléfono no puede ser un número secuencial"

        # ========== VALIDACIÓN DE EMAIL ==========
        email = participant.get("email")
        if email:
            email_str = str(email).strip()
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, email_str):
                errors["email"] = "Formato de correo electrónico inválido"
            elif len(email_str) > 100:
                errors["email"] = "Email no puede tener más de 100 caracteres"
            elif Participant.query.filter_by(email=email).first():
                errors["email"] = "El correo ya está registrado"

        # ========== VALIDACIÓN DE EDAD (1-80 años) ==========
        age = participant.get("age")
        if age is not None:
            try:
                age_int = int(age)
                if age_int < 1:
                    errors["age"] = "Edad debe ser mayor a 0"
                elif age_int > 80:
                    errors["age"] = "Edad máxima permitida es 80 años"
            except (ValueError, TypeError):
                errors["age"] = "Edad debe ser un número válido"

        # ========== VALIDACIÓN DE PROGRAMA SEGÚN EDAD ==========
        # Reglas:
        # - Menores de 16 años: solo INICIACIÓN
        # - 16-17 años: puede FUNCIONAL o INICIACIÓN
        # - 18+ años: solo FUNCIONAL
        program = participant.get("program")
        if age is not None and program:
            try:
                age_int = int(age)
                if age_int < 16 and program == "FUNCIONAL":
                    errors["program"] = "Menores de 16 años solo pueden inscribirse a INICIACIÓN"
                elif age_int >= 18 and program == "INICIACION":
                    errors["program"] = "Mayores de 18 años solo pueden inscribirse a FUNCIONAL"
            except (ValueError, TypeError):
                pass  # Ya se validó arriba

        # ========== VALIDACIÓN DE NOMBRES (sin caracteres especiales ni espacios) ==========
        firstName = participant.get("firstName")
        if firstName:
            firstName_str = str(firstName).strip()
            # Solo letras y acentos permitidos (sin espacios)
            name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+$'
            if len(firstName_str) < 2:
                errors["firstName"] = "Nombre debe tener al menos 2 caracteres"
            elif len(firstName_str) > 50:
                errors["firstName"] = "Nombre no puede tener más de 50 caracteres"
            elif not re.match(name_pattern, firstName_str):
                errors["firstName"] = "Nombre solo puede contener letras (sin espacios) y no puede contener caracteres no permitidos"
        
        lastName = participant.get("lastName")
        if lastName:
            lastName_str = str(lastName).strip()
            name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+$'
            if len(lastName_str) < 2:
                errors["lastName"] = "Apellido debe tener al menos 2 caracteres"
            elif len(lastName_str) > 50:
                errors["lastName"] = "Apellido no puede tener más de 50 caracteres"
            elif not re.match(name_pattern, lastName_str):
                errors["lastName"] = "Apellido solo puede contener letras (sin espacios) y no puede contener caracteres no permitidos"

        # ========== VALIDACIÓN DE DIRECCIÓN ==========
        address = participant.get("address")
        if address:
            address_str = str(address).strip()
            if len(address_str) > 200:
                errors["address"] = "Dirección no puede tener más de 200 caracteres"
            # No caracteres peligrosos para SQL injection o XSS
            dangerous_pattern = r'[<>"\';{}]'
            if re.search(dangerous_pattern, address_str):
                errors["address"] = "Dirección contiene caracteres no permitidos"

        # ========== VALIDACIÓN DE TYPE ==========
        valid_types = ["ESTUDIANTE", "EXTERNO", "DOCENTE", "PASANTE"]
        type_val = participant.get("type")
        if type_val and type_val not in valid_types:
            errors["type"] = f"Tipo inválido. Use: {valid_types}"

        # ========== VALIDACIÓN DE PROGRAMA ==========
        valid_programs = ["INICIACION", "FUNCIONAL"]
        if program and program not in valid_programs:
            errors["program"] = f"Programa inválido. Use: {valid_programs}"

        # ========== VALIDACIÓN DE RESPONSABLE (MENORES de 18) ==========
        if is_minor:
            if not responsible:
                errors["responsibleName"] = "Campo requerido"
                errors["responsibleDni"] = "Campo requerido"
                errors["responsiblePhone"] = "Campo requerido"
            else:
                responsible_required = ["name", "dni", "phone"]
                for field in responsible_required:
                    key = "responsible" + field.capitalize()
                    if not responsible.get(field):
                        errors[key] = "Campo requerido"

                # Validar nombre del responsable
                resp_name = responsible.get("name")
                if resp_name:
                    name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ ]+$'
                    if len(resp_name.strip()) < 2:
                        errors["responsibleName"] = "Nombre debe tener al menos 2 caracteres"
                    elif not re.match(name_pattern, resp_name.strip()):
                        errors["responsibleName"] = "Nombre solo puede contener letras"

                # Validar DNI del responsable
                responsible_dni = responsible.get("dni")
                if responsible_dni:
                    dni_str = str(responsible_dni).strip()
                    if not dni_str.isdigit():
                        errors["responsibleDni"] = "DNI debe contener solo números"
                    elif len(dni_str) != 10:
                        errors["responsibleDni"] = "DNI debe tener exactamente 10 dígitos"
                    elif dni_str == "0000000000":
                        errors["responsibleDni"] = "DNI no puede ser solo ceros"
                    elif self._is_sequential(dni_str):
                        errors["responsibleDni"] = "DNI no puede ser un número secuencial"
                    elif Responsible.query.filter_by(dni=responsible_dni).first():
                        errors["responsibleDni"] = "El DNI del responsable ya está registrado"

                # Validar teléfono del responsable
                responsible_phone = responsible.get("phone")
                if responsible_phone:
                    phone_str = str(responsible_phone).strip()
                    if not phone_str.isdigit():
                        errors["responsiblePhone"] = "Teléfono debe contener solo números"
                    elif len(phone_str) != 10:
                        errors["responsiblePhone"] = "Teléfono debe tener exactamente 10 dígitos"
                    elif phone_str == "0000000000":
                        errors["responsiblePhone"] = "Teléfono no puede ser solo ceros"
                    elif phone_str[0] != "0":
                        errors["responsiblePhone"] = "Teléfono debe iniciar con 0"
                    elif self._is_sequential(phone_str):
                        errors["responsiblePhone"] = "Teléfono no puede ser un número secuencial"

                # Validar que DNI del responsable sea diferente al del participante
                participant_dni = participant.get("dni")
                if responsible_dni and participant_dni:
                    if str(responsible_dni).strip() == str(participant_dni).strip():
                        errors["responsibleDni"] = "El DNI del responsable no puede ser igual al del participante"

        if errors:
            return error_response("Errores de validación", data=errors)

        return None

    def _build_participant(self, data, is_minor, program=None):
        return Participant(
            firstName=data.get("firstName"),
            lastName=data.get("lastName"),
            age=data.get("age"),
            dni=data.get("dni"),
            phone=data.get("phone"),
            email=data.get("email") or None,
            address=data.get("address"),
            status="ACTIVO",
            type="INICIACION" if is_minor else data.get("type", "EXTERNO"),
            program=program,
        )

    def _create_responsible(self, data, participant):
        responsible = Responsible(
            name=data.get("name"),
            dni=data.get("dni"),
            phone=data.get("phone"),
            participant_id=participant.id,
        )
        db.session.add(responsible)
        return responsible

    def _check_java_duplicate(self, participant_data, token):
        if not token:
            return

        dni = participant_data.get("dni")
        if not dni:
            return

        java_search = java_sync.search_by_identification(dni, token)
        if java_search.get("found"):
            raise Exception("Participante ya existe en el sistema central")

    def _sync_with_java(self, participant, participant_data, token, is_minor):
        if not token:
            return

        email = participant_data.get("email")
        password = participant_data.get("password")

        if not email:
            email = f"{participant_data.get('dni')}@kallpa.system"

        if not password:
            password = str(uuid.uuid4())[:8]

        java_data = {
            "firstName": participant_data.get("firstName"),
            "lastName": participant_data.get("lastName"),
            "dni": participant_data.get("dni"),
            "phone": participant_data.get("phone", ""),
            "address": participant_data.get("address", ""),
            "type": (
                "INICIACION" if is_minor else participant_data.get("type", "EXTERNO")
            ),
            "email": email,
            "password": password,
        }

        java_result = java_sync.create_person_with_account(java_data, token)

        if java_result and java_result.get("success"):
            participant.java_external = java_result.get("data", {}).get("external")

    def get_profile(self, external_id):
        """
        Obtiene el perfil completo de un usuario por su external_id.
        """
        try:
            db.session.expire_all()
            user = User.query.filter_by(external_id=external_id).first()
            if not user:
                return error_response("Usuario no encontrado", 404)

            return success_response(
                msg="Perfil obtenido correctamente",
                data={
                    "external_id": user.external_id,
                    "email": user.email,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "dni": user.dni,
                    "phone": user.phone,
                    "address": user.address,
                    "role": user.role,
                    "status": user.status,
                },
            )
        except Exception as e:
            print(f"[UserService] Error obteniendo perfil: {str(e)}")
            return error_response(f"Error obteniendo perfil: {str(e)}")

    def update_profile(self, external_id, data, token_auth):
        """
        Actualiza el perfil de un usuario y sincroniza con Java.
        external_id: ID del usuario logueado (de la BD local)
        data: JSON con { firstName, lastName, phone, address, ... }
        token_auth: No se usa - se obtiene token fresco de Java
        """
        import requests

        try:
            print(f"[UserService] Buscando usuario con external_id: {external_id}")

            user = User.query.filter_by(external_id=external_id).first()
            if not user:
                print(f"[UserService] Usuario no encontrado")
                return error_response("Usuario no encontrado", 404)

            print(f"[UserService] Usuario encontrado: {user.firstName} {user.lastName}")

            if "firstName" in data:
                user.firstName = data["firstName"]
            if "lastName" in data:
                user.lastName = data["lastName"]
            if "phone" in data:
                user.phone = data["phone"]
            if "address" in data:
                user.address = data["address"]

            db.session.commit()
            print(f"[UserService] Datos actualizados en BD local")

            java_synced = False
            java_error_msg = None

            try:
                print(
                    f"[UserService] Haciendo login a Java para obtener external y token frescos..."
                )

                java_login_resp = requests.post(
                    "http://localhost:8096/api/person/login",
                    json={
                        "email": user.email,
                        "password": data.get("password", "12345678"),
                    },
                    timeout=5,
                )

                print(
                    f"[UserService] Java login response: {java_login_resp.status_code}"
                )

                if java_login_resp.status_code == 200:
                    java_data = java_login_resp.json().get("data", {})
                    java_external = java_data.get("external")
                    java_token = java_data.get("token")

                    print(f"[UserService] Java external FRESCO: {java_external}")
                    print(
                        f"[UserService] Java token FRESCO: {java_token[:30] if java_token else 'None'}..."
                    )

                    if java_external and java_token:
                        rol_java = "EXTERNOS"
                        if user.role == "ESTUDIANTE":
                            rol_java = "ESTUDIANTES"
                        elif user.role == "DOCENTE":
                            rol_java = "DOCENTES"
                        elif user.role == "ADMINISTRATIVO":
                            rol_java = "ADMINISTRATIVOS"

                        payload_java = {
                            "first_name": user.firstName,
                            "last_name": user.lastName,
                            "external": java_external,
                            "type_identification": "CEDULA",
                            "type_stament": rol_java,
                            "direction": (
                                user.address if user.address else "Sin dirección"
                            ),
                            "phono": user.phone if user.phone else "0000000000",
                        }

                        print(f"[UserService] Payload para Java: {payload_java}")

                        java_resp = java_sync.update_person_in_java(
                            payload_java, java_token
                        )

                        if java_resp and java_resp.get("status") == "success":
                            java_synced = True
                            print(f"[UserService] Sincronizado con Java exitosamente")
                        else:
                            java_error_msg = (
                                java_resp.get("message")
                                if java_resp
                                else "Sin respuesta"
                            )
                            print(f"[UserService] Java update falló: {java_error_msg}")
                    else:
                        java_error_msg = "No se obtuvo external/token de Java"
                else:
                    java_error_msg = f"Login Java falló: {java_login_resp.status_code}"
                    print(f"[UserService] {java_error_msg}")

            except requests.exceptions.RequestException as e:
                java_error_msg = f"Error conexión Java: {str(e)}"
                print(f"[UserService] {java_error_msg}")

            response_data = {
                "external_id": user.external_id,
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "dni": user.dni,
                "phone": user.phone,
                "address": user.address,
                "role": user.role,
                "status": user.status,
                "java_synced": java_synced,
            }

            if java_synced:
                return success_response(
                    msg="Perfil actualizado correctamente", data=response_data
                )
            else:
                return success_response(
                    msg=f"Perfil actualizado localmente. Java: {java_error_msg}",
                    data=response_data,
                )

        except Exception as e:
            db.session.rollback()
            print(f"[UserService] Error: {str(e)}")
            return error_response(f"Error actualizando perfil: {str(e)}")

    def get_active_participants_count(self):
        """
        Devuelve el total de participantes activos mayores y menores de edad.
        """
        try:
            total_adult = Participant.query.filter(
                Participant.age >= 18, Participant.status == "ACTIVO"
            ).count()

            total_minor = Participant.query.filter(
                Participant.age < 18, Participant.status == "ACTIVO"
            ).count()

            return success_response(
                msg="Totales de participantes activos obtenidos correctamente",
                data={"adult": total_adult, "minor": total_minor},
            )

        except Exception as e:
            return error_response("Error interno del servidor", code=500)
