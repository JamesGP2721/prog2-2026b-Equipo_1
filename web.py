import os
from flask import (
    Flask,
    redirect,
    render_template_string,
    request,
    send_from_directory,
    session,
    url_for,
)
from almacen import AlmacenSQLite
from modelo import BLOQUES_HORARIO, DIAS_SEMANA, Alumno, Docente, Materia
from sistema import SistemaEscolar

app = Flask(__name__)
app.secret_key = "udg_cugdl_control_escolar_admin_james"
RUTA_BD = "sistema_escolar.db"

ADMIN_USER = "Admin-James"
ADMIN_PASS = "admin James"


def cargar_sistema() -> SistemaEscolar:
    """Carga y devuelve una instancia actualizada del sistema escolar desde SQLite."""
    sistema = SistemaEscolar()
    sistema.cargar(RUTA_BD)
    return sistema


SHARED_SIIUU_STYLE = """
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    background: #f4f6f9;
    color: #1e293b;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .siiuu-navbar {
    background: #162238;
    color: #ffffff;
    height: 62px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
  }
  .siiuu-nav-left { display: flex; align-items: center; gap: 16px; }
  .siiuu-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: #ffffff;
    font-weight: 800;
    font-size: 21px;
    letter-spacing: 0.4px;
  }
  .siiuu-tag {
    background: #0ea5e9;
    color: #0f172a;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
  }
  .siiuu-sub {
    font-size: 12.5px;
    color: #cbd5e1;
    border-left: 1px solid rgba(255, 255, 255, 0.18);
    padding-left: 14px;
    text-transform: uppercase;
  }
  .siiuu-nav-right { display: flex; align-items: center; gap: 14px; font-size: 13px; }
  .siiuu-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #38bdf8;
    color: #0f172a;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .siiuu-logout {
    color: #e2e8f0;
    text-decoration: none;
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 6px 12px;
    border-radius: 7px;
    font-size: 12.5px;
    font-weight: 600;
  }
  .siiuu-logout:hover { background: rgba(255, 255, 255, 0.1); }
  .siiuu-body { display: flex; flex: 1; }
  .siiuu-sidebar {
    width: 245px;
    background: #1c2841;
    color: #cbd5e1;
    padding: 18px 0;
    flex-shrink: 0;
  }
  .siiuu-side-item {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 12px 20px;
    color: #cbd5e1;
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 500;
    border-left: 3px solid transparent;
  }
  .siiuu-side-item:hover { background: rgba(255, 255, 255, 0.06); color: #ffffff; }
  .siiuu-side-item.active {
    background: #2d3a56;
    color: #ffffff;
    border-left-color: #38bdf8;
    font-weight: 600;
  }
  .siiuu-main {
    flex: 1;
    padding: 26px 32px 60px;
    max-width: 1180px;
    margin: 0 auto;
    width: 100%;
  }
  .siiuu-alert {
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    margin-bottom: 18px;
    border: 1px solid;
  }
  .siiuu-alert.ok { background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }
  .siiuu-alert.err { background: #fef2f2; color: #991b1b; border-color: #fecaca; }
  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px;
    margin-bottom: 22px;
  }
  .kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  }
  .kpi-card small {
    display: block;
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 4px;
  }
  .kpi-card strong { font-size: 24px; color: #0f294a; }
  .grid-3 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 18px;
    margin-bottom: 20px;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 18px;
    margin-bottom: 16px;
  }
  .siiuu-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  }
  .siiuu-card.highlight { border: 2px solid #005596; }
  .siiuu-card-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
  }
  .siiuu-card-header h3 { margin: 0; font-size: 16px; color: #0f294a; }
  label {
    display: block;
    font-size: 12.5px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 5px;
  }
  input[type="text"], input[type="password"], input[type="number"], select {
    width: 100%;
    padding: 9px 12px;
    margin-bottom: 13px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 13.5px;
    background: #ffffff;
  }
  input:focus, select:focus {
    outline: none;
    border-color: #005596;
    box-shadow: 0 0 0 3px rgba(0, 85, 150, 0.12);
  }
  .days-box {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 14px;
  }
  .day-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
    cursor: pointer;
    user-select: none;
  }
  .day-chip input { margin: 0; width: auto; }
  .btn-primary {
    width: 100%;
    background: #005596;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn-primary:hover { background: #003f70; }
  .btn-sm {
    background: #005596;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    padding: 7px 13px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
  }
  .btn-sm:hover { background: #003f70; }
  .btn-danger {
    background: #dc2626;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    padding: 7px 12px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn-danger:hover { background: #b91c1c; }
  .btn-outline {
    background: #ffffff;
    color: #374151;
    border: 1px solid #cbd5e1;
    padding: 7px 13px;
    font-size: 12.5px;
    border-radius: 7px;
    font-weight: 600;
    text-decoration: none;
    display: inline-block;
    cursor: pointer;
  }
  .btn-outline:hover { background: #f1f5f9; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th {
    background: #f8fafc;
    color: #475569;
    text-align: left;
    padding: 10px 12px;
    border-bottom: 2px solid #e2e8f0;
  }
  td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }
  .sched-table th, .sched-table td {
    border: 1px solid #e2e8f0;
    text-align: center;
    padding: 9px 8px;
  }
  .sched-slot {
    background: #e0f2fe;
    border: 1px solid #bae6fd;
    color: #0369a1;
    border-radius: 7px;
    padding: 6px 8px;
    font-size: 12px;
    line-height: 1.35;
  }
  .grade-form { display: flex; align-items: center; gap: 8px; margin: 0; }
  .grade-input {
    width: 92px !important;
    margin-bottom: 0 !important;
    padding: 7px 10px !important;
    font-weight: 600;
    text-align: center;
  }
  .pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    background: #e0f2fe;
    color: #0369a1;
  }
  .pill.aprob { background: #dcfce7; color: #166534; }
  .pill.reprob { background: #fee2e2; color: #b91c1c; }
  .pill.pend { background: #fef3c7; color: #92400e; }
  .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
  .info-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 13px 15px;
  }
  .info-box small {
    display: block;
    color: #64748b;
    font-size: 11.5px;
    font-weight: 600;
    margin-bottom: 4px;
    text-transform: uppercase;
  }
  .info-box strong { font-size: 14.5px; color: #0f294a; }
  .log-box {
    max-height: 320px;
    overflow-y: auto;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
    font-family: monospace;
    font-size: 12.5px;
  }
  .log-item { padding: 5px 0; border-bottom: 1px dashed #cbd5e1; }
  .user-link { color: #005596; font-weight: 700; text-decoration: none; }
  .user-link:hover { text-decoration: underline; }
  .siiuu-footer {
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    padding: 12px 24px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 28px;
  }
  .siiuu-footer img { height: 40px; width: auto; object-fit: contain; }
  .siiuu-footer-sep { width: 1px; height: 30px; background: #cbd5e1; }
</style>
"""

AUTH_STYLE = """
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    background: #f4f6f9;
    color: #1f2937;
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .siiuu-navbar {
    background: #162238;
    color: #ffffff;
    height: 62px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
  }
  .siiuu-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #ffffff;
    font-weight: 800;
    font-size: 21px;
    letter-spacing: 0.4px;
  }
  .siiuu-tag {
    background: #0ea5e9;
    color: #0f172a;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
  }
  .auth-wrapper {
    width: 100%;
    max-width: 420px;
    margin: auto;
    padding: 24px 16px 48px;
  }
  .auth-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 28px 26px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
  }
  .auth-card h2 {
    margin: 0 0 6px;
    font-size: 20px;
    color: #0f294a;
    text-align: center;
  }
  .auth-desc {
    margin: 0 0 20px;
    font-size: 13.5px;
    color: #64748b;
    text-align: center;
  }
  label {
    display: block;
    font-size: 12.5px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 5px;
  }
  input[type="text"], input[type="password"] {
    width: 100%;
    padding: 10px 12px;
    margin-bottom: 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 13.5px;
    background: #ffffff;
  }
  input:focus {
    outline: none;
    border-color: #005596;
    box-shadow: 0 0 0 3px rgba(0, 85, 150, 0.12);
  }
  .btn {
    width: 100%;
    background: #005596;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn:hover { background: #003f70; }
  .alert {
    padding: 11px 14px;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    margin-bottom: 16px;
    border: 1px solid;
  }
  .alert.ok { background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }
  .alert.err { background: #fef2f2; color: #991b1b; border-color: #fecaca; }
  .first-login-box {
    margin-bottom: 16px;
    padding: 11px 13px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    font-size: 12.5px;
    color: #1e3a8a;
    line-height: 1.45;
  }
  .siiuu-footer {
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    padding: 12px 24px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 28px;
  }
  .siiuu-footer img { height: 40px; width: auto; object-fit: contain; }
  .siiuu-footer-sep { width: 1px; height: 30px; background: #cbd5e1; }
</style>
"""

FOOTER_HTML = """
<footer class="siiuu-footer">
  <img src="/logo/udg" alt="Universidad de Guadalajara">
  <div class="siiuu-footer-sep"></div>
  <img src="/logo/cugdl" alt="Centro Universitario de Guadalajara">
</footer>
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIIUU — Iniciar Sesión | UDG CUGDL</title>
__STYLE__
</head>
<body>
<header class="siiuu-navbar">
  <div class="siiuu-brand">
    SIIUU <span class="siiuu-tag">Control Escolar</span>
  </div>
  <span style="font-size:12.5px; color:#cbd5e1;">Centro Universitario de Guadalajara</span>
</header>

<div class="auth-wrapper">
  <div class="auth-card">
    <h2>Iniciar Sesión</h2>
    <p class="auth-desc">Acceso institucional SIIUU</p>
    {% if msg %}
      <div class="alert {{ 'err' if err else 'ok' }}">{{ msg }}</div>
    {% endif %}
    <form method="POST" action="/login" autocomplete="off">
      <input type="text" name="decoy_user" style="display:none;" tabindex="-1" autocomplete="off">
      <input type="password" name="decoy_pass" style="display:none;" tabindex="-1" autocomplete="off">

      <label>Usuario o Código</label>
      <input
        type="text"
        name="usuario_siiuu"
        placeholder="Ingresa tu usuario o código"
        autocomplete="off"
        autocapitalize="off"
        spellcheck="false"
        readonly
        onfocus="this.removeAttribute('readonly');"
        required
      >

      <label>Contraseña</label>
      <input
        type="password"
        name="clave_siiuu"
        placeholder="Ingresa tu contraseña"
        autocomplete="new-password"
        readonly
        onfocus="this.removeAttribute('readonly');"
        required
      >
      <button type="submit" class="btn">Entrar al sistema</button>
    </form>
  </div>
</div>
__FOOTER__
</body>
</html>""".replace("__STYLE__", AUTH_STYLE).replace("__FOOTER__", FOOTER_HTML)

CAMBIAR_PASS_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIIUU — Cambio de Contraseña</title>
__STYLE__
</head>
<body>
<header class="siiuu-navbar">
  <div class="siiuu-brand">
    SIIUU <span class="siiuu-tag">Seguridad</span>
  </div>
  <span style="font-size:12.5px; color:#cbd5e1;">{{ usuario.codigo }}</span>
</header>

<div class="auth-wrapper">
  <div class="auth-card">
    <h2>Cambio Obligatorio de Contraseña</h2>
    <p class="auth-desc">
      Bienvenido, <b>{{ usuario.nombre }}</b> ({{ usuario.codigo }})
    </p>
    <div class="first-login-box">
      <b>Primer acceso:</b> Como iniciaste sesión con tu código de 9 dígitos como contraseña inicial, registra una contraseña personal nueva antes de continuar.
    </div>
    {% if msg %}
      <div class="alert err">{{ msg }}</div>
    {% endif %}
    <form method="POST" action="/cambiar_password" autocomplete="off">
      <label>Nueva contraseña (mínimo 6 caracteres)</label>
      <input
        type="password"
        name="nueva_password"
        placeholder="Escribe tu nueva contraseña"
        autocomplete="new-password"
        readonly
        onfocus="this.removeAttribute('readonly');"
        required
      >
      <label>Confirmar nueva contraseña</label>
      <input
        type="password"
        name="confirmacion"
        placeholder="Repite tu nueva contraseña"
        autocomplete="new-password"
        readonly
        onfocus="this.removeAttribute('readonly');"
        required
      >
      <button type="submit" class="btn">Guardar contraseña y entrar</button>
    </form>
    <div style="margin-top: 14px; text-align: center;">
      <a href="/logout" style="font-size: 13px; color: #64748b; text-decoration: none;">Cancelar y cerrar sesión</a>
    </div>
  </div>
</div>
__FOOTER__
</body>
</html>""".replace("__STYLE__", AUTH_STYLE).replace("__FOOTER__", FOOTER_HTML)

ADMIN_PANEL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIIUU Administrador — UDG | CUGDL</title>
__STYLE__
</head>
<body>
  <header class="siiuu-navbar">
    <div class="siiuu-nav-left">
      <a href="/?tab=altas" class="siiuu-brand">
        SIIUU <span class="siiuu-tag">Administrador</span>
      </a>
      <div class="siiuu-sub">Control Escolar CUGDL</div>
    </div>
    <div class="siiuu-nav-right">
      <span>Admin-James</span>
      <div class="siiuu-avatar">A</div>
      <a href="/logout" class="siiuu-logout">Cerrar sesión</a>
    </div>
  </header>

  <div class="siiuu-body">
    <aside class="siiuu-sidebar">
      <a href="/?tab=altas" class="siiuu-side-item {{ 'active' if tab == 'altas' else '' }}">
        <span>&#10133;</span> Altas y Asignaciones
      </a>
      <a href="/?tab=usuarios" class="siiuu-side-item {{ 'active' if tab == 'usuarios' else '' }}">
        <span>&#128101;</span> Expedientes de Usuarios
      </a>
      <a href="/?tab=materias" class="siiuu-side-item {{ 'active' if tab == 'materias' else '' }}">
        <span>&#128218;</span> Catálogo de Materias
      </a>
      <a href="/?tab=bitacora" class="siiuu-side-item {{ 'active' if tab == 'bitacora' else '' }}">
        <span>&#128221;</span> Bitácora y Sistema
      </a>
    </aside>

    <main class="siiuu-main">
      {% if msg %}
        <div class="siiuu-alert {{ 'err' if err else 'ok' }}">{{ msg }}</div>
      {% endif %}

      <div class="kpi-row">
        <div class="kpi-card">
          <small>Alumnos Registrados</small>
          <strong>{{ total_alumnos }}</strong>
        </div>
        <div class="kpi-card">
          <small>Docentes Registrados</small>
          <strong>{{ total_docentes }}</strong>
        </div>
        <div class="kpi-card">
          <small>Materias Activas</small>
          <strong>{{ materias|length }}</strong>
        </div>
      </div>

      {% if tab == 'altas' %}
        <div class="grid-3">
          <div class="siiuu-card">
            <div class="siiuu-card-header">
              <h3>1. Dar de alta Alumno o Docente</h3>
            </div>
            <form method="POST" action="/registrar_miembro" autocomplete="off">
              <label>Tipo</label>
              <select name="tipo">
                <option value="Alumno">Alumno</option>
                <option value="Docente">Docente</option>
              </select>
              <label>Código (9 dígitos — clave inicial)</label>
              <input type="text" name="codigo" placeholder="Ej. 220123456" required>
              <label>Nombre completo</label>
              <input type="text" name="nombre" placeholder="Ej. Alex Ramírez" required>
              <label>Carrera (Alumno) o Departamento (Docente)</label>
              <input type="text" name="detalle" placeholder="Ej. Ingeniería en Ciberseguridad" required>
              <button type="submit" class="btn-primary">Registrar persona</button>
            </form>
          </div>

          <div class="siiuu-card">
            <div class="siiuu-card-header">
              <h3>2. Registrar Materia</h3>
            </div>
            <form method="POST" action="/registrar_materia" autocomplete="off">
              <label>Clave de materia</label>
              <input type="text" name="clave" placeholder="Ej. PROG2" required>
              <label>Nombre de la materia</label>
              <input type="text" name="nombre" placeholder="Ej. Programación II" required>
              <label>Cupo máximo</label>
              <input type="number" name="cupo" value="30" min="1" required>
              <button type="submit" class="btn-primary">Registrar materia</button>
            </form>
          </div>

          <div class="siiuu-card">
            <div class="siiuu-card-header">
              <h3>3. Asignar Materia y Horario</h3>
            </div>
            <form method="POST" action="/asignar" autocomplete="off">
              <label>Alumno o Docente</label>
              <select name="codigo" required>
                <option value="">-- Selecciona --</option>
                {% for m in miembros %}
                  <option value="{{ m.codigo }}">{{ m.describir() }}</option>
                {% endfor %}
              </select>
              <label>Materia</label>
              <select name="clave" required>
                <option value="">-- Selecciona --</option>
                {% for mat in materias %}
                  <option value="{{ mat.clave }}">
                    {{ mat.clave }} - {{ mat.nombre }} ({{ mat.inscritos|length }}/{{ mat.cupo_maximo }})
                  </option>
                {% endfor %}
              </select>
              <label>Horario (Bloques de 2h: 07:00 a 21:00)</label>
              <select name="bloque" required>
                {% for b in bloques %}
                  <option value="{{ b }}">{{ b }}</option>
                {% endfor %}
              </select>
              <label>Días de clase</label>
              <div class="days-box">
                {% for d in dias_semana %}
                  <label class="day-chip">
                    <input type="checkbox" name="dias" value="{{ d }}"> {{ d }}
                  </label>
                {% endfor %}
              </div>
              <button type="submit" class="btn-primary">Asignar materia y horario</button>
            </form>
          </div>
        </div>
      {% endif %}

      {% if tab == 'usuarios' %}
        {% if usuario_sel %}
        <div class="siiuu-card highlight">
          <div class="siiuu-card-header">
            <div>
              <span class="pill">{{ 'Alumno' if es_alumno_sel else 'Docente' }}</span>
              <strong style="margin-left:8px; font-size:16px; color:#0f294a;">
                Expediente de {{ usuario_sel.nombre }} ({{ usuario_sel.codigo }})
              </strong>
            </div>
            <div style="display:flex; gap:8px;">
              <form method="POST" action="/admin_eliminar_usuario" style="margin:0;" onsubmit="return confirm('¿Eliminar permanentemente a {{ usuario_sel.nombre }}?');">
                <input type="hidden" name="codigo" value="{{ usuario_sel.codigo }}">
                <button type="submit" class="btn-danger">Eliminar usuario</button>
              </form>
              <a href="/?tab=usuarios" class="btn-outline">Cerrar expediente</a>
            </div>
          </div>

          <div class="grid-2">
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px;">
              <h4 style="margin:0 0 10px; color:#0f294a;">Editar Datos Generales</h4>
              <form method="POST" action="/admin_editar_usuario" style="margin:0;" autocomplete="off">
                <input type="hidden" name="codigo" value="{{ usuario_sel.codigo }}">
                <label>Nombre completo</label>
                <input type="text" name="nombre" value="{{ usuario_sel.nombre }}" required>
                <label>{{ 'Carrera' if es_alumno_sel else 'Departamento' }}</label>
                <input type="text" name="detalle" value="{{ usuario_sel.carrera if es_alumno_sel else usuario_sel.departamento }}" required>
                <button type="submit" class="btn-primary">Guardar cambios de perfil</button>
              </form>
            </div>

            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px;">
              <h4 style="margin:0 0 10px; color:#0f294a;">Recuperación de Contraseña</h4>
              <p style="margin:0 0 10px; font-size:12.5px; color:#475569;">
                Contraseña almacenada: <code><b>{{ usuario_sel.obtener_password_almacenada() }}</b></code>
              </p>
              <form method="POST" action="/admin_reset_password" style="margin-bottom:12px;">
                <input type="hidden" name="codigo" value="{{ usuario_sel.codigo }}">
                <input type="hidden" name="modo" value="inicial">
                <button type="submit" class="btn-outline" style="width:100%;">
                  Restablecer a código inicial ({{ usuario_sel.codigo }}) y pedir cambio
                </button>
              </form>
              <form method="POST" action="/admin_reset_password" style="margin:0;" autocomplete="off">
                <input type="hidden" name="codigo" value="{{ usuario_sel.codigo }}">
                <input type="hidden" name="modo" value="manual">
                <label>O asignar nueva contraseña directa (mín. 6 caracteres)</label>
                <div style="display:flex; gap:8px;">
                  <input type="text" name="nueva_password" placeholder="Nueva contraseña" style="margin:0;" required>
                  <button type="submit" class="btn-sm" style="white-space:nowrap;">Asignar</button>
                </div>
              </form>
            </div>
          </div>

          <h4 style="margin:12px 0 10px; color:#0f294a;">Materias Inscritas y Horarios ({{ cursos_sel|length }})</h4>
          <table>
            <thead>
              <tr>
                <th>Clave</th>
                <th>Materia</th>
                <th>Horario Actual</th>
                <th>Cambiar Horario</th>
                <th>Baja</th>
              </tr>
            </thead>
            <tbody>
              {% for c in cursos_sel %}
              <tr>
                <td><b>{{ c.materia.clave }}</b></td>
                <td>{{ c.materia.nombre }}</td>
                <td><span class="pill">{{ c.horario_texto }}</span></td>
                <td>
                  <form method="POST" action="/admin_cambiar_horario" style="margin:0; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
                    <input type="hidden" name="codigo" value="{{ usuario_sel.codigo }}">
                    <input type="hidden" name="clave" value="{{ c.materia.clave }}">
                    <select name="bloque" style="width:135px; margin:0; padding:6px 8px; font-size:12px;">
                      {% for b in bloques %}
                        <option value="{{ b }}" {{ 'selected' if c.horario_obj and c.horario_obj.bloque == b else '' }}>{{ b }}</option>
                      {% endfor %}
                    </select>
                    <div style="display:flex; flex-wrap:wrap; gap:4px;">
                      {% for d in dias_semana %}
                        <label class="day-chip" style="padding:3px 6px; font-size:11px; margin:0;">
                          <input type="checkbox" name="dias" value="{{ d }}" {{ 'checked' if c.horario_obj and d in c.horario_obj.dias else '' }}>
                          {{ d[:3] }}
                        </label>
                      {% endfor %}
                    </div>
                    <button type="submit" class="btn-sm">Cambiar</button>
                  </form>
                </td>
                <td>
                  <form method="POST" action="/admin_baja_materia" style="margin:0;" onsubmit="return confirm('¿Dar de baja {{ c.materia.clave }} a {{ usuario_sel.nombre }}?');">
                    <input type="hidden" name="codigo" value="{{ usuario_sel.codigo }}">
                    <input type="hidden" name="clave" value="{{ c.materia.clave }}">
                    <button type="submit" class="btn-danger">Dar de baja</button>
                  </form>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="5" style="color:#64748b;">Este usuario no tiene materias inscritas actualmente.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% endif %}

        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Personas Registradas ({{ miembros|length }})</h3>
            {% if tiene_bd_previa %}
              <form method="POST" action="/importar_bd" style="margin:0;">
                <button type="submit" class="btn-outline">Importar desde estudiantes_ibm.db</button>
              </form>
            {% endif %}
          </div>
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Descripción</th>
                <th>Contraseña almacenada</th>
                <th>Estado de acceso</th>
                <th>Gestión</th>
              </tr>
            </thead>
            <tbody>
              {% for m in miembros %}
              <tr>
                <td><a href="/?tab=usuarios&ver_usuario={{ m.codigo }}" class="user-link">{{ m.codigo }}</a></td>
                <td><a href="/?tab=usuarios&ver_usuario={{ m.codigo }}" class="user-link">{{ m.describir() }}</a></td>
                <td><code>{{ m.obtener_password_almacenada() }}</code></td>
                <td>
                  <span class="pill {{ 'pend' if m.debe_cambiar_password else 'aprob' }}">
                    {{ 'Pendiente 1er acceso' if m.debe_cambiar_password else 'Contraseña actualizada' }}
                  </span>
                </td>
                <td>
                  <a href="/?tab=usuarios&ver_usuario={{ m.codigo }}" class="btn-sm">Abrir expediente</a>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="5" style="color:#64748b;">No hay alumnos ni docentes registrados todavía.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab == 'materias' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Catálogo de Materias, Cupos y Horarios ({{ materias|length }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Clave</th>
                <th>Materia</th>
                <th>Cupo</th>
                <th>Inscritos y Horarios</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {% for mat in materias %}
              <tr>
                <td><b>{{ mat.clave }}</b></td>
                <td>{{ mat.nombre }}</td>
                <td>
                  <span class="pill {{ 'reprob' if mat.cupo_disponible == 0 else '' }}">
                    {{ mat.inscritos|length }} / {{ mat.cupo_maximo }}
                  </span>
                </td>
                <td>
                  {% if mat.inscritos %}
                    {% for cod in mat.inscritos %}
                      <div style="font-size:12px; margin-bottom:2px;">
                        <b>{{ cod }}</b> &rarr; {{ mat.formatear_horario(cod) }}
                      </div>
                    {% endfor %}
                  {% else %}
                    <span style="color:#64748b;">Sin inscritos</span>
                  {% endif %}
                </td>
                <td>
                  <form method="POST" action="/admin_eliminar_materia" style="margin:0;" onsubmit="return confirm('¿Eliminar la materia {{ mat.clave }}?');">
                    <input type="hidden" name="clave" value="{{ mat.clave }}">
                    <button type="submit" class="btn-danger">Eliminar</button>
                  </form>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="5" style="color:#64748b;">No hay materias registradas todavía.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab == 'bitacora' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Bitácora de Eventos del Sistema</h3>
            <form method="POST" action="/vaciar_bd" style="margin:0;" onsubmit="return confirm('¿Seguro que deseas eliminar toda la base de datos y dejarla vacía?');">
              <button type="submit" class="btn-danger">Vaciar Base de Datos</button>
            </form>
          </div>
          <div class="log-box">
            {% for ev in historial|reverse %}
              <div class="log-item">{{ ev }}</div>
            {% else %}
              <div style="color:#64748b;">Sin eventos registrados en esta sesión.</div>
            {% endfor %}
          </div>
        </div>
      {% endif %}
    </main>
  </div>
__FOOTER__
</body>
</html>""".replace("__STYLE__", SHARED_SIIUU_STYLE).replace("__FOOTER__", FOOTER_HTML)

DOCENTE_PANEL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIIUU Docentes — UDG | CUGDL</title>
__STYLE__
</head>
<body>
  <header class="siiuu-navbar">
    <div class="siiuu-nav-left">
      <a href="/?tab=materias" class="siiuu-brand">
        SIIUU <span class="siiuu-tag">Docentes</span>
      </a>
      <div class="siiuu-sub">Depto. {{ docente.departamento }}</div>
    </div>
    <div class="siiuu-nav-right">
      <span>{{ docente.nombre }} ({{ docente.codigo }})</span>
      <div class="siiuu-avatar">D</div>
      <a href="/logout" class="siiuu-logout">Cerrar sesión</a>
    </div>
  </header>

  <div class="siiuu-body">
    <aside class="siiuu-sidebar">
      <a href="/?tab=materias" class="siiuu-side-item {{ 'active' if tab == 'materias' else '' }}">
        <span>&#128218;</span> Mis Materias y Calificaciones
      </a>
      <a href="/?tab=horario" class="siiuu-side-item {{ 'active' if tab == 'horario' else '' }}">
        <span>&#128197;</span> Mi Horario Docente
      </a>
      <a href="/?tab=resumen" class="siiuu-side-item {{ 'active' if tab == 'resumen' else '' }}">
        <span>&#128202;</span> Resumen de Grupos
      </a>
      <a href="/?tab=datos" class="siiuu-side-item {{ 'active' if tab == 'datos' else '' }}">
        <span>&#128100;</span> Datos Académicos
      </a>
    </aside>

    <main class="siiuu-main">
      {% if msg %}
        <div class="siiuu-alert {{ 'err' if err else 'ok' }}">{{ msg }}</div>
      {% endif %}

      <div class="kpi-row">
        <div class="kpi-card">
          <small>Materias Asignadas</small>
          <strong>{{ grupos|length }}</strong>
        </div>
        <div class="kpi-card">
          <small>Total de Alumnos en Grupo</small>
          <strong>{{ total_alumnos }}</strong>
        </div>
        <div class="kpi-card">
          <small>Calificaciones Capturadas</small>
          <strong>{{ total_calificados }} / {{ total_alumnos }}</strong>
        </div>
      </div>

      {% if tab == 'horario' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Mi Horario Semanal de Clases (07:00 am — 09:00 pm)</h3>
            <span class="pill">Ciclo 2026-B</span>
          </div>
          <table class="sched-table">
            <thead>
              <tr>
                <th style="width:120px;">Horario</th>
                {% for d in dias_semana %}
                  <th>{{ d }}</th>
                {% endfor %}
              </tr>
            </thead>
            <tbody>
              {% for b in bloques %}
              <tr>
                <td><b>{{ b }}</b></td>
                {% for d in dias_semana %}
                  {% set celda = tabla_horario[b][d] %}
                  <td>
                    {% if celda %}
                      <div class="sched-slot">
                        <b>{{ celda.clave }}</b><br>
                        {{ celda.nombre }}
                      </div>
                    {% else %}
                      <span style="color:#cbd5e1;">—</span>
                    {% endif %}
                  </td>
                {% endfor %}
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab in ['materias', 'horario'] %}
        {% for g in grupos %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <div>
              <h3>[{{ g.materia.clave }}] {{ g.materia.nombre }}</h3>
              <span style="font-size:12.5px; color:#64748b;">
                Horario asignado: <b>{{ g.horario_docente }}</b> &bull; Alumnos inscritos: {{ g.alumnos|length }}
              </span>
            </div>
            <span class="pill">{{ g.horario_docente }}</span>
          </div>

          {% if tab == 'materias' %}
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre del Alumno</th>
                <th>Carrera</th>
                <th>Horario Alumno</th>
                <th>Estatus</th>
                <th>Calificación (0 - 100)</th>
              </tr>
            </thead>
            <tbody>
              {% for item in g.alumnos %}
              <tr>
                <td><b>{{ item.alumno.codigo }}</b></td>
                <td>{{ item.alumno.nombre }}</td>
                <td>{{ item.alumno.carrera }}</td>
                <td><span style="font-size:12px; color:#475569;">{{ item.horario_alumno }}</span></td>
                <td>
                  {% if item.nota is none %}
                    <span class="pill pend">Sin calificar</span>
                  {% elif item.nota >= 60 %}
                    <span class="pill aprob">Aprobado ({{ item.nota }})</span>
                  {% else %}
                    <span class="pill reprob">Reprobado ({{ item.nota }})</span>
                  {% endif %}
                </td>
                <td>
                  <form method="POST" action="/calificar_docente" class="grade-form" autocomplete="off">
                    <input type="hidden" name="clave_materia" value="{{ g.materia.clave }}">
                    <input type="hidden" name="codigo_alumno" value="{{ item.alumno.codigo }}">
                    <input
                      type="number"
                      name="calificacion"
                      class="grade-input"
                      step="0.1"
                      min="0"
                      max="100"
                      placeholder="0 - 100"
                      value="{{ item.nota if item.nota is not none else '' }}"
                      required
                    >
                    <button type="submit" class="btn-sm">Guardar</button>
                  </form>
                </td>
              </tr>
              {% else %}
              <tr>
                <td colspan="6" style="color:#64748b;">
                  Aún no hay alumnos inscritos en esta materia.
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% endif %}
        </div>
        {% else %}
        <div class="siiuu-card">
          <h3 style="margin:0 0 8px; color:#0f294a;">Sin materias asignadas</h3>
          <p style="margin:0; font-size:13.5px; color:#64748b;">
            El administrador aún no te ha asignado materias para impartir en este ciclo escolar.
          </p>
        </div>
        {% endfor %}
      {% endif %}

      {% if tab == 'resumen' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Resumen General de Mis Materias</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Clave</th>
                <th>Materia</th>
                <th>Horario</th>
                <th>Alumnos Inscritos</th>
                <th>Calificados</th>
                <th>Promedio del Grupo</th>
              </tr>
            </thead>
            <tbody>
              {% for g in grupos %}
              <tr>
                <td><b>{{ g.materia.clave }}</b></td>
                <td>{{ g.materia.nombre }}</td>
                <td>{{ g.horario_docente }}</td>
                <td>{{ g.alumnos|length }}</td>
                <td>{{ g.calificados }} / {{ g.alumnos|length }}</td>
                <td>
                  {% if g.promedio is not none %}
                    <span class="pill {{ 'aprob' if g.promedio >= 60 else 'reprob' }}">{{ g.promedio }}</span>
                  {% else %}
                    <span style="color:#94a3b8;">--</span>
                  {% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="color:#64748b;">No tienes materias asignadas todavía.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab == 'datos' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Datos Generales del Docente</h3>
          </div>
          <div class="info-grid">
            <div class="info-box"><small>Código de Académico</small><strong>{{ docente.codigo }}</strong></div>
            <div class="info-box"><small>Nombre Completo</small><strong>{{ docente.nombre }}</strong></div>
            <div class="info-box"><small>Departamento</small><strong>{{ docente.departamento }}</strong></div>
            <div class="info-box"><small>Correo Institucional</small><strong>{{ correo_docente }}</strong></div>
          </div>
        </div>
      {% endif %}
    </main>
  </div>
__FOOTER__
</body>
</html>""".replace("__STYLE__", SHARED_SIIUU_STYLE).replace("__FOOTER__", FOOTER_HTML)

ALUMNO_PANEL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIIUU Alumnos — UDG | CUGDL</title>
__STYLE__
</head>
<body>
  <header class="siiuu-navbar">
    <div class="siiuu-nav-left">
      <a href="/?tab=inicio" class="siiuu-brand">
        SIIUU <span class="siiuu-tag">Alumnos</span>
      </a>
      <div class="siiuu-sub">{{ alumno.carrera }}</div>
    </div>
    <div class="siiuu-nav-right">
      <span>{{ alumno.nombre }} ({{ alumno.codigo }})</span>
      <div class="siiuu-avatar">A</div>
      <a href="/logout" class="siiuu-logout">Cerrar sesión</a>
    </div>
  </header>

  <div class="siiuu-body">
    <aside class="siiuu-sidebar">
      <a href="/?tab=inicio" class="siiuu-side-item {{ 'active' if tab == 'inicio' else '' }}">
        <span>&#127968;</span> Inicio y Resumen
      </a>
      <a href="/?tab=horario" class="siiuu-side-item {{ 'active' if tab == 'horario' else '' }}">
        <span>&#128197;</span> Mi Horario
      </a>
      <a href="/?tab=kardex" class="siiuu-side-item {{ 'active' if tab == 'kardex' else '' }}">
        <span>&#127891;</span> Kárdex y Calificaciones
      </a>
      <a href="/?tab=registrar" class="siiuu-side-item {{ 'active' if tab == 'registrar' else '' }}">
        <span>&#10133;</span> Registrar Cursos
      </a>
      <a href="/?tab=oferta" class="siiuu-side-item {{ 'active' if tab == 'oferta' else '' }}">
        <span>&#128218;</span> Oferta Académica
      </a>
      <a href="/?tab=datos" class="siiuu-side-item {{ 'active' if tab == 'datos' else '' }}">
        <span>&#128100;</span> Datos Generales
      </a>
    </aside>

    <main class="siiuu-main">
      {% if msg %}
        <div class="siiuu-alert {{ 'err' if err else 'ok' }}">{{ msg }}</div>
      {% endif %}

      <div class="kpi-row">
        <div class="kpi-card">
          <small>Materias Inscritas</small>
          <strong>{{ mis_cursos|length }}</strong>
        </div>
        <div class="kpi-card">
          <small>Materias Evaluadas</small>
          <strong>{{ total_evaluadas }} / {{ mis_cursos|length }}</strong>
        </div>
        <div class="kpi-card">
          <small>Promedio General</small>
          <strong>{{ promedio_general if promedio_general is not none else '--' }}</strong>
        </div>
      </div>

      {% if tab in ['inicio', 'horario'] %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Mi Horario Semanal de Clases (07:00 am — 09:00 pm)</h3>
            <span class="pill">Ciclo 2026-B</span>
          </div>
          <table class="sched-table">
            <thead>
              <tr>
                <th style="width:120px;">Horario</th>
                {% for d in dias_semana %}
                  <th>{{ d }}</th>
                {% endfor %}
              </tr>
            </thead>
            <tbody>
              {% for b in bloques %}
              <tr>
                <td><b>{{ b }}</b></td>
                {% for d in dias_semana %}
                  {% set celda = tabla_horario[b][d] %}
                  <td>
                    {% if celda %}
                      <div class="sched-slot">
                        <b>{{ celda.clave }}</b><br>
                        {{ celda.nombre }}<br>
                        <span style="font-size:10.5px; color:#0f294a;">{{ celda.docente }}</span>
                      </div>
                    {% else %}
                      <span style="color:#cbd5e1;">—</span>
                    {% endif %}
                  </td>
                {% endfor %}
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab in ['inicio', 'horario', 'kardex'] %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>{{ 'Kárdex y Calificaciones Oficiales' if tab == 'kardex' else 'Detalle de Materias Inscritas' }} ({{ mis_cursos|length }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Clave</th>
                <th>Materia</th>
                <th>Docente</th>
                <th>Horario Asignado</th>
                <th>Calificación</th>
                <th>Estatus</th>
              </tr>
            </thead>
            <tbody>
              {% for c in mis_cursos %}
              <tr>
                <td><b>{{ c.materia.clave }}</b></td>
                <td>{{ c.materia.nombre }}</td>
                <td>{{ c.docente_nombre }}</td>
                <td><span class="pill">{{ c.horario_texto }}</span></td>
                <td>
                  {% if c.nota is not none %}
                    <strong>{{ c.nota }}</strong>
                  {% else %}
                    <span style="color:#94a3b8;">Pendiente</span>
                  {% endif %}
                </td>
                <td>
                  {% if c.nota is none %}
                    <span class="pill pend">Cursando</span>
                  {% elif c.nota >= 60 %}
                    <span class="pill aprob">Aprobada</span>
                  {% else %}
                    <span class="pill reprob">Reprobada</span>
                  {% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="color:#64748b;">Aún no tienes materias registradas en este ciclo.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab == 'registrar' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Registro a Cursos — Ciclo 2026-B</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Clave</th>
                <th>Materia</th>
                <th>Cupo disponible</th>
                <th>Seleccionar Horario y Registrar</th>
              </tr>
            </thead>
            <tbody>
              {% for mat in todas_materias %}
              {% set ref = mat.horario_referencia() %}
              <tr>
                <td><b>{{ mat.clave }}</b></td>
                <td>{{ mat.nombre }}</td>
                <td>
                  <span class="pill {{ 'reprob' if mat.cupo_disponible == 0 else '' }}">
                    {{ mat.cupo_disponible }} lugares ({{ mat.inscritos|length }}/{{ mat.cupo_maximo }})
                  </span>
                </td>
                <td>
                  {% if alumno.codigo in mat.inscritos %}
                    <span class="pill aprob">Ya inscrito ({{ mat.formatear_horario(alumno.codigo) }})</span>
                  {% elif mat.cupo_disponible == 0 %}
                    <span class="pill reprob">Cupo lleno</span>
                  {% else %}
                    <form method="POST" action="/inscribir_alumno" style="margin:0; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
                      <input type="hidden" name="clave" value="{{ mat.clave }}">
                      <select name="bloque" style="width:135px; margin:0; padding:6px 8px; font-size:12px;">
                        {% for b in bloques %}
                          <option value="{{ b }}" {{ 'selected' if ref and ref.bloque == b else '' }}>{{ b }}</option>
                        {% endfor %}
                      </select>
                      <div style="display:flex; flex-wrap:wrap; gap:4px;">
                        {% for d in dias_semana %}
                          <label class="day-chip" style="padding:3px 6px; font-size:11px; margin:0;">
                            <input type="checkbox" name="dias" value="{{ d }}" {{ 'checked' if ref and d in ref.dias else '' }}> {{ d[:3] }}
                          </label>
                        {% endfor %}
                      </div>
                      <button type="submit" class="btn-sm">Registrar</button>
                    </form>
                  {% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="4" style="color:#64748b;">El administrador aún no ha dado de alta materias.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab == 'oferta' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Oferta Académica Disponible ({{ todas_materias|length }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Clave</th>
                <th>Asignatura</th>
                <th>Cupo máximo</th>
                <th>Lugares disponibles</th>
              </tr>
            </thead>
            <tbody>
              {% for mat in todas_materias %}
              <tr>
                <td><b>{{ mat.clave }}</b></td>
                <td>{{ mat.nombre }}</td>
                <td>{{ mat.cupo_maximo }}</td>
                <td>
                  <span class="pill {{ 'reprob' if mat.cupo_disponible == 0 else 'aprob' }}">
                    {{ mat.cupo_disponible }} disponibles
                  </span>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="4" style="color:#64748b;">No hay oferta académica registrada.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}

      {% if tab == 'datos' %}
        <div class="siiuu-card">
          <div class="siiuu-card-header">
            <h3>Datos Generales del Alumno</h3>
          </div>
          <div class="info-grid">
            <div class="info-box"><small>Código Universitario</small><strong>{{ alumno.codigo }}</strong></div>
            <div class="info-box"><small>Nombre Completo</small><strong>{{ alumno.nombre }}</strong></div>
            <div class="info-box"><small>Carrera</small><strong>{{ alumno.carrera }}</strong></div>
            <div class="info-box"><small>Correo Institucional</small><strong>{{ correo_institucional }}</strong></div>
          </div>
        </div>
      {% endif %}
    </main>
  </div>
__FOOTER__
</body>
</html>""".replace("__STYLE__", SHARED_SIIUU_STYLE).replace("__FOOTER__", FOOTER_HTML)


@app.route("/logo/udg")
def logo_udg():
    """Sirve el logotipo institucional de la Universidad de Guadalajara."""
    return send_from_directory(".", "UDGLOGO.webp")


@app.route("/logo/cugdl")
def logo_cugdl():
    """Sirve el logotipo del Centro Universitario de Guadalajara."""
    return send_from_directory(".", "CUGDLLOGO.webp")


@app.route("/", methods=["GET"])
def index():
    """Renderiza el inicio de sesión o el panel correspondiente al rol autenticado."""
    rol = session.get("rol")

    if not rol:
        return render_template_string(
            LOGIN_HTML,
            msg=request.args.get("msg", ""),
            err=request.args.get("err") == "1",
        )

    sistema = cargar_sistema()

    if rol == "admin":
        miembros = sistema.obtener_miembros()
        total_alumnos = sum(1 for m in miembros if isinstance(m, Alumno))
        total_docentes = sum(1 for m in miembros if isinstance(m, Docente))

        ver_codigo = request.args.get("ver_usuario", "").strip()
        usuario_sel = sistema.buscar_miembro(ver_codigo) if ver_codigo else None
        cursos_sel = []
        if usuario_sel:
            for mat in sistema.obtener_materias():
                if usuario_sel.codigo in mat.inscritos:
                    cursos_sel.append(
                        {
                            "materia": mat,
                            "horario_texto": mat.formatear_horario(usuario_sel.codigo),
                            "horario_obj": mat.obtener_horario(usuario_sel.codigo),
                        }
                    )

        tab = request.args.get("tab", "usuarios" if usuario_sel else "altas")
        if tab not in {"altas", "usuarios", "materias", "bitacora"}:
            tab = "altas"

        return render_template_string(
            ADMIN_PANEL_HTML,
            miembros=miembros,
            materias=sistema.obtener_materias(),
            total_alumnos=total_alumnos,
            total_docentes=total_docentes,
            historial=sistema.historial,
            tiene_bd_previa=os.path.exists("estudiantes_ibm.db"),
            usuario_sel=usuario_sel,
            es_alumno_sel=isinstance(usuario_sel, Alumno),
            cursos_sel=cursos_sel,
            bloques=BLOQUES_HORARIO,
            dias_semana=DIAS_SEMANA,
            tab=tab,
            msg=request.args.get("msg", ""),
            err=request.args.get("err") == "1",
        )

    codigo_activo = session.get("usuario_codigo")
    usuario = sistema.buscar_miembro(codigo_activo)
    if not usuario:
        session.clear()
        return redirect(url_for("index"))

    if usuario.debe_cambiar_password:
        return redirect(url_for("vista_cambiar_password"))

    todas_materias = sistema.obtener_materias()
    tabla_horario = sistema.construir_tabla_horario(usuario.codigo)

    if isinstance(usuario, Docente):
        grupos = []
        total_alumnos = 0
        total_calificados = 0

        for mat in todas_materias:
            if usuario.codigo in mat.inscritos:
                alumnos_grupo = []
                notas_grupo = []
                for cod in mat.inscritos:
                    miembro = sistema.buscar_miembro(cod)
                    if isinstance(miembro, Alumno):
                        nota = mat.obtener_calificacion(cod)
                        alumnos_grupo.append(
                            {
                                "alumno": miembro,
                                "nota": nota,
                                "horario_alumno": mat.formatear_horario(cod),
                            }
                        )
                        if nota is not None:
                            notas_grupo.append(nota)

                total_alumnos += len(alumnos_grupo)
                total_calificados += len(notas_grupo)
                promedio = (
                    round(sum(notas_grupo) / len(notas_grupo), 2)
                    if notas_grupo
                    else None
                )
                grupos.append(
                    {
                        "materia": mat,
                        "horario_docente": mat.formatear_horario(usuario.codigo),
                        "alumnos": alumnos_grupo,
                        "calificados": len(notas_grupo),
                        "promedio": promedio,
                    }
                )

        tab = request.args.get("tab", "materias")
        if tab not in {"materias", "horario", "resumen", "datos"}:
            tab = "materias"

        primer_nombre = usuario.nombre.split()[0].lower()
        correo_docente = f"{primer_nombre}.{usuario.codigo[-4:]}@academicos.udg.mx"

        return render_template_string(
            DOCENTE_PANEL_HTML,
            docente=usuario,
            grupos=grupos,
            tabla_horario=tabla_horario,
            bloques=BLOQUES_HORARIO,
            dias_semana=DIAS_SEMANA,
            total_alumnos=total_alumnos,
            total_calificados=total_calificados,
            correo_docente=correo_docente,
            tab=tab,
            msg=request.args.get("msg", ""),
            err=request.args.get("err") == "1",
        )

    mis_cursos = []
    notas_alumno = []
    for mat in todas_materias:
        if usuario.codigo in mat.inscritos:
            docente_nombre = "Por asignar"
            for cod in mat.inscritos:
                m = sistema.buscar_miembro(cod)
                if isinstance(m, Docente):
                    docente_nombre = m.nombre
                    break
            nota = mat.obtener_calificacion(usuario.codigo)
            if nota is not None:
                notas_alumno.append(nota)
            mis_cursos.append(
                {
                    "materia": mat,
                    "docente_nombre": docente_nombre,
                    "horario_texto": mat.formatear_horario(usuario.codigo),
                    "nota": nota,
                }
            )

    promedio_general = (
        round(sum(notas_alumno) / len(notas_alumno), 2) if notas_alumno else None
    )

    primer_nombre = usuario.nombre.split()[0].lower()
    correo_institucional = f"{primer_nombre}.{usuario.codigo[-4:]}@alumnos.udg.mx"

    tab = request.args.get("tab", "inicio")
    if tab not in {"inicio", "datos", "horario", "kardex", "registrar", "oferta"}:
        tab = "inicio"

    return render_template_string(
        ALUMNO_PANEL_HTML,
        alumno=usuario,
        mis_cursos=mis_cursos,
        todas_materias=todas_materias,
        tabla_horario=tabla_horario,
        bloques=BLOQUES_HORARIO,
        dias_semana=DIAS_SEMANA,
        total_evaluadas=len(notas_alumno),
        promedio_general=promedio_general,
        correo_institucional=correo_institucional,
        tab=tab,
        msg=request.args.get("msg", ""),
        err=request.args.get("err") == "1",
    )


@app.route("/login", methods=["POST"])
def login():
    """Procesa la autenticación de administrador, docente o alumno."""
    usuario_input = request.form.get("usuario_siiuu", "").strip()
    password_input = request.form.get("clave_siiuu", "")

    if usuario_input == ADMIN_USER and password_input == ADMIN_PASS:
        session.clear()
        session["rol"] = "admin"
        return redirect(url_for("index"))

    sistema = cargar_sistema()
    try:
        usuario = sistema.autenticar(usuario_input, password_input)
        sistema.guardar(RUTA_BD)
        session.clear()
        session["rol"] = "miembro"
        session["usuario_codigo"] = usuario.codigo
        if usuario.debe_cambiar_password:
            return redirect(url_for("vista_cambiar_password"))
        return redirect(url_for("index"))
    except ValueError:
        return redirect(
            url_for("index", msg="Usuario o contraseña incorrectos.", err="1")
        )


@app.route("/cambiar_password", methods=["GET", "POST"])
def vista_cambiar_password():
    """Gestiona el cambio obligatorio de contraseña en el primer acceso."""
    if session.get("rol") != "miembro":
        return redirect(url_for("index"))

    sistema = cargar_sistema()
    usuario = sistema.buscar_miembro(session.get("usuario_codigo"))
    if not usuario:
        session.clear()
        return redirect(url_for("index"))

    if not usuario.debe_cambiar_password:
        return redirect(url_for("index"))

    if request.method == "POST":
        nueva = request.form.get("nueva_password", "")
        confirmacion = request.form.get("confirmacion", "")
        try:
            sistema.actualizar_password(usuario.codigo, nueva, confirmacion)
            sistema.guardar(RUTA_BD)
            return redirect(
                url_for("index", msg="Contraseña actualizada correctamente.")
            )
        except ValueError as e:
            return render_template_string(
                CAMBIAR_PASS_HTML, usuario=usuario, msg=str(e)
            )

    return render_template_string(CAMBIAR_PASS_HTML, usuario=usuario, msg="")


@app.route("/calificar_docente", methods=["POST"])
def calificar_docente():
    """Guarda la calificación asignada por un docente a un alumno de su grupo."""
    if session.get("rol") != "miembro":
        return redirect(url_for("index"))

    sistema = cargar_sistema()
    docente = sistema.buscar_miembro(session.get("usuario_codigo"))
    if not isinstance(docente, Docente):
        return redirect(url_for("index"))

    clave_materia = request.form.get("clave_materia", "").strip().upper()
    codigo_alumno = request.form.get("codigo_alumno", "").strip()
    calif_raw = request.form.get("calificacion", "").strip()

    try:
        materia = sistema.buscar_materia(clave_materia)
        if not materia or docente.codigo not in materia.inscritos:
            raise ValueError("No tienes permiso para calificar esta materia.")

        nota = float(calif_raw)
        sistema.calificar(codigo_alumno, clave_materia, nota)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for(
                "index",
                tab="materias",
                msg=f"Calificación {nota} guardada para el alumno {codigo_alumno} en {clave_materia}.",
            )
        )
    except ValueError as e:
        return redirect(url_for("index", tab="materias", msg=str(e), err="1"))


@app.route("/inscribir_alumno", methods=["POST"])
def inscribir_alumno():
    """Inscribe al alumno autenticado en una materia y horario desde su portal."""
    if session.get("rol") != "miembro":
        return redirect(url_for("index"))
    codigo = session.get("usuario_codigo", "")
    clave = request.form.get("clave", "")
    bloque = request.form.get("bloque", "")
    dias = request.form.getlist("dias")
    sistema = cargar_sistema()
    try:
        sistema.asignar(codigo, clave, dias, bloque)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for(
                "index",
                tab="registrar",
                msg=f"Curso {clave} registrado correctamente en tu horario.",
            )
        )
    except ValueError as e:
        return redirect(url_for("index", tab="registrar", msg=str(e), err="1"))


@app.route("/logout", methods=["GET"])
def logout():
    """Cierra la sesión activa y redirige al inicio de sesión."""
    session.clear()
    return redirect(url_for("index", msg="Sesión cerrada."))


@app.route("/vaciar_bd", methods=["POST"])
def vaciar_bd():
    """Elimina el archivo de base de datos SQLite desde el panel de administrador."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    if os.path.exists(RUTA_BD):
        os.remove(RUTA_BD)
    return redirect(
        url_for("index", tab="bitacora", msg="Base de datos eliminada y reiniciada desde cero.")
    )


@app.route("/registrar_miembro", methods=["POST"])
def registrar_miembro():
    """Da de alta un nuevo alumno o docente desde el panel de administrador."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    tipo = request.form.get("tipo", "Alumno")
    codigo = request.form.get("codigo", "")
    nombre = request.form.get("nombre", "")
    detalle = request.form.get("detalle", "")
    try:
        persona = (
            Alumno(codigo, nombre, detalle)
            if tipo == "Alumno"
            else Docente(codigo, nombre, detalle)
        )
        sistema.registrar(persona)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for("index", tab="altas", msg=f"Alta exitosa: {persona.describir()}")
        )
    except ValueError as e:
        return redirect(url_for("index", tab="altas", msg=str(e), err="1"))


@app.route("/registrar_materia", methods=["POST"])
def registrar_materia():
    """Registra una nueva materia con su cupo máximo desde el panel de administrador."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    clave = request.form.get("clave", "")
    nombre = request.form.get("nombre", "")
    cupo_raw = request.form.get("cupo", "0")
    try:
        cupo = int(cupo_raw) if cupo_raw.strip() else 0
        materia = Materia(clave, nombre, cupo)
        sistema.registrar(materia)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for("index", tab="altas", msg=f"Materia '{materia.clave}' registrada.")
        )
    except ValueError as e:
        return redirect(url_for("index", tab="altas", msg=str(e), err="1"))


@app.route("/asignar", methods=["POST"])
def asignar():
    """Asigna una materia y un bloque horario a un alumno o docente."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    codigo = request.form.get("codigo", "")
    clave = request.form.get("clave", "")
    bloque = request.form.get("bloque", "")
    dias = request.form.getlist("dias")
    try:
        sistema.asignar(codigo, clave, dias, bloque)
        sistema.guardar(RUTA_BD)
        mat = sistema.buscar_materia(clave)
        horario_txt = mat.formatear_horario(codigo) if mat else ""
        return redirect(
            url_for(
                "index",
                tab="altas",
                msg=f"Código {codigo} asignado a {clave} ({horario_txt}).",
            )
        )
    except ValueError as e:
        return redirect(url_for("index", tab="altas", msg=str(e), err="1"))


@app.route("/admin_editar_usuario", methods=["POST"])
def admin_editar_usuario():
    """Edita el nombre y carrera/departamento de un usuario desde su expediente."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    codigo = request.form.get("codigo", "")
    nombre = request.form.get("nombre", "")
    detalle = request.form.get("detalle", "")
    try:
        sistema.editar_miembro(codigo, nombre, detalle)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for(
                "index",
                tab="usuarios",
                ver_usuario=codigo,
                msg="Datos del usuario actualizados.",
            )
        )
    except ValueError as e:
        return redirect(
            url_for("index", tab="usuarios", ver_usuario=codigo, msg=str(e), err="1")
        )


@app.route("/admin_reset_password", methods=["POST"])
def admin_reset_password():
    """Restablece o cambia la contraseña de un usuario desde administración."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    codigo = request.form.get("codigo", "")
    modo = request.form.get("modo", "inicial")
    nueva = request.form.get("nueva_password", "") if modo == "manual" else None
    try:
        sistema.restablecer_password_admin(codigo, nueva)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for(
                "index",
                tab="usuarios",
                ver_usuario=codigo,
                msg="Contraseña restablecida correctamente.",
            )
        )
    except ValueError as e:
        return redirect(
            url_for("index", tab="usuarios", ver_usuario=codigo, msg=str(e), err="1")
        )


@app.route("/admin_cambiar_horario", methods=["POST"])
def admin_cambiar_horario():
    """Cambia los días y el bloque horario de una materia asignada a un usuario."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    codigo = request.form.get("codigo", "")
    clave = request.form.get("clave", "")
    bloque = request.form.get("bloque", "")
    dias = request.form.getlist("dias")
    try:
        sistema.cambiar_horario(codigo, clave, dias, bloque)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for(
                "index",
                tab="usuarios",
                ver_usuario=codigo,
                msg=f"Horario actualizado en {clave}.",
            )
        )
    except ValueError as e:
        return redirect(
            url_for("index", tab="usuarios", ver_usuario=codigo, msg=str(e), err="1")
        )


@app.route("/admin_baja_materia", methods=["POST"])
def admin_baja_materia():
    """Da de baja una materia asignada a un usuario desde el panel de administrador."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    codigo = request.form.get("codigo", "")
    clave = request.form.get("clave", "")
    try:
        sistema.dar_de_baja_materia(codigo, clave)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for(
                "index",
                tab="usuarios",
                ver_usuario=codigo,
                msg=f"Materia {clave} dada de baja correctamente.",
            )
        )
    except ValueError as e:
        return redirect(
            url_for("index", tab="usuarios", ver_usuario=codigo, msg=str(e), err="1")
        )


@app.route("/admin_eliminar_usuario", methods=["POST"])
def admin_eliminar_usuario():
    """Elimina permanentemente a un alumno o docente del sistema."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    codigo = request.form.get("codigo", "")
    try:
        sistema.eliminar_miembro(codigo)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for("index", tab="usuarios", msg=f"Usuario {codigo} eliminado.")
        )
    except ValueError as e:
        return redirect(url_for("index", tab="usuarios", msg=str(e), err="1"))


@app.route("/admin_eliminar_materia", methods=["POST"])
def admin_eliminar_materia():
    """Elimina una materia del catálogo desde el panel de administrador."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    clave = request.form.get("clave", "")
    try:
        sistema.eliminar_materia(clave)
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for("index", tab="materias", msg=f"Materia {clave} eliminada.")
        )
    except ValueError as e:
        return redirect(url_for("index", tab="materias", msg=str(e), err="1"))


@app.route("/importar_bd", methods=["POST"])
def importar_bd():
    """Importa registros de estudiantes desde estudiantes_ibm.db si existe."""
    if session.get("rol") != "admin":
        return redirect(url_for("index"))
    sistema = cargar_sistema()
    try:
        total = AlmacenSQLite().importar_desde_bd_previa(
            sistema, "estudiantes_ibm.db"
        )
        sistema.guardar(RUTA_BD)
        return redirect(
            url_for("index", tab="usuarios", msg=f"Se importaron {total} alumnos válidos.")
        )
    except ValueError as e:
        return redirect(url_for("index", tab="usuarios", msg=str(e), err="1"))


if __name__ == "__main__":
    app.run(debug=True, port=8080)