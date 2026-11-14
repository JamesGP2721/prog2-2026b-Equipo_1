import sqlite3
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IBM x CUGDL - Buscador Local</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: #ffffff;
            color: #202124;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 900px;
            margin-top: 60px;
            padding: 0 20px;
            text-align: center;
        }
        .logo-container {
            margin-bottom: 30px;
        }
        .logo-text {
            font-family: Arial, sans-serif;
            font-size: 3rem;
            font-weight: bold;
            color: #0062FF;
            text-transform: uppercase;
            letter-spacing: -2px;
            background: repeating-linear-gradient(
                180deg,
                #0062FF,
                #0062FF 5px,
                #ffffff 5px,
                #ffffff 10px
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .search-box {
            display: flex;
            align-items: center;
            width: 100%;
            max-width: 580px;
            margin: 0 auto;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            padding: 10px 18px;
            box-shadow: 0 1px 6px rgba(32,33,36,.12);
            transition: box-shadow 0.2s;
            background-color: #ffffff;
        }
        .search-box:hover, .search-box:focus-within {
            box-shadow: 0 1px 6px rgba(32,33,36,.28);
            border-color: rgba(223,225,229,0);
        }
        input[type="text"] {
            flex: 1;
            border: none;
            outline: none;
            font-size: 16px;
            color: #202124;
            background: transparent;
        }
        .clear-btn {
            text-decoration: none;
            color: #70757a;
            font-size: 18px;
            font-weight: 500;
            padding: 2px 8px;
            border-left: 1px solid #dfe1e5;
            margin-left: 8px;
            cursor: pointer;
            transition: color 0.15s;
        }
        .clear-btn:hover {
            color: #202124;
        }
        button.search-btn {
            background-color: #f8f9fa;
            border: 1px solid #f8f9fa;
            border-radius: 4px;
            color: #3c4043;
            font-size: 14px;
            margin-top: 20px;
            padding: 10px 20px;
            cursor: pointer;
        }
        button.search-btn:hover {
            border: 1px solid #dadce0;
            box-shadow: 0 1px 1px rgba(0,0,0,.1);
            color: #202124;
        }
        .results-area {
            width: 100%;
            max-width: 900px;
            margin-top: 25px;
            padding: 0 20px 50px 20px;
        }
        .stats {
            color: #70757a;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .no-results-caption {
            color: #70757a;
            font-size: 14px;
            margin-top: 50px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
            background-color: #fff;
            margin-top: 15px;
        }
        th {
            background-color: #f8f9fa;
            color: #5f6368;
            font-weight: 600;
            text-align: left;
            padding: 14px;
            border-bottom: 2px solid #e8eaed;
            font-size: 14px;
        }
        td {
            padding: 14px;
            border-bottom: 1px solid #e8eaed;
            font-size: 14px;
        }
        tr:hover {
            background-color: #f1f3f4;
        }
        .badge {
            background-color: #e8f0fe;
            color: #1967d2;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="logo-container">
            <div class="logo-text">IBM x CUGDL</div>
        </div>
        
        <form method="GET" action="/">
            <div class="search-box">
                <input type="text" name="q" placeholder="Buscar estudiante por nombre, correo, teléfono, carrera..." value="{{ busqueda }}" autofocus>
                {% if busqueda %}
                <a href="/" class="clear-btn" title="Limpiar búsqueda">✕</a>
                {% endif %}
            </div>
            <button type="submit" class="search-btn">Buscar Estudiante</button>
        </form>
    </div>

    {% if resultados is not none %}
    <div class="results-area">
        <div class="stats">Se encontraron <b>{{ resultados|length }}</b> coincidencias para "<b>{{ busqueda }}</b>"</div>
        
        {% if resultados %}
        <table>
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Nombre Completo</th>
                    <th>Carrera</th>
                    <th>Semestre</th>
                    <th>Correo Institucional</th>
                    <th>WhatsApp</th>
                </tr>
            </thead>
            <tbody>
                {% for row in resultados %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td><b>{{ row[1] }}</b></td>
                    <td><span class="badge">{{ row[2] }}</span></td>
                    <td>{{ row[3] }}</td>
                    <td>{{ row[4] }}</td>
                    <td>{{ row[5] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
    {% else %}
    <div class="no-results-caption">Utiliza el buscador de arriba para filtrar los resultados.</div>
    {% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    busqueda = request.args.get("q", "").strip()
    resultados = None

    if busqueda:
        conn = sqlite3.connect("estudiantes_ibm.db")
        cursor = conn.cursor()
        
        query = """
        SELECT 
            e.codigo_estudiante,
            e.nombre_completo,
            c.nombre_carrera,
            e.semestre,
            co.correo_institucional,
            co.telefono_whatsapp
        FROM Estudiantes e
        JOIN Carreras c ON e.id_carrera = c.id_carrera
        JOIN Contacto co ON e.id_estudiante = co.id_estudiante
        WHERE e.nombre_completo LIKE ? 
           OR e.codigo_estudiante LIKE ?
           OR c.nombre_carrera LIKE ?
           OR co.correo_institucional LIKE ?
           OR co.telefono_whatsapp LIKE ?
        """
        parametro = f"%{busqueda}%"
        cursor.execute(query, (parametro, parametro, parametro, parametro, parametro))
        resultados = cursor.fetchall()
        conn.close()

    return render_template_string(HTML_TEMPLATE, busqueda=busqueda, resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True, port=8080)