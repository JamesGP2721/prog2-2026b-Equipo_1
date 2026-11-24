import os
import tempfile
import unittest
from almacen import cargar, guardar
from modelo import Alumno, Docente, Materia
from sistema import SistemaEscolar


class PruebasSistemaEscolar(unittest.TestCase):
    """Suite de pruebas unitarias para validar reglas de negocio, contrato y persistencia."""

    def setUp(self):
        """Prepara una instancia limpia del sistema y objetos base antes de cada prueba."""
        self.sistema = SistemaEscolar()
        self.alumno1 = Alumno("220100001", "Ana López", "Ingeniería en Computación")
        self.alumno2 = Alumno("220100002", "Carlos Ruiz", "Ingeniería en Informática")
        self.docente1 = Docente("880100001", "Mtro. Héctor Gómez", "Sistemas")
        self.materia = Materia("CC102", "Programación II", 2)
        self.materia2 = Materia("CC103", "Matemáticas Discretas", 5)

    def test_01_registro_valido_y_polimorfismo(self):
        """Verifica que Alumno y Docente redefinan describir() y se listen correctamente."""
        self.sistema.registrar(self.alumno1)
        self.sistema.registrar(self.docente1)
        self.sistema.registrar(self.materia)
        salida = self.sistema.listar()
        self.assertTrue(any("Alumno [220100001]" in linea for linea in salida))
        self.assertTrue(any("Docente [880100001]" in linea for linea in salida))

    def test_02_rechaza_codigo_invalido(self):
        """Comprueba que se rechacen códigos distintos a 9 dígitos numéricos."""
        with self.assertRaises(ValueError):
            Alumno("12345", "Código Corto", "Informática")
        with self.assertRaises(ValueError):
            Docente("12345678A", "Código con Letra", "Redes")

    def test_03_rechaza_campos_vacios_y_cupo_invalido(self):
        """Comprueba que se rechacen nombres, carreras, departamentos vacíos o cupo <= 0."""
        with self.assertRaises(ValueError):
            Alumno("220100099", "   ", "Informática")
        with self.assertRaises(ValueError):
            Materia("CC105", "", 10)
        with self.assertRaises(ValueError):
            Materia("CC106", "Redes", 0)

    def test_04_rechaza_codigos_y_claves_duplicadas(self):
        """Comprueba que no se permitan códigos de usuario ni claves de materia repetidas."""
        self.sistema.registrar(self.alumno1)
        with self.assertRaises(ValueError):
            self.sistema.registrar(Alumno("220100001", "Otro Nombre", "Otra Carrera"))

        self.sistema.registrar(self.materia)
        with self.assertRaises(ValueError):
            self.sistema.registrar(Materia("CC102", "Duplicada", 5))

    def test_05_asignacion_contrato_y_choque_horario(self):
        """Verifica asignar(id, clave) y la detección de empalmes de horario."""
        self.sistema.registrar(self.alumno1)
        self.sistema.registrar(self.materia)
        self.sistema.registrar(self.materia2)

        self.sistema.asignar("220100001", "CC102", ["Lunes", "Jueves"], "07:00 - 09:00")
        self.assertEqual(
            self.materia.formatear_horario("220100001"),
            "Lunes y Jueves | 07:00 - 09:00",
        )

        with self.assertRaises(ValueError):
            self.sistema.asignar("220100001", "CC103", ["Lunes", "Miércoles"], "07:00 - 09:00")

        self.sistema.asignar("220100001", "CC103")
        self.assertIn("220100001", self.materia2.inscritos)

    def test_06_baja_y_cambio_horario(self):
        """Verifica la baja de una materia y la actualización de bloque horario."""
        self.sistema.registrar(self.alumno1)
        self.sistema.registrar(self.materia)
        self.sistema.asignar("220100001", "CC102", ["Lunes", "Jueves"], "07:00 - 09:00")

        self.sistema.cambiar_horario("220100001", "CC102", ["Martes", "Viernes"], "15:00 - 17:00")
        self.assertEqual(
            self.materia.formatear_horario("220100001"),
            "Martes y Viernes | 15:00 - 17:00",
        )

        self.sistema.dar_de_baja_materia("220100001", "CC102")
        self.assertEqual(self.materia.cupo_disponible, 2)

    def test_07_rechaza_doble_asignacion_y_cupo_lleno(self):
        """Verifica el rechazo por inscripción duplicada o cupo agotado."""
        self.sistema.registrar(self.alumno1)
        self.sistema.registrar(self.alumno2)
        self.sistema.registrar(self.docente1)
        self.sistema.registrar(self.materia)

        self.sistema.asignar("220100001", "CC102")
        with self.assertRaises(ValueError):
            self.sistema.asignar("220100001", "CC102")

        self.sistema.asignar("220100002", "CC102")
        with self.assertRaises(ValueError):
            self.sistema.asignar("880100001", "CC102")

    def test_08_calificaciones_y_contraseñas(self):
        """Valida rango de calificaciones y cambio/restablecimiento de contraseña."""
        self.sistema.registrar(self.alumno1)
        self.sistema.registrar(self.materia)
        self.sistema.asignar("220100001", "CC102")

        with self.assertRaises(ValueError):
            self.sistema.calificar("220100001", "CC102", 105)

        self.sistema.calificar("220100001", "CC102", 95.0)
        self.assertEqual(self.materia.obtener_calificacion("220100001"), 95.0)

        self.sistema.actualizar_password("220100001", "NuevaClave99", "NuevaClave99")
        self.assertFalse(self.alumno1.debe_cambiar_password)

    def test_09_persistencia_contrato_guardar_y_cargar(self):
        """Verifica guardar(sistema, ruta), cargar(sistema, ruta) y arranque sin archivo."""
        nuevo_sistema = SistemaEscolar()
        cargar(nuevo_sistema, "archivo_inexistente_12345.db")
        self.assertEqual(len(nuevo_sistema.obtener_miembros()), 0)

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            ruta_tmp = tmp.name

        try:
            self.sistema.registrar(self.alumno1)
            self.sistema.registrar(self.materia)
            self.sistema.asignar("220100001", "CC102", ["Lunes", "Jueves"], "07:00 - 09:00")
            self.sistema.calificar("220100001", "CC102", 95.0)
            guardar(self.sistema, ruta_tmp)

            cargar(nuevo_sistema, ruta_tmp)
            mat_cargada = nuevo_sistema.buscar_materia("CC102")
            self.assertEqual(
                mat_cargada.formatear_horario("220100001"),
                "Lunes y Jueves | 07:00 - 09:00",
            )
            self.assertEqual(mat_cargada.obtener_calificacion("220100001"), 95.0)
        finally:
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)


if __name__ == "__main__":
    unittest.main()