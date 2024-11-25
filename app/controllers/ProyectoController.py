from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, current_user
from app.extensions import mysql  # Importamos mysql desde extensions
from app.models.proyecto import Proyecto  # Importa el modelo Proyecto
from app.models.tarea import Tarea  # Importa el modelo Proyecto



# Crear el blueprint para proyectos
proyecto_bp = Blueprint('proyecto', __name__)

@proyecto_bp.route('/dashboard')
@login_required
def dashboard():
    # Llama a la función del modelo para obtener proyectos del usuario actual
    proyectos = Proyecto.obtener_proyectos_usuario(current_user.id)
    
    # Acceder al rol desde la sesión
    rol = session.get('role')

    return render_template('proyectos/proyectos.html', proyectos=proyectos, rol=rol)



@proyecto_bp.route('/crear_proyecto', methods=['GET', 'POST'])
@login_required
def crear_proyecto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        fechainicio = request.form['fechainicio']
        fechafin = request.form['fechafin']
        estado = request.form['estado']

        if not nombre or not descripcion or not fechainicio or not fechafin:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('proyecto.crear_proyecto'))

        # Obtener el ID del usuario logueado
        id_usuario = current_user.id
        
        cur = mysql.connection.cursor()
        # Insertar el proyecto en la tabla Proyecto
        cur.execute("""
            INSERT INTO Proyecto (nombre, descripcion, fechainicio, fechafin, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, descripcion, fechainicio, fechafin, estado))
        mysql.connection.commit()

        # Obtener el ID del proyecto recién insertado
        id_proyecto = cur.lastrowid

        # Insertar en la tabla Miembro_Proyecto para asociar al usuario logueado con el proyecto
        cur.execute("""
            INSERT INTO Miembro_Proyecto (id_usuario, id_proyecto, id_rol)
            VALUES (%s, %s, %s)
        """, (id_usuario, id_proyecto, 1))  # Asignamos el rol de 'Líder de Proyecto' como ejemplo
        mysql.connection.commit()
        cur.close()

        flash('Proyecto creado con éxito', 'success')
        # Redirige al dashboard para mostrar la lista de proyectos actualizada
        return redirect(url_for('proyecto.dashboard'))

    return render_template('proyectos/crear_proyecto.html')



@proyecto_bp.route('/editar_proyecto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_proyecto(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Proyecto WHERE id_proyecto = %s", (id,))
    proyecto = cur.fetchone()
    cur.close()

    # Ajustar los índices de acuerdo con los datos correctos
    nombre = proyecto[2]
    descripcion = proyecto[3]
    fechainicio = proyecto[4]
    fechafin = proyecto[5]
    estado = proyecto[7]

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        fechainicio = request.form['fechainicio']
        fechafin = request.form['fechafin']
        estado = request.form['estado']
        
        if not nombre or not descripcion or not fechainicio or not fechafin:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('proyecto_controller.editar_proyecto', id=id))
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE Proyecto
            SET nombre = %s, descripcion = %s, fechainicio = %s, fechafin = %s, estado = %s
            WHERE id_proyecto = %s
        """, (nombre, descripcion, fechainicio, fechafin, estado, id))
        mysql.connection.commit()
        cur.close()

        flash('Proyecto editado con éxito', 'success')
        return redirect(url_for('proyecto.dashboard'))

    return render_template('proyectos/editar_proyecto.html', proyecto=proyecto, fechainicio=fechainicio, fechafin=fechafin)


@proyecto_bp.route('/deshabilitar_proyecto/<int:id>', methods=['GET'])
@login_required
def deshabilitar_proyecto(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT estado FROM Proyecto WHERE id_proyecto = %s", (id,))
    proyecto = cur.fetchone()
    
    nuevo_estado = 'Inactivo' if proyecto[0] == 'Activo' else 'Activo'
    
    cur.execute("""
        UPDATE Proyecto
        SET estado = %s
        WHERE id_proyecto = %s
    """, (nuevo_estado, id))
    mysql.connection.commit()
    cur.close()

    flash(f'Proyecto {"deshabilitado" if nuevo_estado == "Inactivo" else "habilitado"} con éxito', 'success')
    return redirect(url_for('dashboard'))
from datetime import datetime

@proyecto_bp.route('/cronograma')
@login_required
def cronograma():
    # Llama al método para obtener los proyectos del usuario actual
    proyectos = Proyecto.obtener_proyectos_usuario(current_user.id)
    
    # Lista para almacenar los proyectos y sus tareas
    proyectos_con_tareas = []
    
    for proyecto in proyectos:
        # Obtén las tareas para cada proyecto usando el id del proyecto
        tareas = Proyecto.obtener_tareas_proyecto(proyecto.id_proyecto)
        
        # Convierte el objeto Proyecto a un diccionario serializable
        proyecto_dict = vars(proyecto)  # Convierte el proyecto a diccionario
        
        # Convierte las fechas de inicio y fin del proyecto a formato 'YYYY-MM-DD'
        proyecto_dict['fechainicio'] = proyecto_dict['fechainicio'].strftime('%Y-%m-%d')
        proyecto_dict['fechafin'] = proyecto_dict['fechafin'].strftime('%Y-%m-%d')
        
        # Convierte las fechas de inicio y fin de las tareas a formato 'YYYY-MM-DD'
        for tarea in tareas:
            tarea['fecha_inicio'] = tarea['fecha_inicio'].strftime('%Y-%m-%d')
            tarea['fecha_fin'] = tarea['fecha_fin'].strftime('%Y-%m-%d')
        
        # Agrega el proyecto y sus tareas a la lista
        proyectos_con_tareas.append({
            'proyecto': proyecto_dict,
            'tareas': tareas
        })
        print(proyectos_con_tareas)  # Para ver la estructura final de los datos
    
    # Renderiza el template del cronograma pasando la información de proyectos y tareas
    return render_template('proyectos/cronograma.html', proyectos_con_tareas=proyectos_con_tareas)
@proyecto_bp.route('/flujo_tareas')
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
