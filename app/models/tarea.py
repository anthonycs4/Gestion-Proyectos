# app/models/tarea.py
from app.extensions import mysql
from datetime import date, timedelta

class Tarea:
    def __init__(self, id_tarea, nombre, descripcion, fecha_inicio, fecha_fin, estado, id_proyecto, id_asignado_a, nombre_asignado):
        self.id_tarea = id_tarea
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.id_proyecto = id_proyecto
        self.id_asignado_a = id_asignado_a
        self.nombre_asignado = nombre_asignado  # Almacenar el nombre del usuario asignado

    def __repr__(self):
        return f"<Tarea {self.nombre} - Asignado a {self.nombre_asignado}>"


    @classmethod
    def obtener_tareas_por_proyecto(cls, id_proyecto):
        """Obtiene todas las tareas de un proyecto y las convierte a diccionarios."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_tarea, id_proyecto, nombre, descripcion, estado, fecha_inicio, fecha_fin, id_asignado_a
            FROM Tarea
            WHERE id_proyecto = %s
        """, (id_proyecto,))
        tareas_data = cur.fetchall()
        cur.close()

        # Convertir cada tarea a un diccionario para mayor facilidad en el uso
        tareas = []
        for tarea in tareas_data:
            tarea_dict = {
                'id_tarea': tarea[0],
                'id_proyecto': tarea[1],
                'nombre': tarea[2],
                'descripcion': tarea[3],
                'estado': tarea[4],
                'fecha_inicio': tarea[5],
                'fecha_fin': tarea[6],
                'id_asignado_a': tarea[7]
            }
            tareas.append(tarea_dict)
        
        print("asignado a",tareas)  # Verificar la salida
        return tareas
    @classmethod
    def obtener_usuarios_asignados(cls, id_proyecto):
        """ Obtiene todos los usuarios asignados a un proyecto especÃ­fico. """
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT Usuario.id_usuario, Usuario.nombre, Usuario.apellido
            FROM Usuario
            JOIN Miembro_Proyecto ON Usuario.id_usuario = Miembro_Proyecto.id_usuario
            WHERE Miembro_Proyecto.id_proyecto = %s
        """, (id_proyecto,))
        usuarios_data = cur.fetchall()
        cur.close()
        return usuarios_data
    @classmethod
    def crear_tarea(cls, nombre, descripcion, fecha_inicio, fecha_fin, id_proyecto, id_asignado_a):
        """Crea una nueva tarea en la base de datos."""
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Tarea (nombre, descripcion, fecha_inicio, fecha_fin, id_proyecto, id_asignado_a)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, fecha_inicio, fecha_fin, id_proyecto, id_asignado_a))
        mysql.connection.commit()
        cur.close()
    @classmethod
    def obtener_tareas_proximas(cls):
    
        cur = mysql.connection.cursor()
        
        hoy = date.today()
        proximas_tareas = hoy + timedelta(days=3)

        cur.execute("""
            SELECT t.id_tarea, t.nombre, t.descripcion, t.fecha_inicio, t.fecha_fin, t.estado, 
                t.id_proyecto, t.id_asignado_a, u.nombre AS nombre_asignado
            FROM Tarea t
            JOIN Usuario u ON t.id_asignado_a = u.id_usuario
            WHERE t.fecha_fin BETWEEN %s AND %s
            AND t.estado = 'Pendiente'
        """, (hoy, proximas_tareas))
        
        tareas_proximas = cur.fetchall()
        cur.close()

        print("tareas proximas:", tareas_proximas)
        # Convertir tuplas en objetos Tarea, ahora incluyendo el nombre del usuario asignado
        return [cls(*tarea[:8], tarea[8]) for tarea in tareas_proximas]  # tarea[8] es el nombre del usuario

    @classmethod
    def obtener_tareas_retrasadas(cls):
        """Obtiene las tareas cuya fecha de vencimiento ya pasÃ³ y siguen pendientes"""
        cur = mysql.connection.cursor()
        
        hoy = date.today()

        cur.execute("""
            SELECT t.id_tarea, t.nombre, t.descripcion, t.fecha_inicio, t.fecha_fin, t.estado, 
                t.id_proyecto, t.id_asignado_a, u.nombre AS nombre_asignado
            FROM Tarea t
            JOIN Usuario u ON t.id_asignado_a = u.id_usuario
            WHERE t.fecha_fin < %s
            AND t.estado = 'Pendiente'
        """, (hoy,))
        
        tareas_retrasadas = cur.fetchall()
        cur.close()

        print("tareas retrasadas:", tareas_retrasadas)
        # Convertir tuplas en objetos Tarea, ahora incluyendo el nombre del usuario asignado
        return [cls(*tarea[:8], tarea[8]) for tarea in tareas_retrasadas]  # tarea[8] es el nombre del usuario


    @classmethod
    def obtener_tareas_proyecto(cls, id_proyecto):
        """Obtiene las tareas de un proyecto."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.id_tarea, t.nombre, t.descripcion, t.fecha_inicio, t.fecha_fin, t.estado
            FROM Tarea t
            WHERE t.id_proyecto = %s
        """, (id_proyecto,))
        tareas_data = cur.fetchall()
        cur.close()
        
        # Crear un color para cada estado de tarea
        color_map = {
            'Pendiente': '#FF0000',  # Rojo para pendiente
            'En Progreso': '#FFA500',  # Naranja para en progreso
            'Completado': '#008000'  # Verde para completado
        }
        
        # Asignar color a cada tarea
        tareas = []
        for tarea in tareas_data:
            tarea_dict = {
                'id_tarea': tarea[0],
                'nombre': tarea[1],
                'descripcion': tarea[2],
                'fecha_inicio': tarea[3],
                'fecha_fin': tarea[4],
                'estado': tarea[5],
                'color': color_map.get(tarea[5], '#000000')  # Color por defecto negro
            }
            tareas.append(tarea_dict)
        
        return tareas
   



    
    

    @staticmethod
    def obtener_estado(id_tarea, mysql):
        cur = mysql.connection.cursor()
        cur.execute("SELECT estado FROM Tarea WHERE id_tarea = %s", (id_tarea,))
        estado = cur.fetchone()
        cur.close()
        return estado[0] if estado else None

    @staticmethod
    def actualizar_estado(id_tarea, nuevo_estado, mysql):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE Tarea SET estado = %s WHERE id_tarea = %s", (nuevo_estado, id_tarea))
        mysql.connection.commit()
        cur.close()