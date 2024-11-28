# app/controllers/tarea_controller.py
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, current_user
from app.models.tarea import Tarea  # Asegúrate de que importas el modelo Tarea
from app.models.historial_tarea import HistorialTarea  # Asegúrate de que importas el modelo Tarea
from app.extensions import mysql  # Importamos mysql desde extensions
from app.models.proyecto import Proyecto


# Crear el Blueprint para las tareas
tarea_bp = Blueprint('tarea', __name__)  # Renombrado el Blueprint correctamente

@tarea_bp.route('/proyecto/<int:id>/tareas', methods=['GET'])
@login_required
def ver_tareas(id):
    
    # Obtener las tareas del proyecto usando el modelo
    tareas = Tarea.obtener_tareas_por_proyecto(id)  # Ahora obtenemos las tareas como diccionarios
    print(tareas)  # Verificar las tareas que llegan al controller

    # Obtener los usuarios asignados al proyecto usando el modelo
    usuarios = Tarea.obtener_usuarios_asignados(id)  # Llamamos al modelo Tarea directamente

    # Pasar tareas y usuarios al template
    return render_template('proyectos/tareas.html', tareas=tareas, usuarios=usuarios, id_proyecto=id)

@tarea_bp.route('/flujo_tareas')
@login_required
def flujo_tareas():
    # Llama al método para obtener los proyectos del usuario actual
    proyectos = Proyecto.obtener_proyectos_usuario(current_user.id)
    
    # Lista para almacenar los proyectos y sus tareas
    proyectos_con_tareas = []
    
    for proyecto in proyectos:
        # Obtén las tareas para cada proyecto usando el id del proyecto
        tareas = Tarea.obtener_tareas_por_proyecto(proyecto.id_proyecto)
        
        # Convierte el objeto Proyecto a un diccionario serializable
        proyecto_dict = vars(proyecto)  # Convierte el proyecto a diccionario
        
        # Agrega el proyecto y sus tareas a la lista
        proyectos_con_tareas.append({
            'proyecto': proyecto_dict,
            'tareas': tareas
        })
        print(proyectos_con_tareas)
    
    # Renderiza el template pasando la información de proyectos y tareas
    return render_template('proyectos/flujo_tareas.html', proyectos_con_tareas=proyectos_con_tareas)

@tarea_bp.route('/proyecto/<int:id_proyecto>/tarea/<int:id_tarea>/historial', methods=['GET'])
@login_required
def ver_historial_tarea(id_proyecto, id_tarea):
    # Obtener el historial de la tarea a través del modelo
    historial = HistorialTarea.obtener_historial_por_tarea(id_tarea)

    # Pasar el historial al template junto con el id del proyecto
    return render_template('proyectos/historial_tarea.html', historial=historial, id_proyecto=id_proyecto)


@tarea_bp.route('/proyecto/<int:id>/tareas/crear', methods=['POST'])
@login_required
def crear_tarea(id):
    
    """Crea una nueva tarea en el proyecto."""
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    id_asignado_a = request.form['asignado_a']

    # Validación de campos
    if not nombre or not descripcion or not fecha_inicio or not fecha_fin or not id_asignado_a:
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('tarea.ver_tareas', id=id))

    # Llamar al método del modelo para crear la tarea
    Tarea.crear_tarea(nombre, descripcion, fecha_inicio, fecha_fin, id, id_asignado_a)

    flash('Tarea creada con éxito', 'success')
    return redirect(url_for('tarea.ver_tareas', id=id))


@tarea_bp.route('/notificaciones')
@login_required
def notificaciones():
    # Obtener tareas próximas a vencer
    tareas_proximas = Tarea.obtener_tareas_proximas()
    
    # Obtener tareas retrasadas
    tareas_retrasadas = Tarea.obtener_tareas_retrasadas()
    print("tareas_proximas",tareas_proximas)
    print("tareas_retrasadas",tareas_retrasadas)
    # Pasar las tareas al template
    return render_template('proyectos/notificaciones.html', 
                           tareas_proximas=tareas_proximas, 
                           tareas_retrasadas=tareas_retrasadas)

@tarea_bp.route('/proyecto/<int:id_proyecto>/tarea/<int:id_tarea>/actualizar', methods=['POST'])
@login_required
def actualizar_estado_tarea(id_proyecto, id_tarea):
    nuevo_estado = request.form['estado']

    # Obtener el estado anterior desde el modelo
    estado_anterior = Tarea.obtener_estado(id_tarea, mysql)
    
    # Si no se encontró el estado anterior, mostrar un error
    if estado_anterior is None:
        flash('No se pudo encontrar el estado de la tarea.', 'error')
        return redirect(url_for('ver_flujo_tareas', id_proyecto=id_proyecto))

    # Actualizar el estado de la tarea en la base de datos
    Tarea.actualizar_estado(id_tarea, nuevo_estado, mysql)
    
    
    # Registrar el cambio de estado en el historial
    HistorialTarea.insertar_historial(id_tarea, estado_anterior, nuevo_estado, current_user.id)
    print(session.get('idusuario'))
    # Mensaje de éxito
    flash('El estado de la tarea ha sido actualizado y registrado en el historial.', 'success')

    return redirect(url_for('tarea.flujo_tareas', id_usuario=session.get('idusuario')))
