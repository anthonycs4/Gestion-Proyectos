# app/controllers/miembro_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import mysql
from app.models.miembro_proyecto import MiembroProyecto


miembro_bp = Blueprint('miembro', __name__)

@miembro_bp.route('/gestionar_usuarios', methods=['GET'])
def gestionar_usuarios():
    usuarios = MiembroProyecto.obtener_usuarios_con_proyectos()
    return render_template('Mantenimiento/gestionar_usuarios.html', usuarios=usuarios)

@miembro_bp.route('/cambiar_rol/<int:id_usuario>', methods=['GET', 'POST'])
def cambiar_rol(id_usuario):
    if request.method == 'POST':
        nuevo_rol_id = request.form['rol']
        MiembroProyecto.actualizar_rol(id_usuario, nuevo_rol_id)
        flash('Rol actualizado con éxito', 'success')
        return redirect(url_for('miembro.gestionar_usuarios'))
    
    roles = MiembroProyecto.obtener_roles()
    return render_template('Mantenimiento/cambiar_rol.html', id_usuario=id_usuario, roles=roles)

@miembro_bp.route('/activar_desactivar/<int:id_usuario>', methods=['POST'])
def activar_desactivar(id_usuario):
    MiembroProyecto.cambiar_estado(id_usuario)
    flash('Estado de usuario actualizado', 'success')
    return redirect(url_for('miembro.gestionar_usuarios'))

@miembro_bp.route('/asignar_proyecto/<int:id_usuario>', methods=['GET', 'POST'])
def asignar_proyecto(id_usuario):
    if request.method == 'POST':
        id_proyecto = request.form['proyecto']
        id_rol = request.form['rol']  # Recoge el rol seleccionado

        # Asigna proyecto y rol al usuario
        MiembroProyecto.asignar_proyecto(id_usuario, id_proyecto, id_rol)
        flash('Proyecto y rol asignados con éxito', 'success')
        return redirect(url_for('miembro.gestionar_usuarios'))

    proyectos = MiembroProyecto.obtener_proyectos(id_usuario)  # Pasamos el id_usuario aquí
    roles = MiembroProyecto.obtener_roles()
    
    return render_template('Mantenimiento/asignar_proyecto.html', id_usuario=id_usuario, proyectos=proyectos, roles=roles)