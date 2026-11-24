from almacen import AlmacenSQLite, Bitacora, cargar as _cargar_almacen, guardar as _guardar_almacen
from modelo import (
    BLOQUES_HORARIO,
    DIAS_SEMANA,
    Alumno,
    Docente,
    Materia,
    MiembroUniversitario,
)


class SistemaEscolar:
    """Coordina las operaciones principales del control escolar mediante las reglas de negocio."""

    def __init__(self):
        """Inicializa las colecciones internas de miembros, materias, bitácora y almacén."""
        self._miembros: dict[str, MiembroUniversitario] = {}
        self._materias: dict[str, Materia] = {}
        self._bitacora = Bitacora()
        self._almacen = AlmacenSQLite()

    @property
    def historial(self) -> tuple[str, ...]:
        """Devuelve los eventos registrados cronológicamente en la bitácora."""
        return self._bitacora.eventos

    def obtener_miembros(self) -> tuple[MiembroUniversitario, ...]:
        """Devuelve una tupla con todos los alumnos y docentes registrados."""
        return tuple(self._miembros.values())

    def obtener_materias(self) -> tuple[Materia, ...]:
        """Devuelve una tupla con todas las materias registradas."""
        return tuple(self._materias.values())

    def buscar_miembro(self, codigo: str) -> MiembroUniversitario | None:
        """Busca y devuelve un miembro universitario por su código de 9 dígitos."""
        return self._miembros.get(str(codigo or "").strip())

    def buscar_materia(self, clave: str) -> Materia | None:
        """Busca y devuelve una materia por su clave única."""
        return self._materias.get(str(clave or "").strip().upper())

    def limpiar(self) -> None:
        """Vacía en memoria los diccionarios de miembros y materias."""
        self._miembros.clear()
        self._materias.clear()

    def _verificar_choque_horario(
        self,
        codigo_miembro: str,
        clave_excluir: str,
        dias: list[str] | tuple[str, ...],
        bloque: str,
    ) -> None:
        """Valida que un miembro no tenga otra materia en el mismo día y bloque horario."""
        dias_nuevos = set(dias or [])
        if not dias_nuevos or not bloque:
            return

        for mat in self._materias.values():
            if mat.clave == clave_excluir:
                continue
            if codigo_miembro in mat.inscritos:
                h_existente = mat.obtener_horario(codigo_miembro)
                if h_existente and h_existente["bloque"] == bloque:
                    empalme = dias_nuevos.intersection(h_existente["dias"])
                    if empalme:
                        dias_texto = ", ".join(d for d in DIAS_SEMANA if d in empalme)
                        raise ValueError(
                            f"Choque de horario: el código '{codigo_miembro}' ya tiene "
                            f"'{mat.clave} - {mat.nombre}' el {dias_texto} de {bloque}."
                        )

    def registrar(self, objeto) -> None:
        """Da de alta un objeto de tipo Alumno, Docente o Materia validando que no exista."""
        if isinstance(objeto, MiembroUniversitario):
            if objeto.codigo in self._miembros:
                raise ValueError(
                    f"Ya existe una persona registrada con el código '{objeto.codigo}'."
                )
            self._miembros[objeto.codigo] = objeto
            self._bitacora.registrar_evento(f"Registrado: {objeto.describir()}")
        elif isinstance(objeto, Materia):
            if objeto.clave in self._materias:
                raise ValueError(
                    f"Ya existe una materia registrada con la clave '{objeto.clave}'."
                )
            self._materias[objeto.clave] = objeto
            self._bitacora.registrar_evento(f"Registrada: {objeto.describir()}")
        else:
            raise ValueError(
                "Solo se pueden registrar objetos de tipo Alumno, Docente o Materia."
            )

    def asignar(
        self,
        identificador: str,
        clave: str,
        dias: list[str] | tuple[str, ...] | None = None,
        bloque: str | None = None,
    ) -> None:
        """Asigna un miembro ya registrado a una materia verificando cupo y horario."""
        codigo = str(identificador).strip() if identificador is not None else ""
        clave_mat = str(clave).strip().upper() if clave is not None else ""

        if codigo not in self._miembros:
            raise ValueError(
                f"No existe ningún alumno o docente registrado con el código '{codigo}'."
            )
        if clave_mat not in self._materias:
            raise ValueError(
                f"No existe ninguna materia registrada con la clave '{clave_mat}'."
            )

        if dias is not None or bloque is not None:
            self._verificar_choque_horario(codigo, clave_mat, dias or [], bloque or "")

        materia = self._materias[clave_mat]
        materia.inscribir(codigo, dias, bloque)

        detalle_h = f" ({materia.formatear_horario(codigo)})" if dias and bloque else ""
        self._bitacora.registrar_evento(
            f"Asignado código '{codigo}' a materia '{clave_mat}'{detalle_h}."
        )

    def cambiar_horario(
        self,
        codigo_miembro: str,
        clave_materia: str,
        dias: list[str] | tuple[str, ...],
        bloque: str,
    ) -> None:
        """Modifica los días y el bloque horario de una materia ya inscrita sin choques."""
        cod = str(codigo_miembro or "").strip()
        clave_mat = str(clave_materia or "").strip().upper()

        if cod not in self._miembros:
            raise ValueError(f"No existe el usuario con código '{cod}'.")
        if clave_mat not in self._materias:
            raise ValueError(f"No existe la materia con clave '{clave_mat}'.")

        self._verificar_choque_horario(cod, clave_mat, dias, bloque)
        materia = self._materias[clave_mat]
        materia.asignar_horario(cod, dias, bloque)
        self._bitacora.registrar_evento(
            f"Horario actualizado para '{cod}' en '{clave_mat}': {materia.formatear_horario(cod)}."
        )

    def dar_de_baja_materia(self, codigo_miembro: str, clave_materia: str) -> None:
        """Da de baja a un alumno o docente de una materia liberando su cupo."""
        cod = str(codigo_miembro or "").strip()
        clave_mat = str(clave_materia or "").strip().upper()

        if cod not in self._miembros:
            raise ValueError(f"No existe el usuario con código '{cod}'.")
        if clave_mat not in self._materias:
            raise ValueError(f"No existe la materia con clave '{clave_mat}'.")

        materia = self._materias[clave_mat]
        materia.dar_de_baja(cod)
        self._bitacora.registrar_evento(
            f"Baja de materia '{clave_mat}' para el código '{cod}'."
        )

    def editar_miembro(self, codigo: str, nuevo_nombre: str, nuevo_detalle: str) -> None:
        """Actualiza el nombre y la carrera o departamento de un miembro registrado."""
        miembro = self.buscar_miembro(codigo)
        if not miembro:
            raise ValueError("Usuario no encontrado.")
        miembro.actualizar_perfil(nuevo_nombre, nuevo_detalle)
        self._bitacora.registrar_evento(f"Perfil editado: {miembro.describir()}")

    def restablecer_password_admin(
        self, codigo: str, nueva_password: str | None = None
    ) -> None:
        """Restablece la contraseña de un usuario desde el panel de administración."""
        miembro = self.buscar_miembro(codigo)
        if not miembro:
            raise ValueError("Usuario no encontrado.")
        miembro.restablecer_password_admin(nueva_password)
        self._bitacora.registrar_evento(
            f"Contraseña restablecida por administrador para '{miembro.codigo}'."
        )

    def eliminar_miembro(self, codigo: str) -> None:
        """Elimina un miembro del sistema y lo da de baja de todas sus materias."""
        cod = str(codigo or "").strip()
        if cod not in self._miembros:
            raise ValueError("Usuario no encontrado.")
        for mat in self._materias.values():
            if cod in mat.inscritos:
                mat.dar_de_baja(cod)
        del self._miembros[cod]
        self._bitacora.registrar_evento(f"Usuario '{cod}' eliminado del sistema.")

    def eliminar_materia(self, clave: str) -> None:
        """Elimina una materia registrada del catálogo del sistema."""
        clv = str(clave or "").strip().upper()
        if clv not in self._materias:
            raise ValueError("Materia no encontrada.")
        del self._materias[clv]
        self._bitacora.registrar_evento(f"Materia '{clv}' eliminada del sistema.")

    def construir_tabla_horario(self, codigo_miembro: str) -> dict[str, dict[str, dict | None]]:
        """Construye la matriz semanal de bloques horarios de 07:00 a 21:00 para un usuario."""
        tabla: dict[str, dict[str, dict | None]] = {
            bloque: {dia: None for dia in DIAS_SEMANA} for bloque in BLOQUES_HORARIO
        }

        for mat in self._materias.values():
            if codigo_miembro in mat.inscritos:
                h = mat.obtener_horario(codigo_miembro)
                if not h:
                    continue

                docente_nombre = "Sin docente asignado"
                for cod_ins in mat.inscritos:
                    m = self.buscar_miembro(cod_ins)
                    if isinstance(m, Docente):
                        docente_nombre = m.nombre
                        break

                bloque = h["bloque"]
                if bloque in tabla:
                    for dia in h["dias"]:
                        if dia in tabla[bloque]:
                            tabla[bloque][dia] = {
                                "clave": mat.clave,
                                "nombre": mat.nombre,
                                "docente": docente_nombre,
                            }
        return tabla

    def calificar(self, codigo_alumno: str, clave_materia: str, calificacion: float) -> None:
        """Registra una calificación válida para un alumno inscrito en una materia."""
        cod = str(codigo_alumno or "").strip()
        clave_mat = str(clave_materia or "").strip().upper()

        miembro = self._miembros.get(cod)
        if not miembro or not isinstance(miembro, Alumno):
            raise ValueError(
                f"El código '{cod}' no corresponde a un alumno registrado."
            )
        if clave_mat not in self._materias:
            raise ValueError(
                f"No existe ninguna materia registrada con la clave '{clave_mat}'."
            )

        materia = self._materias[clave_mat]
        materia.calificar(cod, calificacion)
        self._bitacora.registrar_evento(
            f"Calificación {calificacion} registrada para '{cod}' en '{clave_mat}'."
        )

    def autenticar(self, codigo: str, password: str) -> MiembroUniversitario:
        """Valida las credenciales de acceso de un miembro universitario."""
        cod = str(codigo or "").strip()
        miembro = self._miembros.get(cod)
        if not miembro or not miembro.verificar_password(password):
            raise ValueError("Código o contraseña incorrectos.")
        self._bitacora.registrar_evento(f"Inicio de sesión: {miembro.describir()}")
        return miembro

    def actualizar_password(self, codigo: str, nueva_password: str, confirmacion: str) -> None:
        """Actualiza la contraseña personal de un usuario tras validar las reglas de seguridad."""
        miembro = self.buscar_miembro(codigo)
        if not miembro:
            raise ValueError("Usuario no encontrado.")
        miembro.cambiar_password(nueva_password, confirmacion)
        self._bitacora.registrar_evento(
            f"Contraseña actualizada para el código '{miembro.codigo}'."
        )

    def listar(self) -> list[str]:
        """Imprime en consola todos los miembros y materias registrados y devuelve sus líneas."""
        lineas: list[str] = []
        for miembro in self._miembros.values():
            texto = miembro.describir()
            print(texto)
            lineas.append(texto)

        for materia in self._materias.values():
            texto = materia.describir()
            print(texto)
            lineas.append(texto)

        if not lineas:
            print("No hay registros en el sistema.")

        return lineas

    def guardar(self, ruta: str) -> None:
        """Guarda el estado actual del sistema en la ruta de base de datos indicada."""
        self._almacen.guardar(self, ruta)
        self._bitacora.registrar_evento(f"Base de datos guardada en '{ruta}'.")

    def cargar(self, ruta: str) -> None:
        """Carga el estado del sistema desde la ruta de base de datos indicada."""
        self._almacen.cargar(self, ruta)
        self._bitacora.registrar_evento(f"Base de datos cargada desde '{ruta}'.")


def guardar(sistema: SistemaEscolar, ruta: str) -> None:
    """Función del contrato que guarda el estado del sistema en el archivo indicado."""
    _guardar_almacen(sistema, ruta)


def cargar(sistema: SistemaEscolar, ruta: str) -> None:
    """Función del contrato que carga el estado del sistema desde el archivo indicado."""
    _cargar_almacen(sistema, ruta)