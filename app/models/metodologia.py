# app/models/metodologia.py

from app.extensions import mysql
from flask import session

class Metodologia:
    @staticmethod
    def obtener_todas_metodologias():
        """Obtener todas las metodologías de la base de datos"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_metodologia, nombre FROM Metodologia")
        metodologias = cur.fetchall()
        cur.close()
        return metodologias

    @staticmethod
    def obtener_proyectos_con_metodologia(user_id):
        """Obtener todos los proyectos con su metodología para un usuario específico"""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.id_proyecto, p.nombre, p.fechainicio, p.fechafin, p.descripcion, p.estado, 
                m.nombre AS metodologia_nombre
            FROM Proyecto p
            LEFT JOIN Metodologia m ON p.id_metodologia = m.id_metodologia
            JOIN Miembro_Proyecto mp ON p.id_proyecto = mp.id_proyecto
            WHERE mp.id_usuario = %s
        """, (user_id,))  # Filtrar por el usuario a través de Miembro_Proyecto

        # Convertir la consulta a formato de diccionario
        proyectos = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]  # Obtener los nombres de las columnas
        proyectos_dict = [dict(zip(columnas, proyecto)) for proyecto in proyectos]  # Convertir cada fila en un diccionario

        cur.close()
        return proyectos_dict

    
    @staticmethod
    def actualizar_metodologia(id_metodologia, id_proyecto):
        """Actualizar la metodología de un proyecto"""
        cur = mysql.connection.cursor()
        cur.execute("UPDATE Proyecto SET id_metodologia = %s WHERE id_proyecto = %s", (id_metodologia, id_proyecto))
        mysql.connection.commit()
        cur.close()
    # Modelo - No se necesitan cambios
    @staticmethod
    def obtener_proyecto_por_id(id_proyecto):
        """Obtener un proyecto por su ID"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Proyecto WHERE id_proyecto = %s", (id_proyecto,))
        proyecto = cur.fetchone()  # Devuelve una tupla
        cur.close()
        return proyecto
