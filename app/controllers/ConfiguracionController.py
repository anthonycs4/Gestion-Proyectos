# app/controllers/configuracion_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required
from app import mysql
import os
from werkzeug.utils import secure_filename
import difflib

configuracion_controller = Blueprint('configuracion_controller', __name__)

@configuracion_controller.route('/proyecto/<int:id>/configuracion', methods=['GET'])
@login_required
def ver_configuracion(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id_version, version, tipo, fecha_subida, descripcion, ruta_archivo
        FROM Version_Configuracion
        WHERE id_proyecto = %s
        ORDER BY fecha_subida DESC
    """, (id,))
    versiones = cur.fetchall()
    cur.close()

    return render_template('configuracion/ver_configuracion.html', versiones=versiones, id_proyecto=id)

@configuracion_controller.route('/proyecto/<int:id>/configuracion/subir', methods=['GET', 'POST'])
@login_required
def subir_version(id):
    if request.method == 'POST':
        archivo = request.files['archivo']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        if archivo and descripcion:
            ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(archivo.filename))
            archivo.save(ruta_archivo)

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO Version_Configuracion (version, descripcion, ruta_archivo, tipo, fecha_subida, id_proyecto)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (archivo.filename, descripcion, ruta_archivo, tipo, id))
            mysql.connection.commit()
            cur.close()

            flash('Nueva versión subida con éxito', 'success')
            return redirect(url_for('configuracion_controller.ver_configuracion', id=id))
    return render_template('configuracion/subir_version.html', id_proyecto=id)

def comparar_archivos(ruta_version_1, ruta_version_2):
    with open(ruta_version_1, 'r', encoding='utf-8', errors='ignore') as archivo_1, open(ruta_version_2, 'r', encoding='utf-8', errors='ignore') as archivo_2:
        contenido_1 = archivo_1.readlines()
        contenido_2 = archivo_2.readlines()

    d = difflib.HtmlDiff()
    return d.make_file(contenido_1, contenido_2)

@configuracion_controller.route('/proyecto/<int:id>/configuracion/comparar', methods=['GET'])
@login_required
def comparar_versiones(id):
    id_version_1 = request.args.get('id_version_1')
    id_version_2 = request.args.get('id_version_2')

    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_archivo FROM Version_Configuracion WHERE id_version = %s", (id_version_1,))
    ruta_version_1 = cur.fetchone()[0]

    cur.execute("SELECT ruta_archivo FROM Version_Configuracion WHERE id_version = %s", (id_version_2,))
    ruta_version_2 = cur.fetchone()[0]
    cur.close()

    diferencias = comparar_archivos(ruta_version_1, ruta_version_2)
    return render_template('configuracion/comparar_versiones.html', diferencias=diferencias, id_proyecto=id)

@configuracion_controller.route('/proyecto/version/descargar/<path:ruta>', methods=['GET'])
@login_required
def descargar_version(ruta):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], ruta, as_attachment=True)

@configuracion_controller.route('/proyecto/<int:id_proyecto>/configuracion/restaurar/<int:id_version>', methods=['POST'])
@login_required
def restaurar_version(id_proyecto, id_version):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_archivo FROM Version_Configuracion WHERE id_version = %s", (id_version,))
    ruta_version = cur.fetchone()[0]
    cur.close()

    flash(f'Versión restaurada desde {ruta_version} con éxito', 'success')
    return redirect(url_for('configuracion_controller.ver_configuracion', id=id_proyecto))
