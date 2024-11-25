# app/models/proyecto.py
from app.extensions import mysql

class Proyecto:
    def __init__(self, id_proyecto, nombre, fechainicio, fechafin, descripcion, estado):
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.fechainicio = fechainicio
        self.fechafin = fechafin
        self.descripcion = descripcion
        self.estado = estado

    @classmethod
    def obtener_proyectos_usuario(cls, id_usuario):
        """Obtiene los proyectos en los que un usuario es miembro."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.id_proyecto, p.nombre, p.fechainicio, p.fechafin, p.descripcion, p.estado
            FROM Proyecto p
            JOIN Miembro_Proyecto mp ON p.id_proyecto = mp.id_proyecto
            WHERE mp.id_usuario = %s
        """, (id_usuario,))
        proyectos_data = cur.fetchall()
        cur.close()
        return [cls(*proyecto) for proyecto in proyectos_data]

    @classmethod
    def crear_proyecto(cls, nombre, descripcion, fechainicio, fechafin, estado, id_usuario):
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Proyecto (nombre, descripcion, fechainicio, fechafin, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, descripcion, fechainicio, fechafin, estado))
        mysql.connection.commit()
        id_proyecto = cur.lastrowid

        cur.execute("""
            INSERT INTO Miembro_Proyecto (id_usuario, id_proyecto, id_rol)
            VALUES (%s, %s, %s)
        """, (id_usuario, id_proyecto, 1))  # Asignamos el rol 'Líder de Proyecto'
        mysql.connection.commit()
        cur.close()
        return id_proyecto

    @classmethod
    def editar_proyecto(cls, id_proyecto, nombre, descripcion, fechainicio, fechafin, estado):
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE Proyecto
            SET nombre = %s, descripcion = %s, fechainicio = %s, fechafin = %s, estado = %s
            WHERE id_proyecto = %s
        """, (nombre, descripcion, fechainicio, fechafin, estado, id_proyecto))
        mysql.connection.commit()
        cur.close()

    @classmethod
    def cambiar_estado(cls, id_proyecto):
        cur = mysql.connection.cursor()
        cur.execute("SELECT estado FROM Proyecto WHERE id_proyecto = %s", (id_proyecto,))
        estado_actual = cur.fetchone()[0]
        nuevo_estado = 'Inactivo' if estado_actual == 'Activo' else 'Activo'
        cur.execute("""
            UPDATE Proyecto
            SET estado = %s
            WHERE id_proyecto = %s
        """, (nuevo_estado, id_proyecto))
        mysql.connection.commit()
        cur.close()
        return nuevo_estado
    @classmethod
    def obtener_tareas_proyecto(cls, id_proyecto):
        """Obtiene las tareas asociadas a un proyecto específico."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT nombre, descripcion, fecha_inicio, fecha_fin, estado
            FROM Tarea
            WHERE id_proyecto = %s
        """, (id_proyecto,))
        
        tareas_data = cur.fetchall()
        cur.close()

        tareas = []
        for tarea in tareas_data:
            tarea_dict = {
                'nombre': tarea[0],
                'descripcion': tarea[1],
                'fecha_inicio': tarea[2],
                'fecha_fin': tarea[3],
                'estado': tarea[4]
            }
            
            # Asegurar que el estado esté en minúsculas antes de comparar
            color = ''
            estado = tarea_dict['estado'].lower()  # Convertimos el estado a minúsculas para evitar problemas de comparación
            if estado == 'pendiente':
                color = '#ffcc00'  # Amarillo
            elif estado == 'en progreso':
                color = '#007bff'  # Azul
            elif estado == 'completado':
                color = '#28a745'  # Verde

            tareas.append({
                'nombre': tarea_dict['nombre'],
                'descripcion': tarea_dict['descripcion'],
                'fecha_inicio': tarea_dict['fecha_inicio'],
                'fecha_fin': tarea_dict['fecha_fin'],
                'color': color
            })
        
        return tareas