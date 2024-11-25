from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import mysql  # Importamos mysql desde extensions
from app.models.metodologia import Metodologia


# Crear el blueprint
metodologia = Blueprint('metodologia', __name__)

@metodologia.route('/configurar_metodologia', methods=['GET'])
@login_required
def ver_proyectos():
    # Obtener todos los proyectos con su metodología usando el modelo
    proyectos = Metodologia.obtener_proyectos_con_metodologia()
    
    # Obtener todas las metodologías disponibles usando el modelo
    metodologias = Metodologia.obtener_todas_metodologias()

    return render_template('Mantenimiento/configurar_metodologia_lista.html', proyecto=proyectos, metodologias=metodologias)


@metodologia.route('/configurar_metodologia/<int:id>', methods=['GET', 'POST'])
@login_required
def configurar_metodologia(id):
    # Obtener el proyecto correspondiente al id
    proyecto = Metodologia.obtener_proyecto_por_id(id)  # Regresa una tupla

    # Obtener la lista de metodologías disponibles
    metodologias = Metodologia.obtener_todas_metodologias()  # Lista de tuplas

    if request.method == 'POST':
        id_metodologia = request.form['metodologia']

        # Actualizar la metodología asociada al proyecto
        Metodologia.actualizar_metodologia(id_metodologia, id)

        flash('Metodología configurada con éxito', 'success')
        return redirect(url_for('metodologia.ver_proyectos'))  # Redirige al listado de proyectos

    # Pasar el proyecto y las metodologías a la plantilla
    return render_template(
        'Mantenimiento/configurar_metodologia.html', 
        proyecto=proyecto, 
        metodologias=metodologias
    )
