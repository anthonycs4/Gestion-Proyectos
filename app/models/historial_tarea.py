from app.extensions import mysql

class HistorialTarea:
    def __init__(self, fecha, estado_anterior, estado_nuevo, nombre_responsable):
        self.fecha = fecha
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo
        self.nombre_responsable = nombre_responsable

    @classmethod
    def obtener_historial_por_tarea(cls, id_tarea):
        """Obtiene el historial de estado de una tarea."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ht.fecha, ht.estado_anterior, ht.estado_nuevo, u.nombre
            FROM Historial_Tareas ht
            JOIN Usuario u ON ht.id_usuario = u.id_usuario
            WHERE ht.id_tarea = %s
            ORDER BY ht.fecha DESC
        """, (id_tarea,))
        historial_data = cur.fetchall()
        cur.close()

        # Crear una lista de objetos HistorialTarea con la información obtenida
        historial = [cls(*registro) for registro in historial_data]
        return historial
    
    @staticmethod
    def insertar_historial(id_tarea, estado_anterior, estado_nuevo, id_usuario):
        """Inserta un nuevo historial de cambio de estado de tarea."""
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Historial_Tareas (id_tarea, estado_anterior, estado_nuevo, id_usuario)
            VALUES (%s, %s, %s, %s)
        """, (id_tarea, estado_anterior, estado_nuevo, id_usuario))
        mysql.connection.commit()
        cur.close()
