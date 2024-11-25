# app/controllers/solicitud_cambio_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import mysql, app
from werkzeug.utils import secure_filename
import os

# Crear el blueprint para el SolicitudCambioController
solicitud_cambio_controller = Blueprint('solicitud_cambio_controller', __name__)

# Ruta para solicitar un cambio
@solicitud_cambio_controller.route('/proyecto/<int:id_proyecto>/solicitar_cambio', methods=['GET', 'POST'])
@login_required
def solicitar_cambio(id_proyecto):
    if request.method == 'POST':
        archivo = request.files['archivo']
        descripcion = request.form['descripcion']

        if archivo and descripcion:
            filename = secure_filename(archivo.filename)
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(archivo_path)

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO Solicitud_Cambio (id_proyecto, id_usuario, archivo, descripcion, estado)
                VALUES (%s, %s, %s, %s, 'Pendiente')
            """, (id_proyecto, current_user.id, archivo_path, descripcion))
            mysql.connection.commit()
            cur.close()

            flash('Solicitud de cambio enviada correctamente', 'success')
            return redirect(url_for('solicitud_cambio_controller.ver_solicitudes_cambio', id_proyecto=id_proyecto))
    
    return render_template('solicitar_cambio.html', id_proyecto=id_proyecto)

# Ruta para revisar las solicitudes de cambio
@solicitud_cambio_controller.route('/proyecto/<int:id_proyecto>/cambios', methods=['GET'])
@login_required
def ver_solicitudes_cambio(id_proyecto):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT sc.id_cambio, sc.descripcion, sc.estado, sc.fecha_solicitud, u.nombre 
        FROM Solicitud_Cambio sc 
        JOIN Usuario u ON sc.id_usuario = u.id_usuario
        WHERE sc.id_proyecto = %s
    """, (id_proyecto,))
    solicitudes = cur.fetchall()
    cur.close()

    return render_template('ver_solicitudes_cambio.html', solicitudes=solicitudes, id_proyecto=id_proyecto)

# Ruta para revisar una solicitud de cambio
@solicitud_cambio_controller.route('/proyecto/<int:id_proyecto>/cambio/<int:id_cambio>/revisar', methods=['POST'])
@login_required
def revisar_cambio(id_proyecto, id_cambio):
    accion = request.form['accion']  # Puede ser 'Aprobar' o 'Rechazar'
    
    # Validar que la acción sea correcta
    if accion not in ['Aprobar', 'Rechazar']:
        flash('Acción inválida', 'danger')
        return redirect(url_for('solicitud_cambio_controller.ver_solicitudes_cambio', id_proyecto=id_proyecto))

    # Mapear la acción a los estados correspondientes
    estado_final = 'Aprobado' if accion == 'Aprobar' else 'Rechazado'
    
    cur = mysql.connection.cursor()

    # Actualizar el estado de la solicitud
    cur.execute("UPDATE Solicitud_Cambio SET estado = %s WHERE id_cambio = %s", (estado_final, id_cambio))
    
    # Registrar la acción en el historial de cambios
    cur.execute("INSERT INTO Historial_Cambios (id_cambio, id_usuario, accion) VALUES (%s, %s, %s)", 
                (id_cambio, current_user.id, estado_final))

    mysql.connection.commit()
    cur.close()

    flash(f'El cambio ha sido {estado_final.lower()} con éxito.', 'success')
    return redirect(url_for('solicitud_cambio_controller.ver_solicitudes_cambio', id_proyecto=id_proyecto))
