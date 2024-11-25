# app/models/rol.py

from app.extensions import mysql

class Rol:
    @staticmethod
    def obtener_todos():
        """Obtener todos los roles de la base de datos"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_rol, nombre FROM Rol")
        roles = cur.fetchall()
        cur.close()
        return roles
