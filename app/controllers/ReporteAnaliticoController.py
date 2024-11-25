# app/controllers/reporte_analitico_controller.py

from flask import Blueprint, render_template, make_response, request, flash
from flask_login import login_required, current_user
from app import mysql
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# Crear el blueprint
reporte_analitico_controller = Blueprint('reporte_analitico_controller', __name__)

@reporte_analitico_controller.route('/proyecto/<int:id_proyecto>/reporte_analiticas', methods=['GET'])
@login_required
def reporte_analiticas(id_proyecto):
    cur = mysql.connection.cursor()

    # Obtener el historial de tareas para el proyecto
    cur.execute("""
        SELECT t.nombre, h.estado_anterior, h.estado_nuevo, h.fecha, u.nombre
        FROM Historial_Tareas h
        JOIN Tarea t ON h.id_tarea = t.id_tarea
        JOIN Usuario u ON h.id_usuario = u.id_usuario
        WHERE t.id_proyecto = %s
        ORDER BY h.fecha
    """, (id_proyecto,))
    transiciones = cur.fetchall()
    cur.close()

    # Generar conteo de transiciones
    estados = ["Pendiente", "En progreso", "Completada"]
    conteo_transiciones = {estado: 0 for estado in estados}

    for transicion in transiciones:
        if transicion[2] in conteo_transiciones:
            conteo_transiciones[transicion[2]] += 1

    # Crear gráfico de barras
    plt.bar(conteo_transiciones.keys(), conteo_transiciones.values())
    plt.xlabel('Estados')
    plt.ylabel('Cantidad de Transiciones')
    plt.title('Transiciones de Estado de las Tareas')

    # Convertir gráfico a imagen para incrustar en HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('reporte_analiticas.html', img_url=img_url, transiciones=transiciones, id_proyecto=id_proyecto)

@reporte_analitico_controller.route('/proyecto/<int:id_proyecto>/reporte_analiticas/pdf', methods=['GET'])
@login_required
def exportar_reporteanaliticas_pdf(id_proyecto):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT t.nombre, h.estado_anterior, h.estado_nuevo, h.fecha, u.nombre
        FROM Historial_Tareas h
        JOIN Tarea t ON h.id_tarea = t.id_tarea
        JOIN Usuario u ON h.id_usuario = u.id_usuario
        WHERE t.id_proyecto = %s
        ORDER BY h.fecha
    """, (id_proyecto,))
    transiciones = cur.fetchall()
    cur.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Reporte de Analíticas - Proyecto {id_proyecto}", ln=True, align="C")

    for transicion in transiciones:
        pdf.cell(200, 10, txt="Tarea: {}, Estado Anterior: {}, Estado Nuevo: {}, Fecha: {}, Responsable: {}".format(
            transicion[0], transicion[1], transicion[2], transicion[3], transicion[4]), ln=True)

    response = make_response(pdf.output(dest='S'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_analiticas_{id_proyecto}.pdf'
    
    return response

@reporte_analitico_controller.route('/proyecto/<int:id_proyecto>/reporte_analiticas/excel', methods=['GET'])
@login_required
def exportar_reporte_excel(id_proyecto):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT t.nombre, h.estado_anterior, h.estado_nuevo, h.fecha, u.nombre
        FROM Historial_Tareas h
        JOIN Tarea t ON h.id_tarea = t.id_tarea
        JOIN Usuario u ON h.id_usuario = u.id_usuario
        WHERE t.id_proyecto = %s
        ORDER BY h.fecha
    """, (id_proyecto,))
    transiciones = cur.fetchall()
    cur.close()

    df = pd.DataFrame(transiciones, columns=["Nombre de la Tarea", "Estado Anterior", "Estado Nuevo", "Fecha de Transición", "Responsable"])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte de Analiticas')
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_analiticas_{id_proyecto}.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response
