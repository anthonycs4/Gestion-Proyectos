# app/controllers/informe_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import mysql
from fpdf import FPDF
from datetime import datetime

# Crear el blueprint para el InformeController
Informe = Blueprint('Informe', __name__)

# Ruta para ver los informes de un proyecto
@Informe.route('/proyecto/<int:id>/informes', methods=['GET'])
@login_required
def ver_informes(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.id_informe, p.nombre, i.periodo, i.fecha_generacion
        FROM Informe_Estado i
        JOIN Proyecto p ON i.id_proyecto = p.id_proyecto
        WHERE p.id_proyecto = %s
    """, (id,))
    informes = cur.fetchall()
    cur.close()

    return render_template('informes.html', informes=informes, id_proyecto=id)

# Ruta para gestionar informes (ver y generar)
@Informe.route('/proyectos', methods=['GET', 'POST'])
@login_required
def gestionar_informes():
    cur = mysql.connection.cursor()
    
    # Obtener los proyectos disponibles
    cur.execute("SELECT id_proyecto, nombre FROM Proyecto")
    proyectos = cur.fetchall()

    if request.method == 'POST':
        id_proyecto = request.form['proyecto']
        periodo = request.form['periodo']

        if not id_proyecto or not periodo:
            flash('Debe seleccionar un proyecto y un periodo.', 'danger')
            return redirect(url_for('Informe.gestionar_informes'))

        avance_general = "El proyecto tiene un avance del 70%."
        problemas = "Se identificaron algunos retrasos en las entregas del módulo 3."

        # Guardar el informe en la base de datos
        cur.execute("""
            INSERT INTO Informe_Estado (id_proyecto, periodo, fecha_generacion, avance_general, problemas)
            VALUES (%s, %s, NOW(), %s, %s)
        """, (id_proyecto, periodo, avance_general, problemas))
        mysql.connection.commit()

        flash('Informe generado con éxito', 'success')
        return redirect(url_for('Informe.gestionar_informes'))
    
    # Obtener los informes
    cur.execute("""
        SELECT i.id_informe, p.nombre, i.periodo, i.fecha_generacion
        FROM Informe_Estado i
        JOIN Proyecto p ON i.id_proyecto = p.id_proyecto
    """)
    informes = cur.fetchall()
    cur.close()

    return render_template('proyectos/informes.html', proyectos=proyectos, informes=informes)

# Ruta para ver un informe específico
@Informe.route('/proyecto/informe/<int:id_informe>', methods=['GET'])
@login_required
def ver_informe(id_informe):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT i.avance_general, i.problemas, p.nombre, i.periodo, i.fecha_generacion
        FROM Informe_Estado i
        JOIN Proyecto p ON i.id_proyecto = p.id_proyecto
        WHERE i.id_informe = %s
    """, (id_informe,))
    informe = cur.fetchone()
    cur.close()

    return render_template('proyectos/ver_informe.html', informe=informe)

# Ruta para exportar el informe a PDF
@Informe.route('/proyecto/informe/<int:id_informe>/exportar', methods=['GET'])
@login_required
def exportar_informe_pdf(id_informe):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT i.avance_general, i.problemas, p.nombre, i.periodo, i.fecha_generacion
        FROM Informe_Estado i
        JOIN Proyecto p ON i.id_proyecto = p.id_proyecto
        WHERE i.id_informe = %s
    """, (id_informe,))
    informe = cur.fetchone()
    cur.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, f"Informe de Estado - {informe[2]}", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, f"Periodo: {informe[3]}", ln=True)
    pdf.cell(200, 10, f"Fecha de Generación: {informe[4]}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Avance General:", ln=True)
    pdf.multi_cell(200, 10, informe[0])
    pdf.ln(10)
    pdf.cell(200, 10, "Problemas Identificados:", ln=True)
    pdf.multi_cell(200, 10, informe[1])

    response = make_response(pdf.output(dest='S'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=informe_{id_informe}.pdf'

    return response


@Informe.route('/proyecto/reportes', methods=['GET', 'POST'])
@login_required
def gestionar_reportes():
    cur = mysql.connection.cursor()
    
    # Obtener los proyectos donde el usuario está asignado
    cur.execute("""
        SELECT p.id_proyecto, p.nombre 
        FROM Proyecto p
        JOIN Miembro_Proyecto mp ON p.id_proyecto = mp.id_proyecto
        WHERE mp.id_usuario = %s
    """, (current_user.id,))
    proyectos = cur.fetchall()

    if request.method == 'POST':
        id_proyecto = request.form['proyecto']
        periodo = request.form['periodo']

        if not id_proyecto or not periodo:
            flash('Debe seleccionar un proyecto y un periodo.', 'danger')
            return redirect(url_for('Informe.gestionar_reportes'))

        # Generar el informe (ejemplo de datos)
        avance_general = "El proyecto tiene un avance del 70%."
        problemas = "Se identificaron algunos retrasos en las entregas del módulo 3."

        # Guardar el informe en la base de datos
        cur.execute("""
            INSERT INTO Informe_Estado (id_proyecto, periodo, fecha_generacion, avance_general, problemas)
            VALUES (%s, %s, NOW(), %s, %s)
        """, (id_proyecto, periodo, avance_general, problemas))
        mysql.connection.commit()

        flash('Informe generado con éxito', 'success')
        return redirect(url_for('Informe.gestionar_reportes'))

    # Obtener los informes generados relacionados con los proyectos donde el usuario está asignado
    cur.execute("""
        SELECT i.id_informe, p.nombre, i.periodo, i.fecha_generacion 
        FROM Informe_Estado i
        JOIN Proyecto p ON i.id_proyecto = p.id_proyecto
        JOIN Miembro_Proyecto mp ON p.id_proyecto = mp.id_proyecto
        WHERE mp.id_usuario = %s
    """, (current_user.id,))
    
    informes = cur.fetchall()
    cur.close()

    return render_template('proyectos/reportes.html', proyectos=proyectos, informes=informes)

@Informe.route('/proyecto/reporte/<int:id_reporte>', methods=['GET'])
@login_required
def ver_reporte(id_reporte):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT p.nombre, r.periodo, r.avance, r.actividades_completadas, r.problemas, r.fecha_generacion
        FROM Reporte_Progreso r
        JOIN Proyecto p ON r.id_proyecto = p.id_proyecto
        WHERE r.id_reporte = %s
    """, (id_reporte,))
    reporte = cur.fetchone()
    cur.close()

    return render_template('ver_reporte.html', reporte=reporte)

@Informe.route('/proyecto/reporte/<int:id_reporte>/exportar', methods=['GET'])
@login_required
def exportar_reporte_pdf(id_reporte):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT p.nombre, r.periodo, r.avance, r.actividades_completadas, r.problemas, r.fecha_generacion
        FROM Reporte_Progreso r
        JOIN Proyecto p ON r.id_proyecto = p.id_proyecto
        WHERE r.id_reporte = %s
    """, (id_reporte,))
    reporte = cur.fetchone()
    cur.close()

    # Generar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, f"Informe de Progreso - {reporte[0]}", ln=True, align='C')

    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, f"Periodo: {reporte[1]}", ln=True)
    pdf.cell(200, 10, f"Fecha de Generación: {reporte[5]}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Porcentaje de Avance:", ln=True)
    pdf.cell(200, 10, f"{reporte[2]}%", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Actividades Completadas:", ln=True)
    pdf.multi_cell(200, 10, reporte[3])

    pdf.ln(10)
    pdf.cell(200, 10, "Problemas Identificados:", ln=True)
    pdf.multi_cell(200, 10, reporte[4])

    response = make_response(pdf.output(dest='S'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_{id_reporte}.pdf'
    
    return response

@Informe.route('/informes/generar', methods=['POST'])
@login_required
def generar_informe():
    proyecto_id = request.form['proyecto']
    periodo = request.form['periodo']

    if not proyecto_id:
        flash('Debe seleccionar un proyecto', 'danger')
        return redirect(url_for('Informe.gestionar_reportes'))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO Informe_Estado (id_proyecto, periodo, fecha_generacion, avance_general, problemas)
        VALUES (%s, %s, NOW(), 'Avance del proyecto', 'Problemas detectados')
    """, (proyecto_id, periodo))
    mysql.connection.commit()
    cur.close()

    flash('Informe generado con éxito', 'success')
    return redirect(url_for('Informe.gestionar_reportes'))