from almacen import cargar, guardar
from modelo import Alumno, Docente, Materia
from sistema import SistemaEscolar

RUTA_BD = "sistema_escolar.db"


def main() -> None:
    """Ejecuta una demostración completa de persistencia, registro, asignación y listado."""
    sistema = SistemaEscolar()
    cargar(sistema, RUTA_BD)

    if not sistema.obtener_miembros() and not sistema.obtener_materias():
        print("=== INICIALIZANDO DATOS DE PRUEBA EN EL SISTEMA ESCOLAR ===")
        alumno = Alumno("220123456", "Alex Ramírez", "Ingeniería en Ciberseguridad")
        docente = Docente("900100201", "Dra. Elena Paredes", "Ciencias Computacionales")
        materia = Materia("PROG2", "Programación II", 30)

        sistema.registrar(alumno)
        sistema.registrar(docente)
        sistema.registrar(materia)

        sistema.asignar("220123456", "PROG2", ["Lunes", "Jueves"], "07:00 - 09:00")
        sistema.asignar("900100201", "PROG2", ["Lunes", "Jueves"], "07:00 - 09:00")
        guardar(sistema, RUTA_BD)
    else:
        print("=== DATOS RECUPERADOS DESDE LA BASE DE DATOS ===")

    sistema.listar()


if __name__ == "__main__":
    main()