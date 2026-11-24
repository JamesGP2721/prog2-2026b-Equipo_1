BLOQUES_HORARIO = (
    "07:00 - 09:00",
    "09:00 - 11:00",
    "11:00 - 13:00",
    "13:00 - 15:00",
    "15:00 - 17:00",
    "17:00 - 19:00",
    "19:00 - 21:00",
)

DIAS_SEMANA = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")


class MiembroUniversitario:
    """Representa a una persona vinculada con la institución educativa."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        password: str | None = None,
        debe_cambiar_password: bool = True,
    ):
        """Inicializa un miembro universitario validando su código de 9 dígitos y su nombre."""
        codigo_limpio = str(codigo).strip() if codigo is not None else ""
        nombre_limpio = " ".join(str(nombre).split()) if nombre is not None else ""

        if len(codigo_limpio) != 9 or not codigo_limpio.isdigit():
            raise ValueError(
                f"El código '{codigo}' es inválido: debe contener exactamente 9 dígitos numéricos."
            )
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío.")

        self._codigo = codigo_limpio
        self._nombre = nombre_limpio
        self._password = password if password else codigo_limpio
        self._debe_cambiar_password = bool(debe_cambiar_password)

    @property
    def codigo(self) -> str:
        """Devuelve el código institucional de 9 dígitos."""
        return self._codigo

    @property
    def nombre(self) -> str:
        """Devuelve el nombre completo del miembro universitario."""
        return self._nombre

    @property
    def debe_cambiar_password(self) -> bool:
        """Indica si el usuario aún debe cambiar su contraseña inicial."""
        return self._debe_cambiar_password

    def actualizar_datos_basicos(self, nuevo_nombre: str) -> None:
        """Actualiza el nombre del miembro universitario tras validar que no esté vacío."""
        nombre_limpio = " ".join(str(nuevo_nombre).split()) if nuevo_nombre is not None else ""
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = nombre_limpio

    def verificar_password(self, password: str) -> bool:
        """Comprueba si la contraseña proporcionada coincide con la almacenada."""
        return self._password == str(password or "")

    def obtener_password_almacenada(self) -> str:
        """Devuelve la contraseña actualmente almacenada para persistencia o administración."""
        return self._password

    def cambiar_password(self, nueva_password: str, confirmacion: str) -> None:
        """Cambia la contraseña del usuario validando longitud, diferencia y confirmación."""
        nueva = str(nueva_password or "").strip()
        conf = str(confirmacion or "").strip()

        if len(nueva) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres.")
        if nueva == self._password:
            raise ValueError("La nueva contraseña debe ser diferente a la actual.")
        if nueva != conf:
            raise ValueError("Las contraseñas no coinciden.")

        self._password = nueva
        self._debe_cambiar_password = False

    def restablecer_password_admin(self, nueva_password: str | None = None) -> None:
        """Restablece la contraseña al código inicial o asigna una nueva desde administración."""
        if nueva_password is None or not str(nueva_password).strip():
            self._password = self._codigo
            self._debe_cambiar_password = True
        else:
            nueva = str(nueva_password).strip()
            if len(nueva) < 6:
                raise ValueError("La contraseña asignada debe tener al menos 6 caracteres.")
            self._password = nueva
            self._debe_cambiar_password = False

    def describir(self) -> str:
        """Devuelve una representación textual básica del miembro universitario."""
        return f"[{self._codigo}] {self._nombre}"


class Alumno(MiembroUniversitario):
    """Modela a un estudiante matriculado en una carrera académica."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        carrera: str,
        password: str | None = None,
        debe_cambiar_password: bool = True,
    ):
        """Inicializa un alumno validando sus datos heredados y su carrera."""
        super().__init__(codigo, nombre, password, debe_cambiar_password)
        carrera_limpia = " ".join(str(carrera).split()) if carrera is not None else ""
        if not carrera_limpia:
            raise ValueError("La carrera del alumno no puede estar vacía.")
        self._carrera = carrera_limpia

    @property
    def carrera(self) -> str:
        """Devuelve la carrera académica en la que está inscrito el alumno."""
        return self._carrera

    def actualizar_perfil(self, nuevo_nombre: str, nueva_carrera: str) -> None:
        """Actualiza el nombre y la carrera del alumno."""
        carrera_limpia = " ".join(str(nueva_carrera).split()) if nueva_carrera is not None else ""
        if not carrera_limpia:
            raise ValueError("La carrera del alumno no puede estar vacía.")
        self.actualizar_datos_basicos(nuevo_nombre)
        self._carrera = carrera_limpia

    def describir(self) -> str:
        """Devuelve la descripción formateada del alumno incluyendo su carrera."""
        return f"Alumno {super().describir()} | Carrera: {self._carrera}"


class Docente(MiembroUniversitario):
    """Modela a un profesor adscrito a un departamento académico."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        departamento: str,
        password: str | None = None,
        debe_cambiar_password: bool = True,
    ):
        """Inicializa un docente validando sus datos heredados y su departamento."""
        super().__init__(codigo, nombre, password, debe_cambiar_password)
        depto_limpio = " ".join(str(departamento).split()) if departamento is not None else ""
        if not depto_limpio:
            raise ValueError("El departamento del docente no puede estar vacío.")
        self._departamento = depto_limpio

    @property
    def departamento(self) -> str:
        """Devuelve el departamento académico al que pertenece el docente."""
        return self._departamento

    def actualizar_perfil(self, nuevo_nombre: str, nuevo_departamento: str) -> None:
        """Actualiza el nombre y el departamento del docente."""
        depto_limpio = (
            " ".join(str(nuevo_departamento).split()) if nuevo_departamento is not None else ""
        )
        if not depto_limpio:
            raise ValueError("El departamento del docente no puede estar vacío.")
        self.actualizar_datos_basicos(nuevo_nombre)
        self._departamento = depto_limpio

    def describir(self) -> str:
        """Devuelve la descripción formateada del docente incluyendo su departamento."""
        return f"Docente {super().describir()} | Departamento: {self._departamento}"


class Materia:
    """Administra una asignatura con clave única, límite de cupo, calificaciones y horarios."""

    def __init__(self, clave: str, nombre: str, cupo_maximo: int):
        """Inicializa una materia validando su clave, nombre y cupo máximo positivo."""
        clave_limpia = str(clave).strip().upper() if clave is not None else ""
        nombre_limpio = " ".join(str(nombre).split()) if nombre is not None else ""

        if not clave_limpia:
            raise ValueError("La clave de la materia no puede estar vacía.")
        if not nombre_limpio:
            raise ValueError("El nombre de la materia no puede estar vacío.")
        if isinstance(cupo_maximo, bool) or not isinstance(cupo_maximo, int) or cupo_maximo <= 0:
            raise ValueError("El cupo máximo debe ser un número entero mayor a cero.")

        self._clave = clave_limpia
        self._nombre = nombre_limpio
        self._cupo_maximo = cupo_maximo
        self._inscritos: list[str] = []
        self._calificaciones: dict[str, float] = {}
        self._horarios: dict[str, dict] = {}

    @property
    def clave(self) -> str:
        """Devuelve la clave única de la materia en mayúsculas."""
        return self._clave

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la asignatura."""
        return self._nombre

    @property
    def cupo_maximo(self) -> int:
        """Devuelve el límite máximo de integrantes permitidos en la materia."""
        return self._cupo_maximo

    @property
    def inscritos(self) -> tuple[str, ...]:
        """Devuelve una tupla inmutable con los códigos inscritos en la materia."""
        return tuple(self._inscritos)

    @property
    def cupo_disponible(self) -> int:
        """Calcula cuántos lugares disponibles quedan en la materia."""
        return self._cupo_maximo - len(self._inscritos)

    @property
    def calificaciones(self) -> dict[str, float]:
        """Devuelve una copia del diccionario de calificaciones registradas."""
        return dict(self._calificaciones)

    @property
    def horarios(self) -> dict[str, dict]:
        """Devuelve una copia de los horarios asignados por código inscrito."""
        return {k: dict(v) for k, v in self._horarios.items()}

    def inscribir(
        self,
        codigo_miembro: str,
        dias: list[str] | tuple[str, ...] | None = None,
        bloque: str | None = None,
    ) -> None:
        """Inscribe un código en la materia verificando duplicados, cupo y horario opcional."""
        if codigo_miembro in self._inscritos:
            raise ValueError(
                f"El código '{codigo_miembro}' ya se encuentra asignado en la materia '{self._clave}'."
            )
        if len(self._inscritos) >= self._cupo_maximo:
            raise ValueError(
                f"Cupo lleno en la materia '{self._clave}' ({self._nombre}): máximo {self._cupo_maximo}."
            )

        self._inscritos.append(codigo_miembro)
        if dias is not None or bloque is not None:
            try:
                self.asignar_horario(codigo_miembro, dias or [], bloque or "")
            except ValueError:
                self._inscritos.remove(codigo_miembro)
                raise

    def asignar_horario(
        self,
        codigo_miembro: str,
        dias: list[str] | tuple[str, ...],
        bloque: str,
    ) -> None:
        """Asigna o actualiza los días y el bloque horario de un miembro inscrito."""
        if codigo_miembro not in self._inscritos:
            raise ValueError(
                f"El código '{codigo_miembro}' no está inscrito en la materia '{self._clave}'."
            )

        bloque_limpio = str(bloque or "").strip()
        if bloque_limpio not in BLOQUES_HORARIO:
            raise ValueError(
                f"El bloque horario '{bloque}' no es válido. Usa bloques de 2 horas de 07:00 a 21:00."
            )

        dias_filtrados = [d for d in DIAS_SEMANA if d in set(dias or [])]
        if not dias_filtrados:
            raise ValueError("Debes seleccionar al menos un día de la semana (Lunes a Sábado).")

        self._horarios[codigo_miembro] = {
            "dias": tuple(dias_filtrados),
            "bloque": bloque_limpio,
        }

    def obtener_horario(self, codigo_miembro: str) -> dict | None:
        """Devuelve el diccionario de días y bloque horario asignado a un código."""
        h = self._horarios.get(codigo_miembro)
        return dict(h) if h else None

    def formatear_horario(self, codigo_miembro: str) -> str:
        """Devuelve una cadena legible con los días y el bloque horario del miembro."""
        h = self._horarios.get(codigo_miembro)
        if not h:
            return "Sin horario asignado"
        dias = h["dias"]
        if len(dias) == 1:
            texto_dias = dias[0]
        else:
            texto_dias = ", ".join(dias[:-1]) + " y " + dias[-1]
        return f"{texto_dias} | {h['bloque']}"

    def horario_referencia(self) -> dict | None:
        """Devuelve el primer horario registrado en la materia como referencia de grupo."""
        if not self._horarios:
            return None
        primero = next(iter(self._horarios.values()))
        return dict(primero)

    def dar_de_baja(self, codigo_miembro: str) -> None:
        """Elimina a un miembro de la materia y libera su lugar, horario y calificación."""
        if codigo_miembro not in self._inscritos:
            raise ValueError(
                f"El código '{codigo_miembro}' no está inscrito en la materia '{self._clave}'."
            )
        self._inscritos.remove(codigo_miembro)
        self._calificaciones.pop(codigo_miembro, None)
        self._horarios.pop(codigo_miembro, None)

    def calificar(self, codigo_alumno: str, calificacion: float) -> None:
        """Registra una calificación entre 0 y 100 para un alumno inscrito."""
        if codigo_alumno not in self._inscritos:
            raise ValueError(
                f"El alumno '{codigo_alumno}' no está inscrito en la materia '{self._clave}'."
            )
        if isinstance(calificacion, bool) or not isinstance(calificacion, (int, float)):
            raise ValueError("La calificación debe ser un valor numérico.")
        if calificacion < 0 or calificacion > 100:
            raise ValueError("La calificación debe estar entre 0 y 100.")
        self._calificaciones[codigo_alumno] = round(float(calificacion), 2)

    def obtener_calificacion(self, codigo_alumno: str) -> float | None:
        """Devuelve la calificación registrada de un alumno o None si aún no tiene."""
        return self._calificaciones.get(codigo_alumno)

    def describir(self) -> str:
        """Devuelve una descripción resumida de la materia y su ocupación actual."""
        return (
            f"Materia [{self._clave}] {self._nombre} | "
            f"Cupo: {len(self._inscritos)}/{self._cupo_maximo}"
        )