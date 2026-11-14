SELECT 
    e.nombre_completo AS Estudiante,
    c.nombre_carrera AS Carrera,
    co.correo_institucional AS Correo,
    co.telefono_whatsapp AS Telefono
FROM Estudiantes e
JOIN Carreras c ON e.id_carrera = c.id_carrera
JOIN Contacto co ON e.id_estudiante = co.id_estudiante;
